# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import getSecurityManager

from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from plone.app.layout.viewlets.common import SearchBoxViewlet
from plone.formwidget.namedfile.converter import b64decode_file
from plone.memoize.view import memoize_contextless

from genweb6.core import _
from genweb6.core import utils
from genweb6.core.browser.login import LoginUtils
from genweb6.core.utils import genwebCintilloConfig
from genweb6.core.utils import genwebCookiesConfig
from genweb6.core.utils import genwebFooterConfig
from genweb6.core.utils import genwebHeaderConfig


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


class cintilloViewlet(viewletBase):

    def info_cintillo(self):
        cintillo_config = genwebCintilloConfig()
        if not cintillo_config.active:
            return {"show": False}

        lang = self.pref_lang()
        return {"show": True,
                "style": "background-color: " + cintillo_config.background_color +
                         "; color: " + cintillo_config.font_color + ";",
                "icon": cintillo_config.icon,
                "title": getattr(cintillo_config, "title_" + lang, ""),
                "text": getattr(cintillo_config, "text_" + lang, "")}


class loginViewlet(viewletBase, LoginUtils):

    def show_login(self):
        if self.isAnonymous():
            if not genwebHeaderConfig().amaga_identificacio:
                return True
        return False


class headerViewlet(loginViewlet, SearchBoxViewlet, GlobalSectionsViewlet):

    def getLogosHeader(self):
        header_config = genwebHeaderConfig()
        portal_url = self.root_url()

        if getattr(header_config, 'logo', False):
            filename, data = b64decode_file(header_config.logo)
            logo = '{}/@@gw-logo/{}'.format(portal_url, filename)
        else:
            logo = '%s/logo.png' % portal_url

        if getattr(header_config, 'logo_responsive', False):
            filename, data = b64decode_file(header_config.logo_responsive)
            logo_responsive = '{}/@@gw-logo-responsive/{}'.format(portal_url, filename)
        else:
            logo_responsive = logo

        if getattr(header_config, 'secundary_logo', False):
            filename, data = b64decode_file(header_config.secundary_logo)
            secundary_logo = '{}/@@gw-secundary-logo/{}'.format(portal_url, filename)
        else:
            secundary_logo = None

        if getattr(header_config, 'secundary_logo_responsive', False):
            filename, data = b64decode_file(header_config.secundary_logo_responsive)
            secundary_logo_responsive = '{}/@@gw-secundary-logo-responsive/{}'.format(portal_url, filename)
        else:
            secundary_logo_responsive = secundary_logo

        return {"logo": logo,
                "logo_responsive": logo_responsive,
                "logo_alt": getattr(header_config, 'logo_alt', ""),
                "logo_url": getattr(header_config, 'logo_url', None),
                "logo_target": "_blank" if header_config.logo_external_url else "_self",
                "logo_responsive": logo_responsive,
                "secundary_logo": secundary_logo,
                "secundary_logo_responsive": secundary_logo_responsive,
                "secundary_logo_alt": getattr(header_config, 'secundary_logo_alt', ""),
                "secundary_logo_url": getattr(header_config, 'secundary_logo_url', None),
                "secundary_logo_target": "_blank" if header_config.secundary_logo_external_url else "_self"}

    def show_auto_register(self):
        if self.isAnonymous():
            return getSecurityManager().checkPermission("Add portal member", self.context)
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
