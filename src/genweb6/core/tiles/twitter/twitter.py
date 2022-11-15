# -*- coding: utf-8 -*-
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from zope import schema


class ITwitter(Schema):
    """ Twitter tile schema interface."""

    twitter_account = schema.TextLine(
        title=_(u"Twitter Account"),
        description=_(u"Name of the Twitter account used to shown the tweets"),
        default=u'la_UPC',
        required=True)


class Twitter(Tile):
    """The Twitter tile displays twitter widget of @la_UPC"""

    def __call__(self):
        return self.index()

    @property
    def twitter_account(self):
        """ return twitter_account of tile """
        return self.data.get('twitter_account', '')
