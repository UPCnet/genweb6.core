# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.login.login import LoginForm
from Products.statusmessages.interfaces import IStatusMessage

from plone.base.interfaces import ILoginForm
from z3c.form import button
from zope.interface import implementer


@implementer(ILoginForm)
class GWLoginForm(LoginForm):

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
