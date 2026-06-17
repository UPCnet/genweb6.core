# -*- coding: utf-8 -*-
"""
Tareas asíncronas para procesamiento en background usando collective.taskqueue2.

Este módulo contiene las tareas que se ejecutan de forma asíncrona usando el
sistema de colas de Huey. Si ``collective.taskqueue2`` no está disponible, las
tareas se ejecutan de forma síncrona (fallback transparente).
"""
from contextlib import contextmanager

import logging
import os

logger = logging.getLogger(__name__)
# El consumer de Huey fija el root logger en WARNING (verbose=False), lo que
# ocultaría nuestros logs INFO en el worker. Forzamos INFO en este logger para
# que la traza de la exportación sea visible también en el consumer.
logger.setLevel(logging.INFO)
# En desarrollo, Products.PrintingMailHost imprime el correo con un LOG.info
# sobre el logger 'PrintingMailHost', que hereda el nivel del root (WARNING en
# el worker de Huey) y quedaría oculto. Forzamos INFO para ver el correo en el
# terminal igual que en una petición web. En producción este logger no se usa.
logging.getLogger('PrintingMailHost').setLevel(logging.INFO)

# Intentar importar collective.taskqueue2.
# Si no está disponible, las tareas se ejecutarán de forma síncrona.
try:
    from collective.taskqueue2.huey_config import huey_taskqueue
    TASKQUEUE_AVAILABLE = True
    logger.info(
        "collective.taskqueue2 disponible - Modo asíncrono habilitado"
    )
except ImportError:
    TASKQUEUE_AVAILABLE = False
    logger.warning(
        "collective.taskqueue2 NO disponible - "
        "Las tareas se ejecutarán de forma síncrona"
    )

    # Definir un decorador dummy para compatibilidad.
    class DummyTaskQueue:
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    huey_taskqueue = DummyTaskQueue()


def register_huey_tasks(event):
    """Registra las tareas Huey de este paquete al arrancar el proceso Zope.

    El consumer de ``collective.taskqueue2`` solo importa sus propias tareas
    (``huey_tasks``). Sin este handler, el worker no conoce
    ``export_download_files_async`` y falla al deserializar la cola.
    """
    if TASKQUEUE_AVAILABLE:
        logger.info(
            "Tareas Huey de genweb6.core registradas en el TaskRegistry"
        )


@contextmanager
def _adopt_export_user(site, user_id):
    """Ejecuta el bloque como ``user_id`` (o como Manager si no se conoce).

    En el worker de Huey no hay petición ni usuario autenticado, por lo que las
    comprobaciones de permisos de creación fallarían. Adoptamos el usuario que
    lanzó la exportación; si no se encuentra, caemos a roles de Manager.
    """
    from AccessControl.SecurityManagement import getSecurityManager
    from AccessControl.SecurityManagement import setSecurityManager
    from AccessControl.SecurityManagement import newSecurityManager

    old_manager = getSecurityManager()
    user = None
    if user_id:
        acl_users = getattr(site, 'acl_users', None)
        if acl_users is not None:
            user = acl_users.getUserById(user_id)
            if user is not None:
                user = user.__of__(acl_users)
    try:
        if user is not None:
            newSecurityManager(None, user)
        else:
            # Fallback: roles de Manager sobre el usuario actual.
            from plone import api
            with api.env.adopt_roles(['Manager']):
                yield
            return
        yield
    finally:
        setSecurityManager(old_manager)


def is_async_download_enabled():
    """
    Verifica si la exportación asíncrona de ficheros está habilitada.

    Se activa con la variable de entorno ``GENWEB_ASYNC_DOWNLOAD_FILES=1`` y
    requiere que ``collective.taskqueue2`` esté disponible.
    """
    async_env = os.environ.get('GENWEB_ASYNC_DOWNLOAD_FILES', '0') == '1'
    return async_env and TASKQUEUE_AVAILABLE


def _get_ldap_email(site, user_id):
    """Obtiene el email del usuario consultando los plugins LDAP.

    Recorre los plugins LDAP conocidos del sitio (``ldapUPC``, ``ldapexterns``)
    y devuelve el primer email encontrado. Devuelve ``None`` si el usuario no
    existe en LDAP o no tiene email; en ese caso no se enviará notificación.
    """
    if not user_id:
        return None
    acl_users = getattr(site, 'acl_users', None)
    if acl_users is None:
        return None

    for plugin_id in ('ldapUPC', 'ldapexterns'):
        plugin = getattr(acl_users, plugin_id, None)
        if plugin is None:
            continue
        try:
            ldap_folder = getattr(plugin, 'acl_users', None)
            if ldap_folder is None:
                continue
            ldap_user = ldap_folder.getUserById(user_id)
            if ldap_user is None:
                continue
            email = (ldap_user.getProperty('email', None)
                     or ldap_user.getProperty('mail', None))
            if email:
                logger.info(
                    "[ASYNC EXPORT MAIL] Email LDAP de {0} ({1}): {2}".format(
                        user_id, plugin_id, email))
                return email
        except Exception as e:
            logger.warning(
                "[ASYNC EXPORT MAIL] Error consultando LDAP {0} para {1}: "
                "{2}".format(plugin_id, user_id, e))

    logger.info(
        "[ASYNC EXPORT MAIL] Sin email LDAP para {0}; no se notificará.".format(
            user_id))
    return None


def _portal_relative_path(physical_path, site_physical_path):
    """Devuelve la ruta relativa al portal, sin punto de montaje ni id de
    instancia ni host.

    Ejemplo: '/2/genwebupc/ca/demana-un-genweb' -> '/ca/demana-un-genweb'.
    """
    if not physical_path:
        return physical_path
    if site_physical_path and physical_path.startswith(site_physical_path):
        rel = physical_path[len(site_physical_path):]
    else:
        rel = physical_path
    return '/' + rel.strip('/')


def _send_export_notification(site, to_email, subject, body):
    """Envía un correo de notificación de la exportación al usuario.

    Falla de forma silenciosa (solo log) para no romper la tarea por un
    problema de envío de correo.
    """
    if not to_email or site is None:
        logger.info(
            "[ASYNC EXPORT MAIL] Sin email o sitio, no se notifica.")
        return
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from plone import api
        from Products.CMFCore.utils import getToolByName

        mailhost = getToolByName(site, 'MailHost')
        try:
            from_address = api.portal.get_registry_record(
                'plone.email_from_address')
        except Exception:
            from_address = None
        from_address = from_address or 'plone.team@upcnet.es'
        try:
            charset = api.portal.get_registry_record('plone.email_charset')
        except Exception:
            charset = 'utf-8'
        charset = charset or 'utf-8'

        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['charset'] = charset
        msg.attach(MIMEText(body, 'plain', charset))

        logger.info(
            "[ASYNC EXPORT MAIL] Enviant correu a {0}: {1}".format(
                to_email, subject))
        # Mismo patrón que subscribers.py (compatible con PrintingMailHost).
        mailhost.send(msg)
        logger.info(
            "[ASYNC EXPORT MAIL] Notificación enviada a {0}".format(to_email))
    except Exception as e:
        logger.exception(
            "[ASYNC EXPORT MAIL ERROR] No se pudo enviar el correo a "
            "{0}: {1}".format(to_email, e))


@huey_taskqueue.task(retries=1)
def export_download_files_async(context_uid, context_path, site_path,
                                portal_types, ac_cookie=None, base_url=None,
                                user_id=None, user_email=None):
    """
    Tarea asíncrona que genera el .zip de exportación de una carpeta.

    Args:
        context_uid (str): UID de la carpeta a exportar.
        context_path (str): Ruta física de la carpeta (fallback).
        site_path (str): Ruta física del sitio Plone (portal root).
        portal_types (list): Tipos de contenido a incluir en la exportación.
        ac_cookie (str): Cookie ``__ac`` para generar los PDFs autenticados.
        base_url (str): URL absoluta de la carpeta capturada desde el request
            real, necesaria para que wkhtmltopdf alcance las páginas.
        user_id (str): Usuario que lanzó la exportación. Se adopta en el worker
            para tener permisos de creación (en el worker no hay usuario
            autenticado y la creación del File fallaría con un anónimo).
        user_email (str): Email del usuario al que notificar el resultado.

    Returns:
        dict: Resultado de la operación con status y mensaje.
    """
    from genweb6.core.browser.download_files import build_export_zip
    from Zope2 import app
    from Testing.makerequest import makerequest
    from zope.component.hooks import setSite
    from zope.globalrequest import setRequest
    import transaction

    zope_app = None
    site = None
    try:
        # Obtener la aplicación Zope (root) con un REQUEST real montado.
        # En el worker de Huey no hay petición HTTP; makerequest provee un
        # REQUEST adquirible para que ``site.REQUEST`` y todo el código que
        # depende de él (api.content.*, eventos, vistas...) funcionen.
        zope_app = makerequest(app())
        setRequest(zope_app.REQUEST)

        # Obtener el sitio Plone y establecerlo como sitio actual.
        site = zope_app.unrestrictedTraverse(site_path, None)
        if site is None:
            error_msg = "No se pudo obtener sitio: {0}".format(site_path)
            logger.error("[ASYNC EXPORT ERROR] {0}".format(error_msg))
            return {'status': 'error', 'message': error_msg}

        setSite(site)

        # Estrategia 1: obtener por UID (robusto frente a renames).
        context = None
        try:
            from plone import api
            context = api.content.get(UID=context_uid)
            if context is not None:
                logger.info(
                    "[ASYNC EXPORT] Carpeta encontrada por UID: {0}".format(
                        context_uid)
                )
        except Exception as e:
            logger.warning(
                "[ASYNC EXPORT] No se pudo obtener por UID {0}: {1}".format(
                    context_uid, e)
            )

        # Estrategia 2: si el UID falla, obtener por ruta física.
        if context is None:
            logger.info(
                "[ASYNC EXPORT] Intentando obtener por ruta: {0}".format(
                    context_path)
            )
            context = zope_app.unrestrictedTraverse(context_path, None)

        if context is None:
            error_msg = (
                "No se pudo obtener la carpeta. "
                "UID: {0}, Ruta: {1}".format(context_uid, context_path)
            )
            logger.error("[ASYNC EXPORT ERROR] {0}".format(error_msg))
            _send_export_notification(
                site,
                user_email,
                "Exportació de fitxers: error",
                "No s'ha pogut generar l'exportació de la carpeta.\n\n"
                "Ruta: {0}".format(
                    _portal_relative_path(context_path, site_path))
            )
            return {'status': 'error', 'message': error_msg}

        final_path = '/'.join(context.getPhysicalPath())
        logger.info(
            "[ASYNC EXPORT START] Generando exportación: {0} "
            "(UID: {1}, usuario: {2})".format(
                final_path, context_uid, user_id or 'sistema')
        )

        # Adoptar el usuario que lanzó la exportación para tener permisos de
        # creación. En el worker no hay usuario autenticado; sin esto, la
        # creación del File falla ('File' no es construible para un anónimo).
        with _adopt_export_user(site, user_id):
            zip_file = build_export_zip(
                context, portal_types, ac_cookie, base_url)
        transaction.commit()

        if zip_file is None:
            msg = "No se encontraron ficheros para exportar: {0}".format(
                final_path)
            logger.info("[ASYNC EXPORT EMPTY] {0}".format(msg))
            _send_export_notification(
                site,
                user_email,
                "Exportació de fitxers: sense resultats",
                "L'exportació ha finalitzat, però no s'han trobat fitxers "
                "per exportar a:\n{0}".format(
                    _portal_relative_path(final_path, site_path))
            )
            return {'status': 'empty', 'message': msg}

        zip_path = '/'.join(zip_file.getPhysicalPath())
        context_rel_path = _portal_relative_path(final_path, site_path)
        zip_rel_path = _portal_relative_path(zip_path, site_path)
        logger.info(
            "[ASYNC EXPORT SUCCESS] Exportación generada: {0}".format(
                final_path)
        )
        _send_export_notification(
            site,
            user_email,
            "Exportació de fitxers: finalitzada",
            "L'exportació ha finalitzat correctament.\n\n"
            "Carpeta exportada:\n{0}\n\n"
            "El fitxer .zip està disponible a:\n{1}".format(
                context_rel_path, zip_rel_path)
        )
        return {
            'status': 'success',
            'message': 'Exportación generada correctamente: {0}'.format(
                final_path)
        }

    except Exception as e:
        error_msg = "Error generando exportación {0}: {1}".format(
            context_uid, str(e))
        logger.exception("[ASYNC EXPORT EXCEPTION] {0}".format(error_msg))
        transaction.abort()
        _send_export_notification(
            site,
            user_email,
            "Exportació de fitxers: error",
            "S'ha produït un error en generar l'exportació.\n\n"
            "Ruta: {0}".format(
                _portal_relative_path(context_path, site_path))
        )
        return {'status': 'error', 'message': error_msg}

    finally:
        # Limpiar el REQUEST global y cerrar la conexión ZODB del worker.
        setRequest(None)
        if zope_app is not None:
            zope_app._p_jar.close()


def schedule_download_files_export(context, portal_types, ac_cookie=None):
    """
    Encola la exportación de ficheros para procesamiento asíncrono.

    Args:
        context: Carpeta Plone a exportar.
        portal_types (list): Tipos de contenido a incluir.
        ac_cookie (str): Cookie ``__ac`` para generar los PDFs autenticados.

    Returns:
        tuple: ``(queued, message)``. ``queued`` es ``True`` cuando la tarea se
            ha encolado para ejecución asíncrona; ``False`` indica que el
            llamante debe ejecutar la exportación de forma síncrona.
    """
    if not is_async_download_enabled():
        logger.info(
            "[SYNC MODE] Exportación de ficheros en modo síncrono: {0}".format(
                context.absolute_url())
        )
        return (False, None)

    from plone import api

    context_uid = context.UID()
    context_path = '/'.join(context.getPhysicalPath())
    # Capturar la URL real desde el request actual: en el worker no hay request
    # y absolute_url() no devolvería un host alcanzable por wkhtmltopdf.
    base_url = context.absolute_url()
    site = api.portal.get()
    site_path = '/'.join(site.getPhysicalPath())
    # Capturar el usuario actual para adoptarlo en el worker (permisos) y su
    # email del LDAP para notificarle el resultado. Si no hay email en LDAP,
    # user_email queda en None y no se enviará ninguna notificación.
    current_user = api.user.get_current()
    user_id = current_user.getId() if current_user else None
    user_email = _get_ldap_email(site, user_id)

    logger.info(
        "[ASYNC MODE] Encolando exportación de ficheros: {0} "
        "(UID: {1}, usuario: {2}, email: {3})".format(
            base_url, context_uid, user_id or 'sistema',
            user_email or 'sin email')
    )
    export_download_files_async(
        context_uid, context_path, site_path, list(portal_types), ac_cookie,
        base_url, user_id, user_email
    )
    return (True, user_email)
