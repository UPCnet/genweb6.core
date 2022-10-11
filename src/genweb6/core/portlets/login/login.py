# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets.login import Renderer as LoginRenderer

from genweb6.core.utils import LoginUtils


class gwLogin(LoginRenderer, LoginUtils):
    """ The standard navigation portlet override 'old style'
        as it doesn't allow to do it jbot way...
    """
    render = ViewPageTemplateFile("login.pt")
