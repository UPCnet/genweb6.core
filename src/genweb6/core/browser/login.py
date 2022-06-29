# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.login.login import LoginForm
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.base.interfaces import ILoginForm
from plone.memoize.instance import memoize
from z3c.form import button
from zope.interface import implementer

from genweb6.core.cas.utils import getCASSettings
from genweb6.core.cas.utils import login_URL
from genweb6.core.utils import genwebLoginConfig
from genweb6.core.utils import portal_url


class LoginUtils():

    def cas_settings(self):
        return getCASSettings()

    def cas_login_URL(self):
        return login_URL(self.context, self.request)

    def login_form(self):
        return "%s/login_form" % api.portal.get().absolute_url()

    def login_name(self):
        auth = self.auth()
        name = None
        if auth is not None:
            name = getattr(auth, "name_cookie", None)
        if not name:
            name = "__ac_name"
        return name

    def login_password(self):
        auth = self.auth()
        passwd = None
        if auth is not None:
            passwd = getattr(auth, "pw_cookie", None)
        if not passwd:
            passwd = "__ac_password"
        return passwd

    @memoize
    def auth(self, _marker=None):
        if _marker is None:
            _marker = []
        acl_users = api.portal.get_tool('acl_users')
        return getattr(acl_users, "credentials_cookie_auth", None)

    def change_password_url(self):
        login_settings = genwebLoginConfig()
        if login_settings.change_password_url:
            return login_settings.change_password_url
        else:
            return '{}/@@change-password'.format(portal_url())


@implementer(ILoginForm)
class GWLoginForm(LoginForm, LoginUtils):

    @button.buttonAndHandler(_('Log in'), name='login')
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        membership_tool = getToolByName(self.context, 'portal_membership')
        status_msg = IStatusMessage(self.request)
        if membership_tool.isAnonymousUser():
            self.request.response.expireCookie('__ac', path='/')
            if self.use_email_as_login():
                status_msg.addStatusMessage(
                    _(
                        'Login failed. Both email address and password are '
                        'case sensitive, check that caps lock is not enabled.'
                    ),
                    'error',
                )
            else:
                status_msg.addStatusMessage(
                    _(
                        'Login failed. Both login name and password are case '
                        'sensitive, check that caps lock is not enabled.'
                    ),
                    'error',
                )

            # Código añadido para que en vez de reedirigir a la página de login reedirija
            # a la misma URL donde se situaba.
            came_from = data.get('came_from', None)
            self.request.response.redirect(came_from)
            # FIN Código añadido

            return

        is_initial_login = self._post_login()
        status_msg.addStatusMessage(
            _(
                'you_are_now_logged_in',
                default='Welcome! You are now logged in.',
            ),
            'info'
        )

        came_from = data.get('came_from', None)
        self.redirect_after_login(came_from, is_initial_login)
