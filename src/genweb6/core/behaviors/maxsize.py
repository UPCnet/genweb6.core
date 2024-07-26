from plone.supermodel import model
from zope import schema
from collective.easyform import config
from genweb6.core import _
from collective.easyform.interfaces import IFieldExtender
from zope import schema
from plone.supermodel import model
from zope.interface import implementer
from zope.component import adapter
from zope.schema.interfaces import IField
from zope.interface import provider
from plone.supermodel.model import Schema
from plone.autoform import directives as form
from plone.supermodel.directives import fieldset
from plone.autoform.interfaces import IFormFieldProvider



@provider(IFormFieldProvider)
class IMaxSizeExtender(model.Schema):

    max_size = schema.TextLine(
        title=_("Mida màxima"),
        description=_("Mida màxima per als fitxers d'aquest formulari. Número enter"),
        required=False,
        default=u'',
    )



@implementer(IMaxSizeExtender)
class MaxSizeExtender(object):

    def __init__(self, context):
        self.context = context

    def _set_max_size(self, value):
        self.context.max_size = value

    def _get_max_size(self):
        return getattr(self.context, 'max_size', self.context.max_size)

    max_size = property(_get_max_size, _set_max_size)
