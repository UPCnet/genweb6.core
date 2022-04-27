# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone.indexer import indexer
from plone.uuid.interfaces import IAttributeUUID
from plone.uuid.interfaces import IUUIDAware
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

try:
    from Acquisition import aq_base
except ImportError:
    def aq_base(v): return v  # soft-dependency on Zope2, fallback

ATTRIBUTE_NAME = '_gw.uuid'


class IGWUUID(Interface):
    """ The interface of the adapter for getting and setting the gwuuid """

    def get():
        """Return the UUID of the context"""

    def set(uuid):
        """Set the unique id of the context with the uuid value.
        """


def addAttributeUUID(obj, event):

    if not IObjectCopiedEvent.providedBy(event):
        if getattr(aq_base(obj), ATTRIBUTE_NAME, None):
            return  # defensive: keep existing UUID on non-copy create

    generator = queryUtility(IUUIDGenerator)
    if generator is None:
        return

    uuid = generator()
    if not uuid:
        return

    setattr(obj, ATTRIBUTE_NAME, uuid)


@implementer(IGWUUID)
class MutableAttributeUUID(object):
    adapts(IAttributeUUID)

    def __init__(self, context):
        self.context = context

    def get(self):
        return getattr(self.context, ATTRIBUTE_NAME, None)

    def set(self, uuid):
        uuid = str(uuid)
        setattr(self.context, ATTRIBUTE_NAME, uuid)


@indexer(IUUIDAware)
def gwUUID(context):
    return IGWUUID(context, None).get()


class GWUUIDView(BrowserView):

    def render(self):
        return IGWUUID(self.context).get()
