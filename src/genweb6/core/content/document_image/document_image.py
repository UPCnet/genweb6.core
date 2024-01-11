# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone.app.contenttypes import _
from plone.dexterity.content import Item
from plone.dexterity.interfaces import IDexteritySchema
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import implementer

from genweb6.core import _ as _GwC


class IDocumentImage(model.Schema, IDexteritySchema):

    image = namedfile.NamedBlobImage(
        title=_(u"Lead Image"),
        description=u"",
        required=True,
    )

    not_show_image = schema.Bool(
        title=_GwC(u"not_show_image"),
        description=u"",
        required=False,
    )

    image_caption = schema.TextLine(
        title=_(u"Lead Image Caption"),
        description=u"",
        required=False,
    )


@implementer(IDocumentImage)
class DocumentImage(Item):

    @property
    def b_icon_expr(self):
        return "file-earmark-richtext"


class View(BrowserView):
    pass
