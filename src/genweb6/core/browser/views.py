# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.contentprovider import interfaces
from zope.interface import implementer

from genweb6.core import GenwebMessageFactory as _
from genweb6.core.adapters import IImportant
from genweb6.core.interfaces import IHomePage
from genweb6.core.portlets.manage_portlets.manager import ISpanStorage
from genweb6.core.utils import json_response
from genweb6.core.utils import pref_lang
from genweb6.theme.theme.tinymce_templates.templates import templates


class GetDXDocumentText(BrowserView):

    def __call__(self):
        return self.context.text.output


class TemplateList(BrowserView):

    @json_response
    def __call__(self):
        results = templates.copy()

        pc = api.portal.get_tool(name='portal_catalog')
        portal = api.portal.get()
        plantilles = pc.searchResults(portal_type='Document',
                                      review_state=['published', 'intranet'],
                                      sort_on='getObjPositionInParent',
                                      path=portal.absolute_url_path() + '/plantilles')

        for plantilla in plantilles:
            results.append({'title': plantilla.Title,
                            'description': plantilla.Description,
                            'url': plantilla.getURL() + '/genweb.get.dxdocument.text'})

        return results


class gwToggleIsImportant(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        is_important = IImportant(context).is_important
        if is_important:
            IImportant(context).is_important = False
            confirm = _(u'L\'element s\'ha desmarcat com important')
        else:
            IImportant(context).is_important = True
            confirm = _(u'L\'element s\'ha marcat com important')

        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())


class HomePageBase(BrowserView):

    """
    Base methods for ease the extension of the genweb homePage view. Just
    define a new class inheriting from this one and redefine the basic
    grokkers like:

    Overriding the one in this module (homePage) with a more specific
    interface.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portlet_container = self.getPortletContainer()

    def getPortletContainer(self):
        context = aq_inner(self.context)
        container = context

        # Portlet container will be in the context,
        # Except in the portal root, when we look for an alternative
        if INavigationRoot.providedBy(self.context):
            pc = api.portal.get_tool(name='portal_catalog')
            # Add the use case of mixin types of IHomepages. The main ones of a
            # non PAM-enabled site and the possible inner ones.
            result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                      portal_type='Document',
                                      Language=pref_lang())
            if result:
                # Return the object without forcing a getObject()
                container = getattr(context, result[0].id, context)

        return container

    def renderProviderByName(self, provider_name):
        provider = queryMultiAdapter(
            (self.portlet_container, self.request, self),
            interfaces.IContentProvider, provider_name)

        provider.update()

        return provider.render()

    def getColValueForManager(self, manager):
        portletManager = getUtility(IPortletManager, manager)
        spanstorage = getMultiAdapter((self.portlet_container, portletManager), ISpanStorage)
        span = spanstorage.span
        if span:
            return span
        else:
            return '4'

    def have_portlets(self, manager_name, view=None):
        """Determine whether a column should be shown. The left column is called
        plone.leftcolumn; the right column is called plone.rightcolumn.
        """
        force_disable = self.request.get('disable_' + manager_name, None)
        if force_disable is not None:
            return not bool(force_disable)

        context = self.portlet_container
        if view is None:
            view = self

        manager = queryUtility(IPortletManager, name=manager_name)
        if manager is None:
            return False

        renderer = queryMultiAdapter((context, self.request, view, manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((context, self.request, self, manager), IPortletManagerRenderer)

        return renderer.visible

    def is_visible(self):
        """ This method lookup for the physical welcome page and checks if the
            user has the permission to view it. If it doesn't raises an
            unauthorized (login)
        """
        portal = api.portal.get()
        pc = api.portal.get_tool('portal_catalog')
        result = pc.unrestrictedSearchResults(object_provides=IHomePage.__identifier__,
                                              Language=pref_lang())
        if result:
            portal.restrictedTraverse(result[0].getPath())
            return True
        else:
            return False


@implementer(IHomePage)
class homePage(HomePageBase):
    """ This is the special view for the homepage containing support for the
        portlet managers provided by the package genweb.portlets.
        It's restrained to IGenwebTheme layer to prevent it will interfere with
        the one defined in the Genweb legacy theme (v3.5).
    """
    pass


@implementer(IHomePage)
class subHomePage(HomePageBase):
    """ This is the special view for the subhomepage containing support for the
        portlet managers provided by the package genweb.portlets.
        This is the PAM aware default LRF homepage view.
        It is also used in IFolderish (DX and AT) content for use in inner landing
        pages.
    """
    pass


@implementer(IHomePage)
class SubhomeView(HomePageBase):
    """ This is the special view for the subhomepage containing support for the
        portlet managers provided by the package genweb.portlets.
        This is the PAM aware default LRF homepage view.
        It is also used in IFolderish (DX and AT) content for use in inner landing
        pages.
    """
    pass
