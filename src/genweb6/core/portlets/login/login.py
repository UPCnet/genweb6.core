# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets.login import Renderer as LoginRenderer

from genweb6.core.utils import LoginUtils
from genweb6.core.cas.utils import login_URL

class gwLogin(LoginRenderer, LoginUtils):
    """ The standard navigation portlet override 'old style'
        as it doesn't allow to do it jbot way...
    """
    render = ViewPageTemplateFile("login.pt")

    def cas_login_URL(self):
        login_url = login_URL(self.context, self.request)
        url = self.context.absolute_url()
        if any(x in url for x in ['localhost', 'fepre.upc.edu', '.pre.upc.edu']):
            return False
        return login_url
