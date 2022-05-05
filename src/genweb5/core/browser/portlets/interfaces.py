# -*- coding: utf-8 -*-
from zope.interface import Interface
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn


class IGenwebPortlets(Interface):
    """
        A layer specific to this product. Is registered using browserlayer.xml
    """


class IHomepagePortletManager(IPortletManager, IColumn):
    """
        Superclass used by our adapter
        The IColumn bit means that we can add all the portlets available to
        the right-hand and left-hand column portlet managers
    """


class IPortletsHomepage(IHomepagePortletManager):
    """
        For the portlet manager above the content area.
    """
