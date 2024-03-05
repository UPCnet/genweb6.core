# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import queryUtility

from ftw.casauth.cas import strip_ticket
from genweb6.core.cas import PLUGIN_CAS
from genweb6.core.cas.controlpanel import ICASSettings

from time import time
from urllib import parse



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
        came_from = getattr(request, 'came_from', None)
        if came_from:
            url = '%s/login?idApp=%s&service=%s' % (plugin.cas_server_url, cas_settings.app_name, secureURL(strip_ticket(parse.urljoin(portal.absolute_url() + '/', came_from))))

        return '%s/login?idApp=%s&service=%s' % (plugin.cas_server_url, cas_settings.app_name, secureURL(strip_ticket(context.absolute_url())))
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
