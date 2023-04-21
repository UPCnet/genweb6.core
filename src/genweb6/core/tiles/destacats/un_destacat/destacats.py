# -*- coding: utf-8 -*-
from zope import schema
from genweb6.core import _
from genweb6.core.utils import create_simple_vocabulary
from genweb6.core.utils import pref_lang
from genweb6.core.tiles.destacats.destacatbase import IDestacatsBase, DestacatsBase


class IDestacats(IDestacatsBase):
    """ Destacats schema """

    heroTextPosition = schema.Choice(
        title=_(u"Text position"),
        description=_(u"Content's title position"),
        required=True,
        vocabulary=create_simple_vocabulary([
            ("centre", _(u"centre")),
            ("superior-esquerra", _(u"superior-esquerra")),
            ("superior-centre", _(u"superior-centre")),
            ("superior-dreta", _(u"superior-dreta")),
            ("inferior-esquerra", _(u"inferior-esquerra")),
            ("inferior-centre", _(u"inferior-centre")),
            ("inferior-dreta", _(u"inferior-dreta")),
            ("cercle-esquerra", _(u"cercle-esquerra")),
            ("cercle-centre", _(u"cercle-centre")),
            ("cercle-dreta", _(u"cercle-dreta")),
            ("invisible", _(u"invisible"))
        ]),
        default=u"centre",
    )


class Destacats(DestacatsBase):
    """ Destacats tile displays a different kind of templates configured by subjects """

    def getNDestacats(self, limit):
        """ Returns DestacatPrincipal object """

        params = {
            'review_state': ['published',],
            'Language': pref_lang(),
            'sort_on': ('effective'),
            'sort_order': 'reverse', 'sort_limit': limit,
            'portal_type': self.portal_types
            if self.portal_types else self.types_to_find, }

        if self.tags:
            params['Subject'] = self.tags

        results = self.catalog.searchResults(**params)
        items = self.filterObjects(results)

        if not items:
            return []

        return items[0]

    @property
    def heroTextPosition(self):
        return self.data.get('heroTextPosition', '')
