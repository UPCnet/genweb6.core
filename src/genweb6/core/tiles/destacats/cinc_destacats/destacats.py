# -*- coding: utf-8 -*-
from zope import schema
from plone.app.vocabularies.catalog import CatalogSource as CatalogSourceBase
from plone.app.uuid.utils import uuidToURL
from genweb6.core import _
from genweb6.core.utils import create_simple_vocabulary
from genweb6.core.utils import pref_lang
from genweb6.core.tiles.destacats.destacatbase import IDestacatsBase, DestacatsBase


class CatalogSource(CatalogSourceBase):
    """ExistingContentTile specific catalog source to allow targeted widget
    """

    def __contains__(self, value):
        return True  # Always contains to allow lazy handling of removed objs


class IDestacats(IDestacatsBase):
    """ Destacats schema """

    imatgeGranPosition = schema.Choice(
        title=_(u"Big image"),
        description=_(u"Big image position"),
        required=True,
        vocabulary=create_simple_vocabulary([
            ("imatge-gran-esquerra", _(u"imatge-gran-esquerra")),
            ("imatge-gran-dreta", _(u"imatge-gran-dreta")),
        ]),
        default=u"imatge-gran-esquerra",
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
        """ Returns N Destacats objects """
        subjects = self.tags + ['@gran']

        params = {
            'Subject': {'query': subjects, 'operator': 'and'},
            'Language': pref_lang(),
            'sort_on': ('effective'),
            'sort_order': 'reverse', 'sort_limit': 1,
            'review_state': ['published',],
            'portal_type': self.portal_types
            if self.portal_types else self.types_to_find}

        # Find Big item
        item_gran = self.catalog.searchResults(**params)
        next_limit = limit if not item_gran else limit + 1

        params['sort_limit'] = next_limit
        subjects.remove('@gran')
        if subjects:
            params['Subject'] = subjects
        else:
            params.pop('Subject', None)

        # Find N Destacats
        items_normals = self.catalog.searchResults(**params)
        items = self.filterObjects(items_normals)

        if item_gran:
            item_gran = self.filterObjects(item_gran)[0]
            if item_gran in items:
                items.remove(item_gran)
            else:
                items = items[0:int(limit)]
            items.insert(0, item_gran)

        if not items:
            return []

        for index, item in enumerate(items):
            if item_gran and index == 0:
                continue
            compose_class = 'area' + str(index)
            key_class = {'class': compose_class}
            item.update(key_class)

        return items[:5]

    @property
    def imatgeGranPosition(self):
        return self.data.get('imatgeGranPosition', '')

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
