from typing import Optional

from zope import schema
from zope.component import hooks
from genweb6.core import GenwebMessageFactory as _


class NotAnExternalLink(schema.ValidationError):
    __doc__ = _(u"This is an inner link")


class InvalidImageFile(schema.ValidationError):
    __doc__ = _(u"El fitxer d'imatge no és vàlid")


class UnsafeImageType(schema.ValidationError):
    __doc__ = _(u"El fitxer d'imatge no és vàlid")


def validate_externalurl(value):
    root_url = hooks.getSite().absolute_url()
    link_extern = value.lower()

    if root_url.startswith("http://"):
        root_url = root_url[7:]
    elif root_url.startswith("https://"):
        root_url = root_url[8:]

    if link_extern.startswith("http://"):
        link_extern = link_extern[7:]
    elif link_extern.startswith("https://"):
        link_extern = link_extern[8:]

    isInnerLink = link_extern.startswith(root_url)
    if isInnerLink:
        raise NotAnExternalLink(value)
    return not isInnerLink


def validate_image_file_content(file_data) -> Optional[str]:
    """
    Valida que un archivo sea una imagen real verificando sus magic bytes.

    Args:
        file_data: Objeto file-like o bytes con el contenido del archivo

    Returns:
        str: Tipo de imagen detectado ('jpeg', 'png', 'webp') o None

    Raises:
        InvalidImageFile: Si el archivo no es una imagen válida
        UnsafeImageType: Si el tipo de imagen no está en la lista blanca
    """
    # Leer los primeros bytes para verificación
    if hasattr(file_data, 'read'):
        # Es un objeto file-like
        current_pos = file_data.tell()
        file_data.seek(0)
        header = file_data.read(32)
        file_data.seek(current_pos)  # Restaurar posición
    else:
        # Es bytes directamente
        header = file_data[:32] if len(file_data) >= 32 else file_data

    # Verificar magic bytes manualmente para mayor seguridad
    if len(header) < 4:
        raise InvalidImageFile("Archivo demasiado pequeño")

    # JPEG: FF D8 FF
    if header[:3] == b'\xff\xd8\xff':
        return 'jpeg'

    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if header[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
        return 'png'

    # WebP: RIFF ... WEBP
    if len(header) >= 12 and header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return 'webp'

    # Si no coincide con ningún tipo permitido
    raise InvalidImageFile("Tipo de archivo no reconocido como imagen válida")


def validate_portrait_upload(portrait) -> bool:
    """
    Valida que un archivo subido como portrait sea una imagen segura.

    Esta función lee SOLO los primeros bytes del archivo para validar
    los magic bytes, sin consumir todo el stream, para que el objeto
    portrait siga siendo utilizable después de la validación.

    Args:
        portrait: Objeto de archivo subido (puede ser NamedBlobFile,
            file-like, o tener atributo 'data')

    Returns:
        bool: True si la imagen es válida

    Raises:
        InvalidImageFile: Si el archivo no es una imagen válida
        UnsafeImageType: Si el tipo de imagen no está permitido
    """
    if not portrait:
        return False

    # Leer SOLO los primeros 32 bytes para validación (magic bytes)
    # Esto evita consumir todo el stream y permite que el objeto
    # portrait siga siendo utilizable después
    header = None

    # Método 1: Si tiene atributo 'data' (NamedBlobFile, etc.)
    if hasattr(portrait, 'data'):
        data = portrait.data
        # Si data es bytes directamente
        if isinstance(data, bytes):
            header = data[:32]
        # Si data es un objeto file-like o blob
        elif hasattr(data, 'read'):
            try:
                current_pos = data.tell()
            except (AttributeError, IOError, TypeError):
                current_pos = 0
            try:
                data.seek(0)
                header = data.read(32)
                # Asegurarse de que header es bytes
                if not isinstance(header, bytes):
                    header = bytes(header)
                data.seek(current_pos)
            except (AttributeError, IOError, TypeError):
                # Si no se puede hacer seek, leer directamente
                header = data.read(32)
                if not isinstance(header, bytes):
                    header = bytes(header)
        # Si data es un objeto blob de ZODB
        elif hasattr(data, 'open'):
            try:
                with data.open() as f:
                    header = f.read(32)
                    if not isinstance(header, bytes):
                        header = bytes(header)
            except (AttributeError, IOError, TypeError):
                raise InvalidImageFile(
                    "No se pudo leer el contenido del archivo blob"
                )

    # Método 2: Si es un objeto file-like con método read()
    elif hasattr(portrait, 'read'):
        try:
            current_pos = portrait.tell()
        except (AttributeError, IOError):
            current_pos = 0

        try:
            portrait.seek(0)
            header = portrait.read(32)
            portrait.seek(current_pos)
        except (AttributeError, IOError):
            # Si no se puede hacer seek, leer directamente
            # (esto puede consumir el stream, pero es el último recurso)
            header = portrait.read(32)

    # Método 3: Si tiene atributo 'file' (algunos objetos de formulario)
    elif hasattr(portrait, 'file'):
        file_obj = portrait.file
        if hasattr(file_obj, 'data'):
            data = file_obj.data
            if isinstance(data, bytes):
                header = data[:32]
            elif hasattr(data, 'read'):
                try:
                    data.seek(0)
                    header = data.read(32)
                    data.seek(0)
                except (AttributeError, IOError):
                    header = data.read(32)
        elif hasattr(file_obj, 'read'):
            try:
                file_obj.seek(0)
                header = file_obj.read(32)
                file_obj.seek(0)
            except (AttributeError, IOError):
                header = file_obj.read(32)

    # Método 4: Si es bytes directamente
    elif isinstance(portrait, bytes):
        header = portrait[:32]

    if header is None:
        raise InvalidImageFile("No se pudo leer el contenido del archivo")

    # Validar contenido por magic bytes (solo los primeros bytes)
    validate_image_file_content(header)

    # Si llegamos aquí, la imagen es válida
    return True
