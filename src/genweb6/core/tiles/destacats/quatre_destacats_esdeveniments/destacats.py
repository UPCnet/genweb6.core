# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime

from plone import api
from plone.app.vocabularies.catalog import CatalogSource as CatalogSourceBase
from plone.app.uuid.utils import uuidToURL
from plone.supermodel.model import Schema
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _
from genweb6.core.tiles.destacats.destacatbase import DestacatsBase
from genweb6.core.tiles.destacats.destacatbase import IDestacatsBase
from genweb6.core.utils import pref_lang

PLMF = MessageFactory('plonelocales')


countVocabulary = SimpleVocabulary.fromValues(range(1, 17))
columnsVocabulary = SimpleVocabulary.fromValues(range(1, 5))


class CatalogSource(CatalogSourceBase):
    """ExistingContentTile specific catalog source to allow targeted widget
    """

    def __contains__(self, value):
        return True  # Always contains to allow lazy handling of removed objs


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

    count = schema.Choice(
        title=_(u"Numero de esdeveniments a mostrar"),
        description=_(u"Maxim numero de esdeveniments a mostrar (d'1 a 16)"),
        required=True,
        vocabulary=countVocabulary,
        default=4
    )

    columns = schema.Choice(
        title=_(u"Numero de columnes"),
        description=_(u"Numero de columnes (d'1 a 4)"),
        required=True,
        vocabulary=columnsVocabulary,
        default=4
    )

    link = schema.Choice(
        title=_(u"Enllaç per les tiles de 5 Destacats"),
        description=_(u"Afegeix un botó a l'enllaç afegit en aquest camp"),
        required=False,
        source=CatalogSource(),
    )

    link_title = schema.TextLine(
        title=_(u"Títol per l'enllaç"),
        description=_(u"Apareixerà a la tile seleccionada"),
        required=False)


class Destacats(DestacatsBase):
    """ Destacats tile displays a different kind of templates configured by subjects """

    def getNDestacats(self, limit):
        """ Returns 4Destacats objects """
        events = []
        ts = api.portal.get_tool(name='translation_service')

        params = {
            'review_state': ['published',],
            'Language': pref_lang(),
            'end': {'query': DateTime(), 'range': 'min'},
            'sort_on': ('effective'),
            'sort_order': 'reverse',
            'sort_limit': limit,
            'portal_type': ('Event') }

        if self.tags:
            params['Subject'] = self.tags

        results = self.catalog.searchResults(**params)

        for event in results:
            obj = event.getObject()

            info = {'url': event.getURL(),
                    'firstday': obj.start.day,
                    'firstmonth': PLMF(ts.month_msgid(obj.start.month)),
                    'abbrfirstmonth': PLMF(ts.month_msgid(obj.start.month)),
                    'lastday': obj.end.day,
                    'lastmonth': PLMF(ts.month_msgid(obj.end.month)),
                    'abbrlastmonth': PLMF(ts.month_msgid(obj.end.month)),
                    'connector': ' to ' if pref_lang() == 'en' else ' a ',
                    'title': obj.title,
                    'image': obj.image,
                    'peu': obj.title,
                    'img_setted': obj.image is None,
                    }

            events.append(info)

        return events

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

    def get_col(self):
        columns = self.data.get('columns', '')
        if columns == 1:
            return 'col-md-12 col-sm-12 col-xs-12'
        elif columns == 2:
            return 'col-md-6 col-sm-6 col-xs-12'
        elif columns == 3:
            return 'col-md-4 col-sm-6 col-xs-12'
        else:
            return 'col-md-3 col-sm-6 col-xs-12'

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
    def count(self):
        """ Return tile count"""
        return self.data.get('count', '')

    @property
    def link_title(self):
        """ Return tile link_title"""
        return self.data.get('link_title', '')