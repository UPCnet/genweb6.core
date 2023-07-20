# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import INewsItem
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer


@indexer(INewsItem)
def newsImageFile(context):
    """Create a catalogue indexer, registered as an adapter, which can
    populate the ``context.filename`` value and index it.
    """
    return context.image.filename
