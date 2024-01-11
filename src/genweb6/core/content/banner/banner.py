# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.dexterity.interfaces import IDexteritySchema
from plone.indexer.decorator import indexer
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema

from genweb6.core import _


class IBanner(model.Schema, IDexteritySchema):
    """ A site banner.
    """

    image = NamedBlobImage(
        title=_(u"Picture"),
        description=_(u"Please upload an image"),
        required=False,
    )

    remoteUrl = schema.TextLine(
        title=_(u"url"),
        description=_(u"URL to open"),
        required=False,
    )


@indexer(IBanner)
def getRemoteUrl(obj):
    if obj.remoteUrl:
        return replace_link_variables_by_paths(obj, obj.remoteUrl)


class View(BrowserView):
    pass
