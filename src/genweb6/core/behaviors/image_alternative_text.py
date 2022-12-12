# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implementer

from genweb6.core import _


class IImageAlternativeText(model.Schema):

    directives.order_after(image_alternative_text='image')
    image_alternative_text = schema.TextLine(
        title=_(u"Text alternatiu per l'imatge"),
        required=False,
    )


alsoProvides(IImageAlternativeText, IFormFieldProvider)


@implementer(IImageAlternativeText)
class ImageAlternativeText(object):
    adapts(IImageAlternativeText)

    def __init__(self, context):
        self.context = context

    def _set_image_alternative_text(self, value):
        self.context.image_alternative_text = value

    def _get_image_alternative_text(self):
        return getattr(self.context, 'image_alternative_text', None)

    image_alternative_text = property(_get_image_alternative_text, _set_image_alternative_text)
