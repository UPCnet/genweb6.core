# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from plone.supermodel.model import Schema
from plone.tiles.tile import Tile
from zope import schema
from zope.i18nmessageid import MessageFactory

from genweb6.core import _
from genweb6.core.utils import create_simple_vocabulary


from abc import ABC, abstractmethod


PLMF = MessageFactory('plonelocales')
_PMF = MessageFactory('plone')


class IDestacatsBase(Schema):
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
                ("Event", _PMF(u"Event")),
                ("News Item", _PMF(u"News Item")),
                ("genweb.upc.documentimage", _(u"Document Image"))
            ])
        )
    )



class DestacatsBase(Tile, ABC):
    """ Destacats tile displays a different kind of templates configured by subjects """

    def __call__(self):
        return self.index()

    def isDestacatsConfigured(self):
        return True

    @abstractmethod
    def getNDestacats(self, limit):
        """ Returns N Destacats objects """
        pass

    def filterObjects(self, results):
        """ Filter objects returned by type """
        if not results:
            return []
        
        items = []
        for result in results:
            obj = result.getObject()
            obj_type = obj.Type()

            info = {
                'url': result.getURL(),
                'image': obj.image,
                'img_setted': obj.image is not None,
                'open_link_in_new_window': '_self',
                'class': "",
                'title': obj.title,
                'description': obj.description,
            }

            if obj_type in ['News Item', 'Document Image']:
                data_efectiva = DateTime.strftime(obj.effective(), '%d/%m/%Y')
                info['data_efectiva'] = data_efectiva

            items.append(info)
        
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