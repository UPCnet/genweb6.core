# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.viewlets.common import ManagePortletsFallbackViewlet
from plone.app.portlets.browser.editmanager import ContextualEditPortletManagerRenderer
from plone.app.portlets.browser.interfaces import IManageContextualPortletsView
from plone.app.portlets.browser.manage import ManageContextualPortlets
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletManager
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from genweb6.core.portlets.manage_portlets.interfaces import IHomepagePortletManager
from genweb6.core.browser.viewlets import viewletBase
from genweb6.core.interfaces import IHomePage
from genweb6.core.utils import pref_lang

SPAN_KEY = 'genweb.portlets.span.'


class GenwebPortletRenderer(ColumnPortletManagerRenderer):
    """
    A renderer for the Genweb portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IHomepagePortletManager)
    template = ViewPageTemplateFile('templates/renderer.pt')


class gwContextualEditPortletManagerRenderer(ContextualEditPortletManagerRenderer):
    """Render a portlet manager in edit mode for contextual portlets"""
    adapts(Interface, IDefaultBrowserLayer, IManageContextualPortletsView, IHomepagePortletManager)

    template = ViewPageTemplateFile('templates/edit-manager-contextual.pt')


class gwManageContextualPortlets(ManageContextualPortlets):
    """ Define our very own view for manage portlets """

    def getValue(self, manager):
        portletManager = getUtility(IPortletManager, name=manager)
        spanstorage = getMultiAdapter((self.context, portletManager), ISpanStorage)
        return spanstorage.span

    @memoize_contextless
    def getTitle(self):
        return self.context.title

    @memoize_contextless
    def paginaPrincipal(self):
        return IHomePage.providedBy(self.context)


class ISpanStorage(IAttributeAnnotatable):
    """Marker persistent used to store span number for portlet managers"""

    span = schema.TextLine(title=u"Number of spans for this portletManager.")


@implementer(ISpanStorage)
class SpanStorage(object):
    """Multiadapter that adapts any context and IPortletManager to provide ISpanStorage"""
    adapts(Interface, IPortletManager)

    def __init__(self, context, manager):
        self.context = context
        self.manager = manager
        self.key_id = SPAN_KEY + manager.__name__

        annotations = IAnnotations(context)
        self._span = annotations.setdefault(self.key_id, '')

    def get_span(self):
        annotations = IAnnotations(self.context)
        self._span = annotations.setdefault(self.key_id, '')
        return self._span

    def set_span(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(self.key_id, value)
        annotations[self.key_id] = value

    span = property(get_span, set_span)


class setPortletHomeManagerSpan(BrowserView):
    """ View that stores the span number assigned to this portletManager for
        this context.
    """

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

    def __call__(self):
        manager = self.request.form['manager']
        span = self.request.form['span']
        portlet_container = self.getPortletContainer()
        portletManager = getUtility(IPortletManager, manager)
        spanstorage = getMultiAdapter((portlet_container, portletManager), ISpanStorage)
        spanstorage.span = span
        self.request.RESPONSE.setStatus('200')
        self.request.RESPONSE.setHeader('Content-type', 'application/json')
        return '{"status": "Saved!"}'


class gwManagePortletsFallbackViewletMixin(object):
    """ The override for the manage_portlets_fallback viewlet for IPloneSiteRoot
    """

    def getPortletContainerPath(self):
        context = aq_inner(self.context)
        lang = self.context.language
        if not lang:
            lang = 'ca'

        container_url = context.absolute_url()

        # Portlet container will be in the context,
        # Except in the portal root, when we look for an alternative
        if INavigationRoot.providedBy(self.context):
            pc = api.portal.get_tool(name='portal_catalog')
            # Add the use case of mixin types of IHomepages. The main ones of a
            # non PAM-enabled site and the possible inner ones.
            result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                      portal_type='Document',
                                      Language=lang)

            if result:
                # Return the object without forcing a getObject()
                container_url = result[0].getURL()

        return container_url

    def managePortletsURL(self):
        return "%s/%s" % (self.getPortletContainerPath(), '@@manage-homeportlets')

    def manageSubhomePortletsURL(self):
        return "%s/%s" % (self.getPortletContainerPath(), '@@manage-subhome')

    def canManageGrid(self):
        secman = getSecurityManager()
        user = secman.getUser()
        context = self.context
        roles = user.getRolesInContext(context)
        if 'Author' in roles or 'Owner' in roles or 'Editor' in roles or 'Contributor' in roles or 'Manager' in roles or 'Reviewer' in roles or 'Site Administrator' in roles or 'WebMaster' in roles:
            return True
        # Reader or Authenticated or Member
        else:
            return False


class gwManagePortletsFallbackViewletForIHomePage(gwManagePortletsFallbackViewletMixin, ManagePortletsFallbackViewlet, viewletBase):
    """ The override for the manage_portlets_fallback viewlet for ISubhome
    """

    index = ViewPageTemplateFile("templates/manage_portlets_fallback_homepage.pt")

    def available(self):
        secman = getSecurityManager()
        if secman.checkPermission('Genweb: Webmaster Users', self.context):
            if self.request.steps[-1] in ['document_view', 'homepage']:
                return True
        return False


class gwManagePortletsFallbackViewletForISubhome(gwManagePortletsFallbackViewletMixin, ManagePortletsFallbackViewlet, viewletBase):
    """ The override for the manage_portlets_fallback viewlet for ISubhome
    """

    index = ViewPageTemplateFile("templates/manage_portlets_fallback_subhome.pt")

    def available(self):
        secman = getSecurityManager()
        if secman.checkPermission('Genweb: Webmaster Users', self.context):
            if self.request.steps[-1] in ['subhome_view']:
                return True
        return False
