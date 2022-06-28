# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.memoize.view import memoize_contextless

from genweb6.core import _
from genweb6.core import utils
from genweb6.core.browser.login import LoginUtils
from genweb6.core.utils import genwebCookiesConfig
from genweb6.core.utils import genwebFooterConfig


class viewletBase(ViewletBase):

    @memoize_contextless
    def root_url(self):
        return self.portal().absolute_url()

    @memoize_contextless
    def portal(self):
        return api.portal.get()

    def pref_lang(self):
        lt = api.portal.get_tool(name='portal_languages')
        lang = lt.getPreferredLanguage()
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'
        return lang

    def isAnonymous(self):
        return api.user.is_anonymous()


class loginViewlet(viewletBase, LoginUtils):

    def show_login(self):
        if self.isAnonymous():
            # TODO
            # self.genweb_config().amaga_identificacio
            return True
        return False


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


class footerViewlet(viewletBase):

    def getSignatura(self):
        lang = self.pref_lang()
        footer_config = genwebFooterConfig()
        return getattr(footer_config, 'signatura_' + lang, '')

    def getLinksPeu(self):
        lang = self.pref_lang()

        links = {"ca": {"contact":       {"url": self.root_url() + "/ca/contact", "target": '_self'},
                        "sitemap":       {"url": self.root_url() + "/ca/sitemap", "target": '_self'},
                        "accessibility": {},
                        "disclaimer":    {},
                        "cookies":       {}},

                 "es": {"contact":       {"url": self.root_url() + "/es/contact", "target": '_self'},
                        "sitemap":       {"url": self.root_url() + "/es/sitemap", "target": '_self'},
                        "accessibility": {},
                        "disclaimer":    {},
                        "cookies":       {}},

                 "en": {"contact":       {"url": self.root_url() + "/en/contact", "target": '_self'},
                        "sitemap":       {"url": self.root_url() + "/en/sitemap", "target": '_self'},
                        "accessibility": {},
                        "disclaimer":    {},
                        "cookies":       {}}}

        return links[lang]


class cookiesViewlet(viewletBase):

    def urlCookies(self):
        lang = self.pref_lang()

        if lang == 'es':
            return self.root_url() + '/politica-de-cookies-es'

        if lang == 'en':
            return self.root_url() + '/cookies-policy'

        return self.root_url() + '/politica-de-cookies'

    def notViewPDF(self):
        try:
            return 'application/pdf' not in self.request.environ['HTTP_ACCEPT']
        except:
            return True

    def isEnable(self):
        config = genwebCookiesConfig()
        return not config.disable

    def alternativeText(self):
        config = genwebCookiesConfig()

        if config.enable_alternative_text:

            lang = self.pref_lang()

            if lang == 'es':
                return config.alternative_text_es

            if lang == 'en':
                return config.alternative_text_en

            return config.alternative_text_ca

        return False
