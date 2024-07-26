from zope.interface import Interface
from zope.interface import implementer
from zope.component import adapter
from plone.namedfile.interfaces import IPluggableFileFieldValidation
from plone.namedfile.interfaces import INamedFileField
from zope.schema import ValidationError


@implementer(IPluggableFileFieldValidation)
@adapter(INamedFileField, Interface)
class FileSizeValidator(object):
   
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __call__(self):
        mb_max_size = getattr(self.field.context, 'max_size', None)

        if not mb_max_size:
            return
        
        int_max_size = None
        
        try:
            int_max_size = int(mb_max_size) * 1024 * 1024
        except ValueError:
            return
        
        mb_value_size = round(self.value.size / (1024 * 1024), 2)
        
        if self.value.size > int_max_size:
            self.field.context.plone_utils.addPortalMessage(
                f"La mida màxima permesa per arxiu és {mb_max_size} MB, mida de l'arxiu pujat: {mb_value_size} MB", type='error')
            raise InvalidFileSizeError()


class InvalidFileSizeError(ValidationError):
    """Exception for file size too large"""
    __doc__ = "La mida de l'arxiu és massa gran."


