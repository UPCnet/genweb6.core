# -*- coding: utf-8 -*-
from plone.app.contenttypes import _ as _Plone
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexteritySchema
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implementer

from genweb6.core import _


class IImage(model.Schema, IDexteritySchema):
    """Add field to add image to content
    """

    model.fieldset(
      'Image',
      label=_(u'Image'),
      description=_(u'Image only visible in portlets and in folder and collection views'),
      fields=['image', 'image_caption'])

    image = namedfile.NamedBlobImage(
        title=_Plone(u"Lead Image"),
        description=u"",
        required=True,
    )

    image_caption = schema.TextLine(
        title=_(u"Lead Image Caption"),
        description=u"",
        required=False,
    )

alsoProvides(IImage, IFormFieldProvider)


@implementer(IImage)
class Image(object):
    adapts(IImage)

    def __init__(self, context):
        self.context = context

    def _set_image(self, value):
        self.context.image = value

    def _get_image(self):
        return getattr(self.context, 'image', None)

    image = property(_get_image, _set_image)

    def _set_image_caption(self, value):
        self.context.image_caption = value

    def _get_image_caption(self):
        return getattr(self.context, 'image_caption', None)

    image_caption = property(_get_image_caption, _set_image_caption)
