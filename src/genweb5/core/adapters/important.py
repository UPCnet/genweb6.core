# -*- coding: utf-8 -*-
from plone.indexer import indexer
from plone.dexterity.interfaces import IDexterityContent
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface

from genweb5.core import GenwebMessageFactory as _

IMPORTANT_KEY = 'genweb.core.important'


class IImportant(Interface):
    """ An object which can be marked as important
    """

    is_important = schema.Bool(
        title=_(u"Tells if an object is marked as important"),
        default=False
    )


@implementer(IImportant)
class ImportantMarker(object):
    """ Adapts all non folderish AT objects (IBaseContent) to have
        the important attribute (Boolean) as an annotation.
        It is available through IImportant adapter.
    """
    adapts(Interface)

    def __init__(self, context):
        self.context = context

        annotations = IAnnotations(context)
        self._is_important = annotations.setdefault(IMPORTANT_KEY, False)

    def get_important(self):
        annotations = IAnnotations(self.context)
        self._is_important = annotations.setdefault(IMPORTANT_KEY, '')
        return self._is_important

    def set_important(self, value):
        annotations = IAnnotations(self.context)
        annotations[IMPORTANT_KEY] = value
        self.context.reindexObject(idxs=["is_important"])

    is_important = property(get_important, set_important)


@indexer(IDexterityContent)
def importantIndexer(context):
    """Create a catalogue indexer, registered as an adapter for DX content. """
    return IImportant(context).is_important
