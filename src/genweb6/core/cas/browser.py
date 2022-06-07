# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserPage

from genweb6.core.cas import utils


class LoginUrl(BrowserPage):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return utils.login_URL(self.context, self.request)


class LoginFormUrl(BrowserPage):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return utils.loginForm_URL(self.context, self.request)


class Logout(BrowserPage):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        utils.logout(self.context, self.request)
