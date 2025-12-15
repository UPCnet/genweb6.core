# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets.login import Renderer as LoginRenderer

from genweb6.core.utils import LoginUtils
from genweb6.core.cas.utils import login_URL

import re


class gwLogin(LoginRenderer, LoginUtils):
    """ The standard navigation portlet override 'old style'
        as it doesn't allow to do it jbot way...
    """
    render = ViewPageTemplateFile("login.pt")

    def cas_login_URL(self):
        login_url = login_URL(self.context, self.request)

        # Si tiene el ticket en la url, quiere decir que es un usuario válido pero no tiene permisos.
        # Por tanto, redirigimos a la página de error para evitar el bucle infinito del SSO
        # En el log vemos Unauthorized(m) - zExceptions.unauthorized.Unauthorized: You are not authorized to access this resource.
        if 'ticket' in getattr(self.request, 'came_from', ''):
            return self.request.response.redirect(
                self.context.absolute_url() + '/insufficient-privileges')

        url = self.context.absolute_url()
        patterns = [
            'localhost',
            'pre.upc.edu',
            'redhood[123].upc.edu',
            r'fe([1-9]|1[0-9]|20).upc.edu', 
        ]
        if any(re.search(pattern, url) for pattern in patterns):
            return False
        return login_url
