# -*- coding: utf-8 -*-
"""
Tareas asíncronas para procesamiento en background usando collective.taskqueue2

Este módulo contiene las tareas que se ejecutan de forma asíncrona
usando el sistema de colas de Huey.
"""
import logging
import os

logger = logging.getLogger(__name__)
logger.propagate = False  # Evitar logs duplicados

# Intentar importar collective.taskqueue2
# Si no está disponible, las tareas se ejecutarán de forma síncrona
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

    # Definir un decorador dummy para compatibilidad
    class DummyTaskQueue:
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    huey_taskqueue = DummyTaskQueue()


def is_async_enabled():
    """
    Verifica si el procesamiento asíncrono está habilitado.

    Se activa con la variable de entorno GENWEB_ASYNC_PDF_CLEANING=1
    """
    async_env = os.environ.get('GENWEB_ASYNC_PDF_CLEANING', '0') == '1'
    return async_env and TASKQUEUE_AVAILABLE


@huey_taskqueue.task(retries=3)
def clean_pdf_async(obj_uid, obj_path, site_path, field_name='file'):
    """
    Tarea asíncrona para limpiar metadatos de un PDF.

    Args:
        obj_uid (str): UID del objeto Plone
        obj_path (str): Ruta física del objeto (fallback)
        site_path (str): Ruta física del sitio Plone (portal root)
        field_name (str): Nombre del campo que contiene el archivo

    Returns:
        dict: Resultado de la operación con status y mensaje
    """
    from genweb6.core.subscribers import clean_pdf_on_upload
    from Zope2 import app
    from zope.component.hooks import setSite
    import transaction

    zope_app = None
    try:
        # Obtener la aplicación Zope (root)
        zope_app = app()

        # Obtener el sitio Plone y establecerlo como sitio actual
        site = zope_app.unrestrictedTraverse(site_path, None)
        if site is None:
            error_msg = f"No se pudo obtener sitio: {site_path}"
            logger.error(f"[ASYNC TASK ERROR] {error_msg}")
            return {'status': 'error', 'message': error_msg}

        # Establecer el sitio activo para que funcione registry
        setSite(site)

        # Estrategia 1: Intentar obtener por UID (más robusto para renames)
        obj = None
        try:
            from plone import api
            obj = api.content.get(UID=obj_uid)
            if obj:
                logger.info(
                    f"[ASYNC TASK] Objeto encontrado por UID: {obj_uid}"
                )
        except Exception as e:
            logger.warning(
                f"[ASYNC TASK] No se pudo obtener por UID {obj_uid}: {e}"
            )

        # Estrategia 2: Si UID falla, intentar por ruta física
        if obj is None:
            logger.info(
                f"[ASYNC TASK] Intentando obtener por ruta: {obj_path}"
            )
            obj = zope_app.unrestrictedTraverse(obj_path, None)

        if obj is None:
            error_msg = (
                f"No se pudo obtener objeto. "
                f"UID: {obj_uid}, Ruta: {obj_path}"
            )
            logger.error(f"[ASYNC TASK ERROR] {error_msg}")
            return {'status': 'error', 'message': error_msg}

        # Ejecutar limpieza del PDF (función existente)
        final_path = '/'.join(obj.getPhysicalPath())
        logger.info(
            f"[ASYNC TASK START] Limpiando PDF: {final_path} "
            f"(UID: {obj_uid})"
        )
        clean_pdf_on_upload(obj, field_name)

        # Commit de la transacción
        transaction.commit()
        logger.info(f"[ASYNC TASK SUCCESS] PDF limpiado: {final_path}")

        return {
            'status': 'success',
            'message': f'PDF limpiado correctamente: {final_path}'
        }

    except Exception as e:
        error_msg = f"Error limpiando PDF {obj_uid}: {str(e)}"
        logger.exception(f"[ASYNC TASK EXCEPTION] {error_msg}")
        transaction.abort()
        return {'status': 'error', 'message': error_msg}

    finally:
        # Cerrar la conexión ZODB
        if zope_app is not None:
            zope_app._p_jar.close()


def schedule_pdf_cleaning(obj, field_name='file'):
    """
    Encola la limpieza de un PDF para procesamiento asíncrono.

    Si el modo asíncrono no está habilitado,
    ejecuta la limpieza de forma síncrona.

    Args:
        obj: Objeto Plone que contiene el PDF
        field_name (str): Nombre del campo que contiene el archivo

    Returns:
        tuple: (success, message)
    """
    try:
        if is_async_enabled():
            # Obtener UID y ruta del objeto
            obj_uid = obj.UID()
            obj_path = '/'.join(obj.getPhysicalPath())

            # Obtener el sitio Plone (portal root)
            from Acquisition import aq_base
            site = obj
            while site is not None:
                if hasattr(aq_base(site), 'portal_url'):
                    break
                parent = getattr(site, '__parent__', None)
                if parent is None:
                    parent = getattr(site, 'aq_parent', None)
                site = parent

            if site is None:
                # Fallback: modo síncrono si no encontramos sitio
                logger.warning(
                    f"[ASYNC WARNING] No se pudo obtener sitio, "
                    f"ejecutando síncrono"
                )
                from genweb6.core.subscribers import clean_pdf_on_upload
                clean_pdf_on_upload(obj, field_name)
                msg = (
                    f"PDF limpiado síncronamente (fallback): "
                    f"{obj.absolute_url()}"
                )
                return (True, msg)

            site_path = '/'.join(site.getPhysicalPath())

            # Modo asíncrono: encolar tarea con UID y ruta
            logger.info(
                f"[ASYNC MODE] Encolando limpieza PDF: "
                f"{obj.absolute_url()} (UID: {obj_uid})"
            )
            clean_pdf_async(obj_uid, obj_path, site_path, field_name)
            msg = (
                f"PDF encolado para limpieza asíncrona: "
                f"{obj.absolute_url()}"
            )
            return (True, msg)
        else:
            # Modo síncrono: ejecutar directamente (actual)
            obj_path = '/'.join(obj.getPhysicalPath())
            logger.info(
                f"[SYNC MODE] Limpiando PDF de forma síncrona: "
                f"{obj_path}"
            )
            from genweb6.core.subscribers import clean_pdf_on_upload
            clean_pdf_on_upload(obj, field_name)
            msg = f"PDF limpiado de forma síncrona: {obj.absolute_url()}"
            return (True, msg)

    except Exception as e:
        error_msg = f"Error programando limpieza de PDF: {str(e)}"
        logger.exception(error_msg)
        return (False, error_msg)
