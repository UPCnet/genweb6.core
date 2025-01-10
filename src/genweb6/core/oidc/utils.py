# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from genweb6.core.oidc import PLUGIN_OIDC
from time import time
from urllib import parse



def secureURL(url):
    """ Secures an URL (given http, returns https) """
    if url[:5] == 'http:' or url[:5] == 'HTTP:':
        return '%s%s' % ('https:', url[5:])
    else:
        return url


def login_URL(context, request):
    """ The contructor of the correct OIDC URL, otherwise the return URL
        will be the login form once authenticated.
    """
    # We suppose that a configured plugin is in place and its called oidc
    portal = getToolByName(context, "portal_url").getPortalObject()
    plugin = getattr(portal.acl_users, PLUGIN_OIDC, None)

    if plugin:
        #/SITE_ID/acl_users/oidc/login
        came_from = getattr(request, 'came_from', None)
        if came_from:
            return f'/{portal.id}/acl_users/oidc/login/?came_from={came_from}'

        return f'/{portal.id}/acl_users/oidc/login'
    else:
        return '%s/login_form' % portal.absolute_url()


def logout(context, request):
    portal = getToolByName(context, "portal_url").getPortalObject()
    plugin = getattr(portal.acl_users, PLUGIN_OIDC, None)

    if plugin:
        mt = getToolByName(context, 'portal_membership')
        mt.logoutUser(REQUEST=request)
        IStatusMessage(request).addStatusMessage(_('heading_signed_out'), type='info')

        logout_url = f'/{portal.id}/acl_users/oidc/logout'

        return request.RESPONSE.redirect(logout_url)

    else:
        return '%s/logout' % portal.absolute_url()