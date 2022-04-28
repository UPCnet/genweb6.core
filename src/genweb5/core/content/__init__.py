# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from zope.interface import implementer

from genweb5.core.content.banner import IBanner


@implementer(IBanner)
class Banner(Item):
    pass


@implementer(IFolder)
class BannerContainer(Container):
    pass
