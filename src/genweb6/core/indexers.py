# -*- coding: utf-8 -*-
from plone.app.contenttypes.indexers import SearchableText
from plone.app.contenttypes.indexers import _unicode_save_string_concat
from plone.app.contenttypes.interfaces import INewsItem
from plone.indexer import indexer

from genweb6.core.content.document_image.document_image import IDocumentImage


@indexer(INewsItem)
def newsImageFile(context):
    """Create a catalogue indexer, registered as an adapter, which can
    populate the ``context.filename`` value and index it.
    """
    return context.image.filename


@indexer(IDocumentImage)
def SearchableText_document_image(obj):
    return _unicode_save_string_concat(SearchableText(obj))