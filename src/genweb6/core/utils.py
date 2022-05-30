# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from DateTime.DateTime import DateTime
from Products.Five.browser import BrowserView

from bs4 import BeautifulSoup
from plone import api
from plone.registry.interfaces import IRegistry
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from souper.interfaces import ICatalogFactory
from souper.soup import NodeAttributeIndexer
from zope.component import getMultiAdapter
from zope.component import provideUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

from genweb6.core import HAS_PAM

import json
import logging

logger = logging.getLogger(__name__)

PLMF = MessageFactory('plonelocales')

if HAS_PAM:
    from plone.app.multilingual.interfaces import ITranslationManager


# def genweb_config():
#     """ Funcio que retorna les configuracions del controlpanel """
#     registry = queryUtility(IRegistry)
#     return registry.forInterface(IGenwebControlPanelSettings)


def havePermissionAtRoot():
    """Funcio que retorna si es Editor a l'arrel"""
    proot = portal()
    pm = api.portal.get_tool(name='portal_membership')
    sm = getSecurityManager()
    user = pm.getAuthenticatedMember()

    return sm.checkPermission('Modify portal content', proot) or \
        ('Manager' in user.getRoles()) or \
        ('Site Administrator' in user.getRoles())
    # WebMaster used to have permission here, but not anymore since uLearn
    # makes use of it
    # ('WebMaster' in user.getRoles()) or \


def portal_url():
    """Get the Plone portal URL out of thin air without importing fancy
       interfaces and doing multi adapter lookups.
    """
    return portal().absolute_url()


def portal():
    """Get the Plone portal object out of thin air without importing fancy
       interfaces and doing multi adapter lookups.
    """
    return getSite()


def pref_lang():
    """ Extracts the current language for the current user
    """
    lt = api.portal.get_tool(name='portal_languages')
    return lt.getPreferredLanguage()


def link_translations(items):
    """
        Links the translations with the declared items with the form:
        [(obj1, lang1), (obj2, lang2), ...] assuming that the first element
        is the 'canonical' (in PAM there is no such thing).
    """
    # Grab the first item object and get its canonical handler
    canonical = ITranslationManager(items[0][0])

    for obj, language in items:
        if not canonical.has_translation(language):
            canonical.register_translation(language, obj)


def json_response(func):
    """ Decorator to transform the result of the decorated function to json.
        Expect a list (collection) that it's returned as is with response 200 or
        a dict with 'data' and 'status_code' as keys that gets extracted and
        applied the response.
    """
    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)
        request.response.setHeader(
            'Content-Type',
            'application/json; charset=utf-8'
        )
        result = func(*args, **kwargs)
        if isinstance(result, list):
            request.response.setStatus(200)
            return json.dumps(result, indent=2, sort_keys=True)
        else:
            request.response.setStatus(result.get('status_code', 200))
            return json.dumps(result.get('data', result), indent=2, sort_keys=True)

    return decorator


def abrevia(summary, sumlenght):
    """ Retalla contingut de cadenes
    """
    bb = ''

    if sumlenght < len(summary):
        bb = summary[:sumlenght]

        lastspace = bb.rfind(' ')
        cutter = lastspace
        precut = bb[0:cutter]

        if precut.count('<b>') > precut.count('</b>'):
            cutter = summary.find('</b>', lastspace) + 4
        elif precut.count('<strong>') > precut.count('</strong>'):
            cutter = summary.find('</strong>', lastspace) + 9
        bb = summary[0:cutter]

        if bb.count('<p') > precut.count('</p'):
            bb += '...</p>'
        else:
            bb = bb + '...'
    else:
        bb = summary

    try:
        return BeautifulSoup(bb.decode('utf-8', 'ignore')).prettify()
    except:
        return BeautifulSoup(bb).prettify()


def abreviaPlainText(summary, sumlenght):
    """ Retalla contingut de cadenes
    """
    bb = ''

    if sumlenght < len(summary):
        bb = summary[:sumlenght]

        lastspace = bb.rfind(' ')
        bb = bb[0:lastspace]
    else:
        bb = summary

    return bb


# class GWConfig(BrowserView):

#     def render(self):
#         return genweb_config()


class genwebUtils(BrowserView):
    """ Convenience methods placeholder genweb.utils view. """

    def portal(self):
        return api.portal.get()

    def portal_url_https(self):
        """Get the Plone portal URL in https mode """
        return self.portal().absolute_url().replace('http://', 'https://')

    def havePermissionAtRoot(self):
        """Funcio que retorna si es Editor a l'arrel"""
        pm = api.portal.get_tool(name='portal_membership')
        proot = portal()
        sm = getSecurityManager()
        user = pm.getAuthenticatedMember()

        return sm.checkPermission('Modify portal content', proot) or \
            ('WebMaster' in user.getRoles()) or \
            ('Site Administrator' in user.getRoles())

    def pref_lang(self):
        """ Extracts the current language for the current user
        """
        lt = api.portal.get_tool('portal_languages')
        return lt.getPreferredLanguage()

    def getContentClass(self, view=None):
        plone_view = getMultiAdapter(
            (self.context, self.request), name=u'plone')
        sl = plone_view.have_portlets('plone.leftcolumn', view=view)
        sr = plone_view.have_portlets('plone.rightcolumn', view=view)

        if not sl and not sr:
            return 'col-md-12'
        if (sl and not sr) or (not sl and sr):
            return 'col-md-9'
        if sl and sr:
            return 'col-md-6'

    def getProgressBarName(self, number, view=None):
        if number == 1:
            return 'progress progress-success'
        elif number == 2:
            return 'progress progress-primary'
        elif number == 3:
            return 'progress progress-warning'
        elif number == 4:
            return 'progress progress-danger'
        return 'progress progress-info'

    def get_proper_menu_list_class(self, subMenuItem):
        """ For use only in the menus to calculate the correct class value of
            some f*cking elements
        """
        if subMenuItem['extra']['id'] == 'plone-contentmenu-settings':
            return 'actionSeparator'
        if subMenuItem['extra']['id'] != 'contextSetDefaultPage':
            return subMenuItem['extra']['separator']
        else:
            return None

    def get_state_label_class_mapping(self):
        return {
            'visible': 'label-success',
            'esborrany': 'label-success',
            'published': 'label-primary',
            'intranet': 'label-intranet',
            'private': 'label-important',
            'pending': 'label-warning',
            'restricted-to-managers': 'label-inverse',
            'convocada': 'label-convocada',
            'en_correccio': 'label-en_correccio',
            'planificada': 'label-planificada',
            'realitzada': 'label-realitzada',
            'tancada': 'label-tancada',
        }

    def pref_lang_native(self):
        """ Extracts the current language for the current user in native
        """
        lt = api.portal.get_tool(name='portal_languages')
        return lt.getAvailableLanguages()[lt.getPreferredLanguage()]['native']

    # def get_published_languages(self):
    #     return genweb_config().idiomes_publicats

    def is_ldap_upc_site(self):
        acl_users = api.portal.get_tool(name='acl_users')
        if 'ldapUPC' in acl_users:
            return True
        else:
            return False

    # def redirect_to_root_always_lang_selector(self):
    #     return genweb_config().languages_link_to_root

    def is_debug_mode(self):
        return api.env.debug_mode()

    def isAnonymous(self):
        return api.user.is_anonymous()

    def isEditor(self):
        if self.isAnonymous():
            return False

        current = api.user.get_current().id
        return api.user.has_permission('Modify portal content', username=current, obj=self.context)

    def link_redirect_blank(self, item, isObject=False):
        ptool = api.portal.get_tool(name='portal_properties')
        mtool = api.portal.get_tool(name='portal_membership')

        redirect_links = getattr(
            ptool.site_properties,
            'redirect_links',
            False
        )

        if not isObject:
            item = item.getObject()

        can_edit = mtool.checkPermission('Modify portal content', item)

        def _url_uses_scheme(self, schemes, url=None):
            url = url or self.remoteUrl
            for scheme in schemes:
                if url.startswith(scheme):
                    return True
            return False

        redirect_links = redirect_links and not _url_uses_scheme(item, [
            'mailto:',
            'tel:',
            'callto:',
            'webdav:',
            'caldav:'
        ])

        return redirect_links and not can_edit and getattr(item, 'open_link_in_new_window', False)

    def localized_time(self, date):
        local_date = DateTime(date)
        return local_date.strftime('%Y-%m-%d %X')


@implementer(ICatalogFactory)
class UserPropertiesSoupCatalogFactory(object):
    def __call__(self, context):
        catalog = Catalog()
        path = NodeAttributeIndexer('path')
        catalog['path'] = CatalogFieldIndex(path)
        uuid = NodeAttributeIndexer('uuid')
        catalog['uuid'] = CatalogFieldIndex(uuid)
        return catalog


provideUtility(UserPropertiesSoupCatalogFactory(), name='uuid_preserver')
