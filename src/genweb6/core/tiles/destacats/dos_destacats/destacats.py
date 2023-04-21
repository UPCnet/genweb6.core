# -*- coding: utf-8 -*-
from genweb6.core import _
from genweb6.core.utils import pref_lang
from genweb6.core.tiles.destacats.destacatbase import IDestacatsBase, DestacatsBase


class IDestacats(IDestacatsBase):
    """ Destacats schema """
    pass


class Destacats(DestacatsBase):
    """ Destacats tile displays a different kind of templates configured by subjects """

    def getNDestacats(self, limit):
        """ Returns 2 destacats object """

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

        return items
