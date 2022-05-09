# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from zope.interface import implementer

from genweb6.core.content.banner.banner import IBanner
from genweb6.core.content.subhome.subhome import ISubhome
from genweb6.core.interfaces import IHomePageView


@implementer(IBanner)
class Banner(Item):
    pass


@implementer(IFolder)
class BannerContainer(Container):
    pass


@implementer(IBanner)
class Logo(Item):
    pass


@implementer(IFolder)
class LogoContainer(Container):
    pass


@implementer(ISubhome, IHomePageView)
class Subhome(Item):
    pass
