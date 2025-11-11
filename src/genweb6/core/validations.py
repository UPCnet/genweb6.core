import imghdr
from typing import Optional

from zope import schema
from zope.component import hooks
from genweb6.core import GenwebMessageFactory as _


class NotAnExternalLink(schema.ValidationError):
    __doc__ = _(u"This is an inner link")


class InvalidImageFile(schema.ValidationError):
    __doc__ = _(u"El fitxer d'imatge no és vàlid")


class UnsafeImageType(schema.ValidationError):
    __doc__ = _(u"Només es permeten imatges JPG, PNG o WEBP")


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
        str: Tipo de imagen detectado ('jpeg', 'png', 'webp') o None si no es válido
        
    Raises:
        InvalidImageFile: Si el archivo no es una imagen válida
        UnsafeImageType: Si el tipo de imagen no está en la lista blanca
    """
    # Lista blanca de tipos permitidos
    ALLOWED_IMAGE_TYPES = {'jpeg', 'png', 'webp'}
    
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
    raise InvalidImageFile(f"Tipo de archivo no reconocido como imagen válida")


def validate_portrait_upload(portrait) -> bool:
    """
    Valida que un archivo subido como portrait sea una imagen segura.
    
    Args:
        portrait: Objeto de archivo subido (debe tener atributos 'data' o ser file-like)
        
    Returns:
        bool: True si la imagen es válida
        
    Raises:
        InvalidImageFile: Si el archivo no es una imagen válida
        UnsafeImageType: Si el tipo de imagen no está permitido
    """
    if not portrait:
        return False
    
    # Obtener el contenido del archivo
    if hasattr(portrait, 'data'):
        file_content = portrait.data
    elif hasattr(portrait, 'read'):
        current_pos = portrait.tell()
        portrait.seek(0)
        file_content = portrait.read()
        portrait.seek(current_pos)
    else:
        raise InvalidImageFile("Formato de archivo no reconocido")
    
    # Validar contenido
    image_type = validate_image_file_content(file_content)
    
    # Si llegamos aquí, la imagen es válida
    return True
