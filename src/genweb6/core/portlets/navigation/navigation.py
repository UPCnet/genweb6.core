# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets.navigation import Renderer as NavigationRenderer


class gwNavigation(NavigationRenderer):
    """ The standard navigation portlet override 'old style'
        as it doesn't allow to do it jbot way...
    """
    _template = ViewPageTemplateFile('navigation.pt')
    recurse = ViewPageTemplateFile('navigation_recurse.pt')

    def is_lrf_type(self):
        return self.context.id in ["ca", "es", "en", "benvingut", "bienvenido", "welcome"]
