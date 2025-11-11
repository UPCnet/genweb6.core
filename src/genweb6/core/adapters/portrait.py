# -*- coding: utf-8 -*-
import logging

from OFS.Image import Image
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.interfaces.membership import IMembershipTool
from Products.PlonePAS.utils import scale_image
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface

from genweb6.core.validations import (
    validate_portrait_upload,
    InvalidImageFile,
    UnsafeImageType,
)

logger = logging.getLogger(__name__)


class IPortraitUploadAdapter(Interface):
    """ The marker interface for the portrait upload adapter used for implement
        special actions after upload. The idea is to have a default (core)
        action and then other that override the default one using IBrowserLayer.
    """


@implementer(IPortraitUploadAdapter)
class PortraitUploadAdapter(object):
    adapts(IMembershipTool, Interface)

    """ Default adapter for portrait custom actions """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, portrait, safe_id):
        if portrait and portrait.filename:
            # Validar que el archivo sea una imagen segura ANTES de procesarlo
            try:
                validate_portrait_upload(portrait)
            except (InvalidImageFile, UnsafeImageType) as e:
                # Log del intento de subida de archivo no válido
                logger.warning(
                    f"Intento de subir archivo no válido como portrait. "
                    f"Usuario: {safe_id}, Filename: {portrait.filename}, "
                    f"Error: {str(e)}"
                )
                # Re-lanzar la excepción para que el usuario vea el error
                raise
            
            # Solo si la validación pasa, procesar la imagen
            try:
                scaled, mimetype = scale_image(portrait)
                portrait = Image(id=safe_id, file=scaled, title='')
                membertool = getToolByName(self.context, 'portal_memberdata')
                membertool._setPortrait(portrait, safe_id)
                logger.info(f"Portrait actualizado correctamente para usuario: {safe_id}")
            except Exception as e:
                logger.error(
                    f"Error al procesar portrait para usuario {safe_id}: {str(e)}"
                )
                raise
