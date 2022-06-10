# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.memoize.instance import memoize
from plone.memoize.view import memoize_contextless
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

from genweb6.core import _
from genweb6.core import utils
from genweb6.core.controlpanels.cookies import ICookiesSettings
from genweb6.core.controlpanels.login import ILoginSettings
from genweb6.core.cas.utils import getCASSettings
from genweb6.core.cas.utils import login_URL


class viewletBase(ViewletBase):

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

    def isAnonymous(self):
        return api.user.is_anonymous()


class loginViewlet(viewletBase):

    def show_login(self):
        if self.isAnonymous():
            # TODO
            # self.genweb_config().amaga_identificacio
            return True
        return False

    def cas_settings(self):
        return getCASSettings()

    def cas_login_URL(self):
        return login_URL(self.context, self.request)

    def login_form(self):
        return "%s/login_form" % self.portal_state.portal_url()

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
        registry = queryUtility(IRegistry)
        login_settings = registry.forInterface(ILoginSettings)
        if login_settings.change_password_url:
            return login_settings.change_password_url
        else:
            portal_url = self.get_root_url()
            return '{}/@@change-password'.format(portal_url)


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


class cookiesViewlet(viewletBase):

    def cookiesConfig(self):
        """ Funcio que retorna les configuracions del controlpanel """
        registry = queryUtility(IRegistry)
        return registry.forInterface(ICookiesSettings)

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
        config = self.cookiesConfig()
        return not config.disable

    def alternativeText(self):
        config = self.cookiesConfig()

        if config.enable_alternative_text:

            lang = self.pref_lang()

            if lang == 'es':
                return config.alternative_text_es

            if lang == 'en':
                return config.alternative_text_en

            return config.alternative_text_ca

        return False
