# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer

from genweb6.core import _


class IEventImage(ILeadImage):
    """Extend ILeadImage to add not_show_image field for events
    """

    not_show_image = schema.Bool(
        title=_(u"not_show_image"),
        description=_(u"No mostreu la imatge a la pàgina, però sí que ho feu als portlets i a les vistes."),
        required=False,
        default=False,
    )

alsoProvides(IEventImage, IFormFieldProvider)


@implementer(IEventImage)
class EventImage(object):
    """Adapter for IEventImage behavior
    """

    def __init__(self, context):
        self.context = context

    def _get_not_show_image(self):
        return getattr(self.context, 'not_show_image', False)

    def _set_not_show_image(self, value):
        self.context.not_show_image = value

    not_show_image = property(_get_not_show_image, _set_not_show_image)

