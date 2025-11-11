# -*- coding: utf-8 -*-
"""
Validador de widget para el campo portrait en el formulario de
personal-information.

Este módulo intercepta el widget ANTES de que procese el archivo,
validando que sea una imagen segura mediante magic bytes.
"""
import logging

from plone.namedfile.interfaces import INamedBlobImageField
from z3c.form import validator
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.i18n import translate
from zope.interface import Invalid
from zope.interface import implementer

try:
    from plone.namedfile.widget import NamedImageWidget
except ImportError:
    # Fallback para versiones más antiguas
    from plone.formwidget.namedfile.widget import NamedImageWidget

from genweb6.core.validations import (
    validate_portrait_upload,
    InvalidImageFile,
    UnsafeImageType,
)

logger = logging.getLogger(__name__)


class ValidatedPortraitWidget(NamedImageWidget):
    """
    Widget personalizado para el campo portrait que valida ANTES de procesar.

    Este widget sobreescribe el método extract() para validar el archivo
    antes de que plone.namedfile lo procese.
    """

    def extract(self, default=NOVALUE):
        """
        Extrae el valor del widget y valida ANTES de procesar.

        Returns:
            El valor extraído del widget o None

        Raises:
            Invalid: Si el archivo no es válido
        """
        # Verificar si la acción es "remove" (eliminar imagen)
        # En ese caso, retornar None inmediatamente como hace el widget padre
        # Esto debe hacerse ANTES de cualquier otra validación
        url = self.request.getURL()
        action = self.request.get("%s.action" % self.name, None)

        # Ignorar requests de validación (igual que hace el widget padre)
        if url.endswith("kss_z3cform_inline_validation") or url.endswith(
            "z3cform_validate_field"
        ):
            action = "nochange"

        if action == "remove":
            # Es una eliminación, retornar None inmediatamente
            # (igual que hace el widget padre)
            logger.debug(
                "Acción de eliminación detectada para portrait, "
                "retornando None"
            )
            return None

        # Interceptar el archivo RAW del request ANTES de procesar
        if hasattr(self, 'request') and self.request:
            form = self.request.form
            field_name = self.name

            # Buscar el archivo en el formulario antes de procesar
            if field_name in form:
                file_data = form[field_name]

                # Verificar si realmente hay un archivo nuevo que subir
                # No validar si:
                # - file_data es None, string vacío, o similar
                # - No tiene filename (no es un archivo real)
                # - El filename está vacío
                has_file = False
                if file_data:
                    # Verificar si es un objeto de archivo con contenido real
                    if hasattr(file_data, 'filename'):
                        filename = getattr(file_data, 'filename', '')
                        # Solo validar si hay un filename no vacío
                        if filename and filename.strip():
                            has_file = True
                    elif (hasattr(file_data, 'file') or
                          hasattr(file_data, 'read')):
                        # Es un objeto file-like, verificar si tiene contenido
                        try:
                            if hasattr(file_data, 'read'):
                                current_pos = file_data.tell()
                                file_data.seek(0, 2)  # Ir al final
                                size = file_data.tell()
                                file_data.seek(current_pos)  # Volver
                                if size > 0:
                                    has_file = True
                        except (AttributeError, IOError, TypeError):
                            # Si no se puede verificar, asumir que no hay
                            # archivo
                            has_file = False

                # Solo validar si realmente hay un archivo nuevo que subir
                if has_file:
                    try:
                        # Validar el archivo RAW antes de procesar
                        validate_portrait_upload(file_data)
                        logger.debug(
                            f"Portrait validado correctamente en widget "
                            f"extract (RAW): "
                            f"{getattr(file_data, 'filename', 'unknown')}"
                        )
                    except (InvalidImageFile, UnsafeImageType) as e:
                        # Log del intento de subida de archivo no válido
                        filename = getattr(file_data, 'filename', 'unknown')
                        logger.warning(
                            f"Intento de subir archivo no válido como "
                            f"portrait en widget (RAW). Filename: {filename}, "
                            f"Error: {str(e)}"
                        )
                        # Obtener el mensaje traducido
                        try:
                            # e.__doc__ es un objeto de traducción, traducirlo
                            error_msg = translate(
                                e.__doc__,
                                domain='genweb',
                                context=self.request
                            )
                        except Exception:
                            # Si falla la traducción, usar el mensaje original
                            error_msg = (
                                str(e.__doc__) or
                                u"El fitxer d'imatge no és vàlid"
                            )

                        # Mostrar mensaje de error usando el sistema de
                        # mensajes de Plone en lugar de lanzar Invalid
                        from Products.statusmessages.interfaces import (
                            IStatusMessage
                        )
                        IStatusMessage(self.request).addStatusMessage(
                            error_msg,
                            type='error'
                        )

                        # Limpiar el campo del formulario para que no se
                        # procese. Retornar None para que no se guarde nada
                        self.value = None
                        return None

        # Ahora llamar al método extract() del padre para procesar
        try:
            value = super(ValidatedPortraitWidget, self).extract()
        except Exception as e:
            # Si el padre falla (por ejemplo, porque el archivo no es válido),
            # capturar el error y mostrar mensaje
            logger.warning(
                f"Error al procesar portrait en widget padre: {str(e)}"
            )
            # Mostrar mensaje de error
            from Products.statusmessages.interfaces import IStatusMessage
            try:
                error_msg = translate(
                    u"El fitxer d'imatge no és vàlid",
                    domain='genweb',
                    context=self.request
                )
            except Exception:
                error_msg = u"El fitxer d'imatge no és vàlid"
            IStatusMessage(self.request).addStatusMessage(
                error_msg,
                type='error'
            )
            self.value = None
            return None

        # Validación adicional después del procesamiento (solo si hay valor)
        # No validar si value es None o vacío (caso de eliminación)
        if value and hasattr(value, 'filename') and value.filename:
            try:
                validate_portrait_upload(value)
                logger.debug(
                    f"Portrait validado correctamente en widget extract "
                    f"(procesado): {getattr(value, 'filename', 'unknown')}"
                )
            except (InvalidImageFile, UnsafeImageType) as e:
                filename = getattr(value, 'filename', 'unknown')
                logger.warning(
                    f"Intento de subir archivo no válido como portrait "
                    f"en widget (procesado). Filename: {filename}, "
                    f"Error: {str(e)}"
                )
                # Obtener el mensaje traducido
                try:
                    # e.__doc__ es un objeto de traducción, traducirlo
                    error_msg = translate(
                        e.__doc__,
                        domain='genweb',
                        context=self.request
                    )
                except Exception:
                    # Si falla la traducción, usar el mensaje original
                    error_msg = (
                        str(e.__doc__) or
                        u"El fitxer d'imatge no és vàlid"
                    )

                # Mostrar mensaje de error usando el sistema de mensajes
                from Products.statusmessages.interfaces import IStatusMessage
                IStatusMessage(self.request).addStatusMessage(
                    error_msg,
                    type='error'
                )

                # Retornar None para que no se guarde nada
                self.value = None
                return None

        return value


class PortraitWidgetValidator(validator.SimpleFieldValidator):
    """
    Validador de widget para el campo portrait (fallback).

    Este validador se ejecuta como respaldo si el widget personalizado
    no se aplica por alguna razón.
    """

    def validate(self, value):
        """
        Valida que el archivo subido sea una imagen segura.

        Args:
            value: El valor del widget (puede ser None, un NamedBlobFile, etc.)

        Raises:
            Invalid: Si el archivo no es válido
        """
        # Si no hay valor, no validar (campo opcional)
        if not value:
            return

        # Si el valor es un string vacío o similar, no validar
        if hasattr(value, '__len__') and len(value) == 0:
            return

        try:
            # Validar el archivo usando nuestra función de validación
            validate_portrait_upload(value)
            logger.debug(
                f"Portrait validado correctamente en widget validator: "
                f"{getattr(value, 'filename', 'unknown')}"
            )
        except (InvalidImageFile, UnsafeImageType) as e:
            # Log del intento de subida de archivo no válido
            filename = getattr(value, 'filename', 'unknown')
            logger.warning(
                f"Intento de subir archivo no válido como portrait en widget. "
                f"Filename: {filename}, Error: {str(e)}"
            )
            # Obtener el mensaje traducido
            try:
                # Necesitamos el request del widget para traducir
                if hasattr(self, 'request') and self.request:
                    # e.__doc__ es un objeto de traducción, traducirlo
                    error_msg = translate(
                        e.__doc__,
                        domain='genweb',
                        context=self.request
                    )
                else:
                    error_msg = (
                        str(e.__doc__) or
                        u"El fitxer d'imatge no és vàlid"
                    )
            except Exception:
                # Si falla la traducción, usar el mensaje original
                error_msg = str(e.__doc__) or "El fitxer d'imatge no és vàlid"

            # Lanzar Invalid para que z3c.form muestre el error
            raise Invalid(error_msg)


# Factory para crear el widget personalizado
@adapter(INamedBlobImageField, IFormLayer)
@implementer(IFieldWidget)
def ValidatedPortraitFieldWidget(field, request):
    """Factory para crear el widget personalizado de portrait."""
    return FieldWidget(field, ValidatedPortraitWidget(request))


# Registrar el validador como fallback
validator.WidgetValidatorDiscriminators(
    PortraitWidgetValidator,
    field=INamedBlobImageField,
)
