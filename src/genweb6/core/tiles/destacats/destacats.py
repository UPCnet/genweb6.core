# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from DateTime.DateTime import DateTime
from Products.CMFCore.permissions import ModifyPortalContent

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


class IDestacats(Schema):
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
                ("Link", _PMF(u"Link")),
                ("Event", _PMF(u"Event")),
                ("Image", _PMF(u"Image")),
                ("News Item", _PMF(u"News Item")),
                ("genweb.upc.documentimage", _(u"Document Image"))
            ])
        )
    )

    option = schema.Choice(
        title=_(u"View as"),
        description=_(u"View as description"),
        required=False,
        vocabulary=create_simple_vocabulary([
            ("1 Destacat Principal", _(u"1 Destacat Principal")),
            ("3 Destacats", _(u"3 Destacats")),
            ("4 Destacats Esdeveniments", _(u"4 Destacats Esdeveniments")),
            ("5 Destacats Esquerra", _(u"5 Destacats Esquerra")),
            ("5 Destacats Dreta", _(u"5 Destacats Dreta"))
            ])
        )

    link = schema.Choice(
        title=_(u"Enllaç per les tiles de 4 i 5 Destacats"),
        description=_(u"El contingut d'aquest camp només aplica en les tiles esmentades"),
        required=False,
        source=CatalogSource(),
        )

    link_title = schema.TextLine(
        title=_(u"Títol per l'enllaç"),
        description=_(u"Apareixerà a la tile seleccionada"),
        required=False)


class Destacats(Tile):
    """ Destacats tile displays a different kind of templates configured by subjects """

    def __call__(self):
        return self.index()

    def is1DestacatPrincipalConfigured(self):
        return self.option == _(u'1 Destacat Principal')

    def is3DestacatsConfigured(self):
        return self.option == _(u'3 Destacats')

    def is4DestacatsEsdevenimentsConfigured(self):
        return self.option == _(u'4 Destacats Esdeveniments')

    def is5DestacatsEsquerraConfigured(self):
        return self.option == _(u'5 Destacats Esquerra')

    def is5DestacatsDretaConfigured(self):
        return self.option == _(u'5 Destacats Dreta')

    def get1DestacatPrincipal(self):
        """ Returns DestacatPrincipal object """
        catalog = api.portal.get_tool(name='portal_catalog')
        if not self.tags and not self.portal_types:
            results = catalog(review_state=['published', 'private'],
                              Language=pref_lang(),
                              sort_on=('effective'),
                              sort_order='reverse',
                              sort_limit=1)
        elif self.tags and not self.portal_types:
            subjects = [t for t in self.tags]
            results = catalog(Subject=subjects,
                              review_state=['published', 'private'],
                              Language=pref_lang(),
                              sort_on=('effective'),
                              sort_order='reverse',
                              sort_limit=1)
        elif not self.tags and self.portal_types:
            if self.portal_types == [u'Image']:
                results = catalog(portal_type=self.portal_types,
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=1)
            else:
                results = catalog(portal_type=self.portal_types,
                                  review_state=['published', 'private'],
                                  Language=pref_lang(),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=1)
        else:
            subjects = [t for t in self.tags]
            if self.portal_types in [u'Image']:
                results = catalog(portal_type=self.portal_types,
                                  Subject=subjects,
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=1)
            else:
                results = catalog(portal_type=self.portal_types,
                                  Subject=subjects,
                                  review_state=['published', 'private'],
                                  Language=pref_lang(),
                                  sort_on=('effective'),
                                  sort_order='reverse',
                                  sort_limit=1)

        return self.filterObjects(results)[0] if len(results) > 0 else None

    def get3Destacats(self):
        """ Returns 3Destacats objects """
        catalog = api.portal.get_tool(name='portal_catalog')
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

    def dateType(self, event):
        startday = event['firstday']
        endday = event['lastday']
        startmonth = event['firstmonth']
        endmonth = event['lastmonth']

        if startmonth != endmonth:
            return 'difday_difmonth'
        elif startday != endday:
            return 'difday_samemonth'
        else:
            return 'sameday_samemonth'

    def get4DestacatsEsdeveniments(self):
        """ Returns 4Destacats objects """
        catalog = api.portal.get_tool(name='portal_catalog')
        events = []
        ts = api.portal.get_tool(name='translation_service')
        # no apliquen els tipus, sempre seran esdeveniments
        if not self.tags:
            results = catalog(portal_type=('Event'),
                              review_state=['published', 'private'],
                              Language=pref_lang(),
                              end={'query': DateTime(), 'range': 'min'},
                              sort_on=('start'),
                              sort_order='ascending',
                              sort_limit=4)
        else:
            subjects = [t for t in self.tags]
            results = catalog(Subject=subjects,
                              portal_type=('Event'),
                              review_state=['published', 'private'],
                              Language=pref_lang(),
                              end={'query': DateTime(), 'range': 'min'},
                              sort_on=('start'),
                              sort_order='ascending',
                              sort_limit=4)
        for event in results:
            obj = event.getObject()
            categories = ""
            tags = [s for s in obj.subject if not s.startswith("#") and not s.startswith("@")]
            for t in tags:
                categories += t.encode('utf-8') if isinstance(t, unicode) else t + ' '
            info = {'url': event.getURL(),
                    'firstday': obj.start.day,
                    'firstmonth': PLMF(ts.month_msgid(obj.start.month)),
                    'abbrfirstmonth': PLMF(ts.month_msgid(obj.start.month)),
                    'lastday': obj.end.day,
                    'lastmonth': PLMF(ts.month_msgid(obj.end.month)),
                    'abbrlastmonth': PLMF(ts.month_msgid(obj.end.month)),
                    'connector': ' to ' if pref_lang() == 'en' else ' a ',
                    'title': obj.title,
                    'category': categories,
                    'imatge': obj.image,
                    'peu': obj.title,
                    'img_setted': obj.image is None,
                    }
            events.append(info)

        return events

    def area_gran(self):
        self.destacats = self.getNDestacats(limit=1)
        try:
            return self.destacats[0]
        except:
            return None

    def all4news(self):
        self.destacats = self.getNDestacats(limit=5)
        try:
            if len(self.destacats) >= 5:
                return self.destacats[1:5]
            else:
                return self.destacats[1:]
        except:
            return None

    def getNDestacats(self, limit):
        """ Returns N Destacats objects """
        catalog = api.portal.get_tool(name='portal_catalog')

        # busquem la mes recent que tingui tag 'gran' mes el tag definit a la tile
        tags = self.tags[:]
        tags.append('#gran')
        subjects = [t for t in self.tags]

        review_states = ['published', 'private']

        gran_dict = {'Subject': {'query': subjects, 'operator': 'and'},
                     'Language': pref_lang(),
                     'sort_on': ('effective'),
                     'sort_order': 'reverse',
                     'sort_limit': 1}

        if not self.portal_types:
            gran_dict.update({'review_state': review_states})
            item_gran = catalog(gran_dict)
        else:
            gran_dict.update({'portal_type': self.portal_types})
            if self.portal_types == ['Image']:
                item_gran = catalog(gran_dict)
            else:
                gran_dict.update({'review_state': review_states})
                item_gran = catalog(gran_dict)

        # busquem les N mes recent que tinguin el tag definit a la tile
        normal_dict = {'Language': pref_lang(),
                       'sort_on': ('effective'),
                       'sort_order': 'reverse',
                       'sort_limit': limit}

        if not self.tags and not self.portal_types:
            normal_dict.update({'review_state': review_states})
            items_normals = catalog(normal_dict)
        elif self.tags and not self.portal_types:
            normal_dict.update({'review_state': review_states})
            normal_dict.update({'Subject': [t for t in self.tags]})
            items_normals = catalog(normal_dict)
        elif not self.tags and self.portal_types:
            normal_dict.update({'portal_type': self.portal_types})
            if self.portal_types == ['Image']:
                items_normals = catalog(normal_dict)
            else:
                normal_dict.update({'review_state': review_states})
                items_normals = catalog(normal_dict)
        else:
            normal_dict.update({'Subject': [t for t in self.tags]})
            normal_dict.update({'portal_type': self.portal_types})
            if self.portal_types == ['Image']:
                items_normals = catalog(normal_dict)
            else:
                normal_dict.update({'review_state': review_states})
                items_normals = catalog(normal_dict)

        items = self.filterObjects(items_normals)
        # si n'hi ha una de gran:
        #   si es a la llista de 5 la treiem i la posem primera
        #   si no es a la llista, treiem la ultima de la llista i posem la gran en primera posicio
        if item_gran:
            item_gran = self.filterObjects(item_gran)[0]
            if item_gran in items:
                items.remove(item_gran)
            else:
                items = items[0:int(limit)]
            items.insert(0, item_gran)

        index = 0
        for i in items:
            compose_class = 'area' + str(index)
            key_class = {'class': compose_class}
            i.update(key_class)
            index += 1

        return items

    def filterObjects(self, results):
        """ Filter objects returned by type """
        if len(results) > 0:
            items = []
            for result in results:
                obj = result.getObject()
                categories = ""
                tags = [s for s in obj.subject]
                for t in tags:
                    if not t.startswith("#") and not t.startswith("@"):
                        categories += t + ' '

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
                        'categories': categories,
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
                        'categories': categories,
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
                        'class': video,
                        'title': obj.title,
                        'description': obj.description,
                        'categories': categories,
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
                        'categories': categories,
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
                        'categories': categories,
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

    @property
    def option(self):
        return self.data.get('option', '')

    @property
    def link(self):
        """ Return tile link"""
        UID = self.data.get('link', '')
        # intenta trobar la versio url textual, si no la troba fara resolveuid
        link = uuidToURL(UID)
        if not link:
            link = 'resolveuid/' + str(UID)
        return link

    @property
    def link_title(self):
        """ Return tile link_title"""
        return self.data.get('link_title', '')
