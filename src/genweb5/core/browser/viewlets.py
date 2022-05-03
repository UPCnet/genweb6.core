# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone import api
from plone.memoize.view import memoize_contextless
from zope.interface import implementer
from zope.viewlet.interfaces import IViewlet

from genweb5.core import _
from genweb5.core import utils


@implementer(IViewlet)
class viewletBase(BrowserView):

    @memoize_contextless
    def root_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return api.portal.get()

    def pref_lang(self):
        """ Extracts the current language for the current user """
        lt = api.portal.get_tool(name='portal_languages')
        return lt.getPreferredLanguage()

    def get_root_url(self):
        """
        Get url link for logo
        """
        portal_url = api.portal.get().absolute_url()
        return portal_url


class logosFooterViewlet(viewletBase):

    def getLogosFooter(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        lang = utils.pref_lang()
        return catalog.searchResults(portal_type='Logos_Footer',
                                     review_state=['published', 'intranet'],
                                     Language=lang,
                                     sort_on='getObjPositionInParent')

    def getAltAndTitle(self, altortitle):
        """ Funcio que extreu idioma actiu i afegeix al alt i al title de les imatges del banner
            el literal Obriu l'enllac en una finestra nova.
        """
        return '%s, %s' % (altortitle, self.portal().translate(_('obrir_link_finestra_nova', default=u"(obriu en una finestra nova)")))
