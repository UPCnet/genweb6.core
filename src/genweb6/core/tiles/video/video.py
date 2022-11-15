# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

from plone.app.uuid.utils import uuidToURL
from plone.app.vocabularies.catalog import CatalogSource
from plone.memoize.view import memoize
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from zope import schema
from zope.component.hooks import getSite

from genweb6.core import _
from genweb6.core.utils import create_simple_vocabulary

import re


def uuidToObject(uuid):
    """Given a UUID, attempt to return a content object. Will return
    None if the UUID can't be found. Raises Unauthorized if the current
    user is not allowed to access the object.
    """

    brain = uuidToCatalogBrainUnrestricted(uuid)
    if brain is None:
        return None

    return brain.getObject()


def uuidToCatalogBrainUnrestricted(uuid):
    """Given a UUID, attempt to return a catalog brain even when the object is
    not visible for the logged in user (e.g. during anonymous traversal)
    """

    site = getSite()
    if site is None:
        return None

    catalog = getToolByName(site, 'portal_catalog', None)
    if catalog is None:
        return None

    result = catalog.unrestrictedSearchResults(UID=uuid)
    if len(result) != 1:
        return None

    return result[0]


class ICustomVideo(Schema):
    """ Video schema. """

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title of the tile"),
        required=True,
    )

    option = schema.Choice(
        title=_(u"View as"),
        description=_(u"View as description"),
        required=True,
        vocabulary=create_simple_vocabulary([
            ("Fons clar", _(u"Fons clar")),
            ("Fons obscur", _(u"Fons obscur"))
        ])
    )

    link = schema.Choice(
        title=_(u"Enllaç intern per obrir en la mateixa finestra"),
        description=_(u"Fer el títol enllaçable cap a algun contingut de la web"),
        required=False,
        source=CatalogSource(),
    )

    external_links_open_new_window = schema.TextLine(
        title=_(u'Enllaç extern per obrir en finestra nova'),
        description=_(u"Fer el títol enllaçable cap a una altra web. NOTA: Si aquest camp està ple no es tindrà en compte l'enllaç intern"),
        required=False)

    content_uid = schema.TextLine(
        title=_(u"URL del vídeo"),
        description=_(u"Adreça web del canal on es troba el vídeo."),
        required=True,
    )


class CustomVideo(Tile):
    """ A tile that embeds video. """

    def isFonsClarConfigured(self):
        return self.option == _(u"Fons clar")

    def isFonsObscurConfigured(self):
        return self.option == _(u"Fons obscur")

    @property
    @memoize
    def get_video(self):
        """ Returns a video url """
        return self.data.get('content_uid')

    @property
    @memoize
    def is_video(self):
        MEDIA_REGEX = re.compile(r'.aac|.f4v|.flac|.m4v|.mkv|.mov|.mp3|.mp4|.oga|.ogg|.ogv|.webm', re.IGNORECASE)
        video_url = self.data.get('content_uid')
        return MEDIA_REGEX.search(video_url)

    def is_embed_video(self):
        # Able to embed youtube and vimeo videos for the moment
        video_url = self.data.get('content_uid')
        return "youtu.be" in video_url or "youtube.com" in video_url or "vimeo.com" in video_url or "zonavideo" in video_url

    @property
    def option(self):
        return self.data.get('option', '')

    @property
    def link(self):
        """ Return tile link"""
        if (self.data.get('external_links_open_new_window')):
            return self.data.get('external_links_open_new_window')
        else:
            UID = self.data.get('link', '')
            # intenta trobar la versio url textual, si no la troba fara resolveuid
            link = uuidToURL(UID)
            if not link:
                link = None
            return link

    @property
    def external_links_open_new_window(self):
        """ Return tile external link"""
        return self.data.get('external_links_open_new_window')

    def open_link_in(self):
        if self.data.get('external_links_open_new_window'):
            return '_blank'
        else:
            return '_self'
