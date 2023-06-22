# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import queryUtility

from genweb6.core.cas.controlpanel import ICASSettings
from genweb6.core.cas import PLUGIN_CAS

from time import time

def secureURL(url):
    """ Secures an URL (given http, returns https) """
    if url[:5] == 'http:' or url[:5] == 'HTTP:':
        return '%s%s' % ('https:', url[5:])
    else:
        return url


def login_URL(context, request):
    """ The contructor of the correct CAS URL, otherwise the return URL
        will be the login form once authenticated.
    """
    # We suppose that a configured plugin is in place and its called CASGW
    portal = getToolByName(context, "portal_url").getPortalObject()
    plugin = getattr(portal.acl_users, PLUGIN_CAS, None)

    if plugin:
        cas_settings = getCASSettings()
        current_url = getMultiAdapter((context, request), name=u'plone_context_state').current_page_url()

        camefrom = getattr(request, 'came_from', None)
        if camefrom:
            catalog = api.portal.get_tool("portal_catalog")
            results = catalog.unrestrictedSearchResults(path=camefrom)
            if results:
                return '%s/login?idApp=%s&service=%s' % (plugin.cas_server_url, cas_settings.app_name, secureURL(results[0]._unrestrictedGetObject().absolute_url()))

        return '%s/login?idApp=%s&service=%s' % (plugin.cas_server_url, cas_settings.app_name, secureURL(context.absolute_url()))
    else:
        return '%s/login_form' % portal.absolute_url()


def logout(context, request):
    portal = getToolByName(context, "portal_url").getPortalObject()
    plugin = getattr(portal.acl_users, PLUGIN_CAS, None)

    if plugin:
        mt = getToolByName(context, 'portal_membership')
        mt.logoutUser(REQUEST=request)
        IStatusMessage(request).addStatusMessage(_('heading_signed_out'), type='info')

        logout_url = '%s/logout?url=%s' % (plugin.cas_server_url, portal.absolute_url())

        return request.RESPONSE.redirect(logout_url)

    else:
        return '%s/logout' % portal.absolute_url()

@ram.cache(lambda *args: time() // (24 * 60 * 60))
def getCASSettings():
    registry = queryUtility(IRegistry)
    return registry.forInterface(ICASSettings)
