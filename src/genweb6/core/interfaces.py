# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager


class IGenweb6CoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IConstrainedFolder(Interface):
    """ Marker interface for constrained folders """


class IHomePage(Interface):
    """ Marker interface for home page documents """


class ITranslatable(Interface):
    """ Fake marker interface in case Products.LinguaPlone is not installed """


class IGenwebUtils(Interface):
    """ Marker describing the functionality of the convenience methods
        placeholder genweb.utils view.
    """

    def portal(self):
        """ Returns the portal object """

    def havePermissionAtRoot(self):
        """ Returns if the user have permission at root """

    def pref_lang(self):
        """ Returns the user preferred language """

    def getDadesUnitat(self):
        """ Returns the data provided by the SC WebService """

    def getContentClass(self, view=None):
        """ Returns the correct class for content container (span) """

    def getProgressBarName(self, view=None):
        """ Returns the correct progress bar class in order to get the color """

    def get_proper_menu_list_class(self, subMenuItem):
        """ For use only in the menus to calculate the correct class value of
            some f*cking elements
        """

    def get_state_label_class_mapping(self):
        """"""

    def pref_lang_native(self):
        """ Get the current language selected """

    def get_published_languages(self):
        """ Get the current published languages """

    def is_ldap_upc_site(self):
        """ Boolean if site is configured with LDAP UPC auth"""

    def redirect_to_root_always_lang_selector(self):
        """ Gets the Genweb configuration property for redirect to root on
            language selector.
        """

class IGenwebLoginUtils(Interface):
    """ Marker describing the functionality of the convenience methods
        placeholder genweb.utils view.
    """

    def view_login(self):
        """ Returns the portal object """


class IProtectedContent(Interface):
    """Marker interface for preventing dumb users to delete system configuration
       related content
    """


class IPAMLSManager(IViewletManager):
    """ Marker for the PAM language switcher manager """


class INewsFolder(Interface):
    """ Marker interface for the news folders """


class IEventFolder(Interface):
    """ Marker interface for the event folders """


class IHomePageView(Interface):
    """Marker interface for the Homepage View."""
