# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implementer

from genweb6.core import _


class IIcon(model.Schema):
    """Add open in new window field to link content
    """

    directives.order_after(icon_large='image')
    icon_large = schema.Bool(
        title=_(u"Icona gran?"),
        description=_(u"Si marqueu aquesta opció la icona es mostrarà més gros, com un fons."),
        required=False,
    )

    directives.order_after(icon='image')
    icon = schema.TextLine(
        title=_(u"Icona"),
        description=_(u"Icona que es mostrarà al costat del títol en cas de no afegir imatge, podeu trobar tots els identificadors en el <a href='https://icons.getbootstrap.com/' target='_blank'>següent enllaç</a>. Ex: bi-gear"),
        required=False,
    )


alsoProvides(IIcon, IFormFieldProvider)


@implementer(IIcon)
class Icon(object):
    adapts(IIcon)

    def __init__(self, context):
        self.context = context

    def _set_icon(self, value):
        self.context.icon = value

    def _get_icon(self):
        return getattr(self.context, 'icon', None)

    icon = property(_get_icon, _set_icon)

    def _set_icon_large(self, value):
        self.context.icon_large = value

    def _get_icon_large(self):
        return getattr(self.context, 'icon_large', None)

    icon_large = property(_get_icon_large, _set_icon_large)
