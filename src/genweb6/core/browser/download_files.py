# -*- coding: utf-8 -*-
from plone.base.interfaces.constrains import ISelectableConstrainTypes
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from datetime import datetime
from plone import api
from plone.namedfile import NamedBlobFile
from zope.i18n import translate

from genweb6.core import _
from genweb6.core.utils import set_pdf_metadata

import hashlib
import logging
import os
import shutil
import tempfile
import uuid

import pdfkit
import transaction

logger = logging.getLogger(__name__)

_DOWNLOAD_TYPE_IDS = (
    'File',
    'Image',
    'News Item',
    'Document',
    'genweb.upc.documentimage',
    'Event',
)
# Asegurar INFO también cuando la exportación corre en el consumer de Huey,
# que deja el root logger en WARNING.
logger.setLevel(logging.INFO)


def _export_temp_dir():
    """Directorio temporal para la exportación (``TMPDIR`` o ``/tmp``)."""
    tmpdir = os.environ.get('TMPDIR') or '/tmp'
    os.makedirs(tmpdir, exist_ok=True)
    return tmpdir


def _running_on_localhost(base_url):
    """Devuelve True si la exportación se está generando contra localhost.

    Sirve para activar logs de depuración del proceso de wkhtmltopdf solo en
    entornos de desarrollo, sin ensuciar los logs de producción.
    """
    if not base_url:
        return False
    base_url = base_url.lower()
    return 'localhost' in base_url


def export_portal_types_hash(portal_types):
    """Hash corto (5 chars) derivado de los tipos de contenido exportados."""
    key = ','.join(sorted(set(portal_types or [])))
    return hashlib.md5(key.encode('utf-8')).hexdigest()[:5]


def query_items_under_root(root, portal_types):
    """
    Todos los contenidos bajo ``root`` que coincidan con ``portal_types``,
    ordenados por path (padre antes que hijo). No usa el árbol de navegación,
    así que incluye Document, File, etc. aunque no aparezcan en el menú.
    """
    catalog = api.portal.get_tool('portal_catalog')
    base_path = '/'.join(root.getPhysicalPath())
    brains = catalog.searchResults(
        path={'query': base_path},
        portal_type=list(portal_types),
    )
    items = [b for b in brains if b.getPath() != base_path]
    items.sort(key=lambda b: b.getPath())
    return items


def get_system_fonts_css(target_dir=None):
    """Crea un archivo CSS temporal que fuerza el uso de fuentes del sistema.

    Se escribe en ``target_dir`` (si se indica) para evitar colisiones entre
    ejecuciones concurrentes; por defecto usa el directorio temporal del SO.
    """
    target_dir = target_dir or _export_temp_dir()
    css_file = os.path.join(target_dir, 'system_fonts_pdf.css')
    # CSS que fuerza fuentes del sistema estándar y maximiza el ancho del contenido
    css_content = """
/* Fuerza el uso de fuentes del sistema estándar */
* {
    font-family: Arial, Helvetica, "Liberation Sans", "DejaVu Sans", sans-serif !important;
}
"""
    with open(css_file, 'w') as f:
        f.write(css_content)
    return css_file


def build_export_zip(context, portal_types, ac_cookie=None, base_url=None):
    """
    Genera el fichero .zip de exportación dentro de ``context``.

    Lógica reutilizable que se ejecuta tanto en modo síncrono (desde la vista)
    como asíncrono (desde la tarea Huey). No depende del ``request``.

    Args:
        context: Carpeta Plone a exportar.
        portal_types (list): Tipos de contenido a incluir en la exportación.
        ac_cookie (str): Cookie ``__ac`` para generar los PDFs autenticados.
        base_url (str): URL absoluta de ``context`` capturada desde el request
            real. Necesaria en modo asíncrono porque en el worker no hay
            request y ``obj.absolute_url()`` no produce un host alcanzable por
            wkhtmltopdf. En modo síncrono puede omitirse.

    Returns:
        El objeto ``File`` creado con el .zip, o ``None`` si no hay contenidos.
    """
    items = query_items_under_root(context, portal_types)
    if not items:
        return None

    today = datetime.today().strftime("%Y-%m-%d")
    types_hash = export_portal_types_hash(portal_types)
    plone_id = 'export-{0}-{1}'.format(context.id, types_hash)
    exp_path = 'export-{0}-{1}-{2}'.format(context.id, today, types_hash)

    if plone_id in context:
        # manage_delObjects no requiere REQUEST (api.content.delete sí, por
        # la comprobación de link integrity).
        context.manage_delObjects([plone_id])

    items = query_items_under_root(context, portal_types)
    from_path = '/'.join(context.getPhysicalPath())
    context_base_url = (base_url or context.absolute_url()).rstrip('/')
    debug_local = _running_on_localhost(context_base_url)
    if debug_local:
        logger.info(
            "[DOWNLOAD FILES DEBUG] Generando exportación contra localhost: "
            "base_url=%s, tipos=%s", context_base_url, portal_types)

    # Directorio de trabajo temporal único (seguFro ante concurrencia y sin
    # depender del working directory del proceso, que en el worker async puede
    # ser distinto al de la instancia).
    work_dir = tempfile.mkdtemp(
        prefix='gw6-download-files-', dir=_export_temp_dir())
    try:
        export_root = os.path.join(work_dir, exp_path)
        os.makedirs(export_root)

        options_pdf = {'cookie': [('__ac', ac_cookie)]} if ac_cookie else {}

        # No abortar la generación si un sub-recurso (imagen, fuente, JS...)
        # falla al cargar. Evita "Exit with code 1 due to network error:
        # UnknownContentError" cuando wkhtmltopdf no llega a un recurso
        # secundario.
        options_pdf['load-error-handling'] = 'ignore'
        options_pdf['load-media-error-handling'] = 'ignore'

        css_file = get_system_fonts_css(work_dir)
        options_pdf['user-style-sheet'] = css_file

        for item in items:
            relative_path = os.path.relpath(item.getPath(), from_path)
            dest_path = os.path.join(export_root, relative_path)
            is_folderish = getattr(item, 'is_folderish', False) or \
                item.portal_type in ('Folder', 'LIF', 'LRF', 'Large Folder')

            if is_folderish:
                os.makedirs(dest_path, exist_ok=True)
                logger.info("Saved {}".format(dest_path))
            elif item.portal_type == 'File':
                obj = item.getObject()
                file_field = getattr(obj, 'file', None)
                if file_field is None:
                    continue
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, 'wb') as f:
                    f.write(file_field.data)
                logger.info("Saved {}".format(dest_path))
            elif item.portal_type == 'Image':
                obj = item.getObject()
                image_field = getattr(obj, 'image', None)
                if image_field is None:
                    continue
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, 'wb') as f:
                    f.write(image_field.data)
                logger.info("Saved {}".format(dest_path))
            elif item.portal_type in ['News Item', 'Document',
                                      'genweb.upc.documentimage', 'Event']:
                obj = item.getObject()
                pdf_path = dest_path + '.pdf'
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                url = (
                    '{0}/{1}/@@genweb.get.dxdocument.text.complete.style'
                    .format(context_base_url,
                            relative_path.replace(os.sep, '/'))
                )
                tmp_pdf = os.path.join(
                    work_dir, '{0}.pdf'.format(uuid.uuid4().hex))
                if debug_local:
                    logger.info(
                        "[DOWNLOAD FILES DEBUG] wkhtmltopdf %s -> %s "
                        "(cookie __ac=%s, opciones=%s)",
                        url, tmp_pdf, 'sí' if ac_cookie else 'no', options_pdf)
                try:
                    # verbose=True deja que pdfkit propague la salida de
                    # wkhtmltopdf; solo en localhost para depurar el proceso.
                    pdfkit.from_url(url, tmp_pdf, options=options_pdf,
                                    verbose=debug_local)
                    if debug_local:
                        size = (os.path.getsize(tmp_pdf)
                                if os.path.isfile(tmp_pdf) else 0)
                        logger.info(
                            "[DOWNLOAD FILES DEBUG] wkhtmltopdf finalizó: "
                            "%s (%s bytes)", tmp_pdf, size)
                    if os.path.isfile(tmp_pdf) and os.path.getsize(tmp_pdf) > 0:
                        shutil.move(tmp_pdf, pdf_path)
                        title = obj.Title()
                        language = getattr(obj, 'language', None)
                        if not language:
                            try:
                                language = api.portal.get_registry_record(
                                    'plone.default_language'
                                )
                            except Exception:
                                language = 'ca'
                        set_pdf_metadata(pdf_path, title, language)
                        logger.info("Saved {}".format(pdf_path))
                except Exception as e:
                    # Un documento que falle no debe abortar toda la
                    # exportación; se omite y se registra.
                    logger.warning(
                        "[DOWNLOAD FILES] No se pudo generar el PDF de %s: %s",
                        url, e)
                finally:
                    if os.path.isfile(tmp_pdf):
                        try:
                            os.remove(tmp_pdf)
                        except OSError:
                            pass

        # Empaquetado seguro: shutil.make_archive en lugar de os.system('zip').
        zip_base = os.path.join(work_dir, exp_path)
        shutil.make_archive(zip_base, 'zip', root_dir=work_dir,
                             base_dir=exp_path)
        zip_full_path = zip_base + '.zip'

        allowed_types = [ct.id for ct in context.allowedContentTypes()]
        disable_file = False
        if 'File' not in allowed_types:
            disable_file = True
            behavior = ISelectableConstrainTypes(context)
            behavior.setLocallyAllowedTypes(list(allowed_types + ['File']))

        zip_file = api.content.create(
            type='File',
            title=exp_path,
            id=plone_id,
            container=context,
        )
        with open(zip_full_path, 'rb') as zip_fh:
            zip_file.file = NamedBlobFile(
                data=zip_fh.read(),
                filename=u'{}.zip'.format(exp_path),
                contentType='application/zip'
            )

        if disable_file:
            behavior.setLocallyAllowedTypes(list(allowed_types))

        zip_file.reindexObject()
        transaction.commit()
        return zip_file
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


class DownloadFiles(BrowserView):

    template = ViewPageTemplateFile('views_templates/download_files.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def options(self):
        portal_types = api.portal.get().portal_types
        return {
            type_id: translate(
                portal_types[type_id].Title(),
                context=self.request,
            )
            for type_id in _DOWNLOAD_TYPE_IDS
        }

    def __call__(self):
        form = self.request.form
        if not form or 'file_type' not in form:
            return self.template()

        query = {'portal_type': []}
        options = [key for key in self.options().keys()]
        if 'all' in form['file_type']:
            query['portal_type'] = ['LIF', 'LRF', 'Folder'] + options
        else:
            query['portal_type'] = ['LIF', 'LRF', 'Folder']
            for option in options:
                if option in form['file_type']:
                    query['portal_type'].append(option)

        items = query_items_under_root(self.context, query['portal_type'])
        if not items:
            IStatusMessage(self.request).addStatusMessage(u"No files found!", "info")
            return self.template()

        ac_cookie = self.request.cookies.get('__ac')

        from genweb6.core.async_tasks import schedule_download_files_export
        queued, user_email, block_reason = schedule_download_files_export(
            self.context, query['portal_type'], ac_cookie
        )

        if block_reason == 'duplicate':
            queue_url = '{0}/@@export_files_queue'.format(
                api.portal.get().absolute_url())
            message = _(
                u"Ja hi ha una exportació en curs per a aquesta carpeta amb "
                u"els mateixos tipus de fitxer. Espereu que finalitzi o "
                u"cancel·leu-la des de la gestió de la cua: ${queue_url}",
                mapping={u'queue_url': queue_url})
            IStatusMessage(self.request).addStatusMessage(message, "warning")
            return self.template()

        if queued:
            # Modo asíncrono: la tarea se ha encolado, respondemos al instante.
            if user_email:
                message = _(
                    u"L'exportació s'està generant en segon pla. Trobaràs el "
                    u"fitxer .zip en aquesta carpeta quan finalitzi. "
                    u"Rebràs un correu electrònic quan finalitzi el procés a "
                    u"${email}.",
                    mapping={u'email': user_email})
            else:
                message = _(
                    u"L'exportació s'està generant en segon pla. Trobaràs el "
                    u"fitxer .zip en aquesta carpeta quan finalitzi el "
                    u"procés.")
            IStatusMessage(self.request).addStatusMessage(message, "info")
            return self.template()

        # Modo síncrono: generamos el .zip y redirigimos al fichero creado.
        zip_file = build_export_zip(self.context, query['portal_type'], ac_cookie)
        if zip_file is None:
            IStatusMessage(self.request).addStatusMessage(u"No files found!", "info")
            return self.template()
        self.request.response.redirect(zip_file.absolute_url() + '/view')


