# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime

from plone import api
from plone.app.uuid.utils import uuidToURL
from plone.app.vocabularies.catalog import CatalogSource as CatalogSourceBase
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from zope import schema
from zope.i18nmessageid import MessageFactory

from genweb6.core import _
from genweb6.core.utils import create_simple_vocabulary
from genweb6.core.utils import pref_lang

import re


class CatalogSource(CatalogSourceBase):
    """ExistingContentTile specific catalog source to allow targeted widget
    """
    def __contains__(self, value):
        return True  # Always contains to allow lazy handling of removed objs


PLMF = MessageFactory('plonelocales')
_PMF = MessageFactory('plone')


class ITresDestacats(Schema):
    """ Destacats schema """

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title of the tile"),
        required=True
    )

    tags = schema.List(
        title=_(u"Tags field"),
        description=_(u"Tags field description"),
        required=False,
        value_type=schema.Choice(
            vocabulary=u'plone.app.vocabularies.Keywords')
    )

    portal_types = schema.List(
        title=_(u"Content type"),
        description=_(u"The content type to check for."),
        required=False,
        value_type=schema.Choice(
            vocabulary=create_simple_vocabulary([
                # ("Link", _PMF(u"Link")),
                ("Event", _PMF(u"Event")),
                # ("Image", _PMF(u"Image")),
                ("News Item", _PMF(u"News Item")),
                ("genweb.upc.documentimage", _(u"Document Image"))
            ])
        )
    )

class TresDestacats(Tile):
    """ Destacats tile displays a different kind of templates configured by subjects """

    def __call__(self):
        return self.index()

    def get3Destacats(self):
        """ Returns 3Destacats objects """
        catalog = api.portal.get_tool(name='portal_catalog')
        if self.portal_types == [u'Image']:
            if self.tags:
                subjects = [t for t in self.tags]
                results = catalog(Subject=subjects,
                                  portal_type=('Image'),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=3)
            else:
                results = catalog(portal_type=('Image'),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=3)
        else:
            if not self.tags and not self.portal_types:
                results = catalog(review_state=['published', 'private'],
                                  Language=pref_lang(),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=3)
            elif self.tags and not self.portal_types:
                subjects = [t for t in self.tags]
                results = catalog(Subject=subjects,
                                  review_state=['published', 'private'],
                                  Language=pref_lang(),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=3)
            elif not self.tags and self.portal_types:
                results = catalog(portal_type=self.portal_types,
                                  review_state=['published', 'private'],
                                  Language=pref_lang(),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=3)
            else:
                subjects = [t for t in self.tags]
                results = catalog(portal_type=self.portal_types,
                                  Subject=subjects,
                                  review_state=['published', 'private'],
                                  Language=pref_lang(),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=3)

        items = self.filterObjects(results)
        return items

    def filterObjects(self, results):
        """ Filter objects returned by type """
        if len(results) > 0:
            items = []
            for result in results:
                obj = result.getObject()

                obj_type = obj.Type()
                if obj_type == 'Event':
                    info = {
                        'url': result.getURL(),
                        'imatge': obj.image,
                        'img_setted': obj.image is not None,
                        'open_link_in_new_window': '_self',
                        'class': "",
                        'title': obj.title,
                        'description': obj.description,
                        }
                elif obj_type in ['News Item', 'Document Image']:
                    data_efectiva = DateTime.strftime(obj.effective(), '%d/%m/%Y')
                    info = {
                        'url': result.getURL(),
                        'imatge': obj.image,
                        'img_setted': obj.image is not None,
                        'open_link_in_new_window': '_self',
                        'class': "",
                        'title': obj.title,
                        'description': obj.description,
                        'data_efectiva': data_efectiva,
                        }
                elif obj_type == 'Link':
                    upctv = False
                    youtube = False
                    video_id = 0
                    url_video = None
                    video = ''
                    YOUTUBE_REGEX = re.compile(r'youtube.*?(?:v=|embed\/)([\w\d-]+)', re.IGNORECASE)
                    data_efectiva = DateTime.strftime(obj.effective(), '%d/%m/%Y')
                    if obj.open_link_in_new_window:
                        open_link = '_blank'
                    else:
                        open_link = '_self'

                    url_video = obj.remoteUrl
                    is_youtube_video = YOUTUBE_REGEX.search(url_video)
                    if is_youtube_video:
                        youtube = True
                        isVideo = True
                    elif url_video.find('tv.upc') >= 0:
                        upctv = True
                        isVideo = True
                    else:
                        isVideo = False

                    if isVideo:
                        video = 'hotnews-video'
                        # per tal que hi pugui haver varis videos generem un id aleatori
                        video_id = 'video-' + obj.id

                    info = {
                        'url': result.getURL(),
                        'imatge': None,
                        'open_link_in_new_window': open_link,
                        'class': 'link-banner ' + video,
                        'title': obj.title,
                        'description': obj.description,
                        'is_video': isVideo,
                        'url_video': url_video,
                        'youtube': youtube,
                        'upctv': upctv,
                        'video_id': video_id,
                        'link_extern_pdf': obj.remoteUrl,
                        'data_efectiva': data_efectiva,
                        }
                elif obj_type == 'Image':
                    info = {
                        'url': result.getURL(),
                        'imatge': obj.image,
                        'img_setted': obj.image is not None,
                        'open_link_in_new_window': '_self',
                        'class': "",
                        'title': obj.title,
                        'description': obj.description,
                        }
                else:
                    info = {
                        'url': result.getURL(),
                        'imatge': None,
                        'img_setted': True,
                        'open_link_in_new_window': '_self',
                        'class': "",
                        'title': obj.title,
                        'description': obj.description,
                        }
                items.append(info)
        else:
            items = None
        return items

    @property
    def title(self):
        """ Return tile title"""
        return self.data.get('title', '')

    @property
    def tags(self):
        return self.data.get('tags', '')

    @property
    def portal_types(self):
        return self.data.get('portal_types', '')
