# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IFolder
from OFS.interfaces import IApplication
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.subrequest import subrequest
from plone.registry.interfaces import IRegistry
from plone.uuid import interfaces
from plone.uuid.interfaces import IMutableUUID
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import Interface

import json
import logging
import os
import pkg_resources
import urllib
import transaction

from genweb5.core import HAS_PAM
from genweb5.core.interfaces import IProtectedContent

try:
    pkg_resources.get_distribution('plone4.csrffixes')
except pkg_resources.DistributionNotFound:
    CSRF = False
else:
    from plone.protect.interfaces import IDisableCSRFProtection
    CSRF = True


def setupInstallProfile(profileid, steps=None):
    """Installs the generic setup profile identified by ``profileid``.
    If a list step names is passed with ``steps`` (e.g. ['actions']),
    only those steps are installed. All steps are installed by default.
    """
    setup = api.portal.get_tool('portal_setup')
    if steps is None:
        setup.runAllImportStepsFromProfile(profileid, purge_old=False)
    else:
        for step in steps:
            setup.runImportStepFromProfile(profileid,
                                           step,
                                           run_dependencies=False,
                                           purge_old=False)


class debug(BrowserView):
    """ Convenience view for faster debugging. Needs to be manager. """

    def __call__(self):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        context = aq_inner(self.context)
        # Magic Victor debug view do not delete!
        import ipdb; ipdb.set_trace()  # Magic! Do not delete!!! :)


class monitoringView(BrowserView):
    """ Convenience view for monitoring software """

    def __call__(self):
        return '1'


class protectContent(BrowserView):
    """ Makes the context a content protected. It could only be deleted by
        managers.
    """

    def __call__(self):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)
        context = aq_inner(self.context)
        alsoProvides(context, IProtectedContent)


class instanceindevelmode(BrowserView):
    """ This instance is in development mode """

    __allow_access_to_unprotected_subobjects__ = True

    def __call__(self):
        return api.env.debug_mode()


def getDorsal():
    """ Returns Zeo dorsal """
    return os.environ.get('dorsal', False)


def listPloneSites(zope):
    """ List the available plonesites to be used by other function """
    out = []
    for item in zope.values():
        if IFolder.providedBy(item) and not IPloneSiteRoot.providedBy(item):
            for site in item.values():
                if IPloneSiteRoot.providedBy(site):
                    out.append(site)
        elif IPloneSiteRoot.providedBy(item):
            out.append(item)
    return out


class getZEO(BrowserView):
    """ [DEPRECATED] Redirect to get_zope """

    def __call__(self):
        self.request.response.redirect('get_zope')


class getZOPE(BrowserView):
    """ This view is used to know the dorsal (the Genweb enviroment) assigned to
        this instance.
    """

    def dorsal(self):
        import socket
        dorsal = os.environ.get('dorsal', False)
        serverid = socket.gethostname()
        if dorsal == '':
            return '<span style="color:#6b2508; font-size: 12vw;">NaN' + "<br/>[" + str(serverid) + "]</span>"
        else:
            return '<span style="color:#6b2508; font-size: 12vw;">' + dorsal + "<br/>[" + str(serverid) + "]</span>"


class listPloneSitesView(BrowserView):
    """ Returns a list with the available plonesites in this Zope """

    def __call__(self):
        context = aq_inner(self.context)
        out = []
        for item in context.values():
            if IFolder.providedBy(item):
                for site in item.values():
                    if IPloneSiteRoot.providedBy(site):
                        out.append(item.id + '/' + site.id)
        return json.dumps(out)


class getFlavourSitesView(BrowserView):
    """ Returns the last layer installed for each plonesite """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            portal_skins = getToolByName(plonesite, 'portal_skins')
            out[plonesite.id] = portal_skins.getDefaultSkin()
        return json.dumps(out)


class getFlavourSiteView(BrowserView):
    """ Returns the last layer installed in this plonesite """

    def __call__(self):
        context = aq_inner(self.context)
        portal_skins = getToolByName(context, 'portal_skins')
        return portal_skins.getDefaultSkin()


class getLanguagesSitesView(BrowserView):
    """ Returns the last layer installed in this plonesite """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            portal_languages = getToolByName(plonesite, 'portal_languages')
            out[plonesite.id] = portal_languages.getSupportedLanguages()
        return json.dumps(out)


class getDefaultLanguageSitesView(BrowserView):
    """ Returns default language for each plonesite """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            portal_languages = getToolByName(plonesite, 'portal_languages')
            out[plonesite.id] = portal_languages.getDefaultLanguage()
        return json.dumps(out)


class getDefaultWFSitesView(BrowserView):
    """ Returns default workflow for each plonesite """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            portal_workflow = getToolByName(plonesite, 'portal_workflow')
            out[plonesite.id] = portal_workflow.getDefaultChain()
        return json.dumps(out)


class configuraSiteCache(BrowserView):
    """ [DEPRECATED] Redirect to configure_site_cache """

    def __call__(self):
        self.request.response.redirect('configure_site_cache')


class configureSiteCache(BrowserView):
    """ Vista que configura la caché del site corresponent. """

    def __call__(self):
        context = aq_inner(self.context)
        from Products.GenericSetup.tests.common import DummyImportContext
        from plone.app.registry.exportimport.handler import RegistryImporter
        from genweb5.core.browser.cachesettings import cacheprofile
        from plone.cachepurging.interfaces import ICachePurgingSettings
        contextImport = DummyImportContext(context, purge=False)
        registry = queryUtility(IRegistry)
        importer = RegistryImporter(registry, contextImport)
        importer.importDocument(cacheprofile)

        cachepurginsettings = registry.forInterface(ICachePurgingSettings)

        varnish_url = os.environ.get('varnish_url', False)
        logger = logging.getLogger('Genweb: Executing configure cache on site -')
        logger.info('%s' % self.context.id)
        if varnish_url:
            cachepurginsettings.cachingProxies = (varnish_url,)
            logger.info('Successfully set caching for this site')
            return 'Successfully set caching for this site.'
        else:
            logger.info('There are not any varnish_url in the environment. No caching proxy could be configured.')
            return 'There are not any varnish_url in the environment. No caching proxy could be configured.'


class refreshUIDs(BrowserView):

    def __call__(self):
        form = self.request.form
        self.output = []
        if self.request['method'] == 'POST' and form.get('origin_root_path', False):
            generator = getUtility(IUUIDGenerator)
            origin_root_path = form.get('origin_root_path')
            all_objects = api.content.find(path=origin_root_path)
            for obj in all_objects:
                obj = obj.getObject()
                setattr(obj, interfaces.ATTRIBUTE_NAME, generator())
                setattr(obj, '_gw.uuid', generator())
                obj.reindexObject()
                self.output.append(obj.absolute_url())
                print(obj.absolute_url())
            self.output = '<br/>'.join(self.output)


class mirrorUIDs(BrowserView):

    def __call__(self):
        portal = self.context
        form = self.request.form
        self.output = []
        if self.request['method'] == 'POST' and form.get('origin_root_path', False):
            origin_root_path = form.get('origin_root_path')
            destination_root_path = '/'.join(portal.getPhysicalPath())
            origin_portal = portal.restrictedTraverse(origin_root_path)
            # Get all eligible objects
            if HAS_PAM:
                all_objects = origin_portal.portal_catalog.searchResults(path=origin_root_path)
            else:
                all_objects = origin_portal.portal_catalog.searchResults(path=origin_root_path, Language='all')
            for obj in all_objects:
                # Check if exist a match object by path in destination
                destination_obj = portal.unrestrictedTraverse(obj.getPath().replace(origin_root_path, destination_root_path), False)
                if destination_obj:
                    origin_uuid = obj.UID
                    IMutableUUID(destination_obj).set(str(origin_uuid))
                    destination_obj.reindexObject()
                    self.output.append('{0} -> {1}'.format(destination_obj.absolute_url(), origin_uuid))
                    print('{0} -> {1}'.format(destination_obj.absolute_url(), origin_uuid))
            self.output = '<br/>'.join(self.output)


class mirrorStates(BrowserView):

    def __call__(self):
        portal = self.context
        form = self.request.form
        self.output = []
        if self.request['method'] == 'POST' and form.get('origin_root_path', False):
            origin_root_path = form.get('origin_root_path')
            destination_root_path = '/'.join(portal.getPhysicalPath())
            origin_portal = portal.restrictedTraverse(origin_root_path)

            # States translation table from genweb_review to genweb_simple
            states = {'esborrany': 'visible', 'intranet': 'intranet', 'pending': 'pending', 'private': 'private', 'published': 'published', 'restricted-to-managers': 'restricted-to-managers'}

            # Get all eligible objects
            if HAS_PAM:
                all_objects = origin_portal.portal_catalog.searchResults(path=origin_root_path)
            else:
                all_objects = origin_portal.portal_catalog.searchResults(path=origin_root_path, Language='all')
            for obj in all_objects:
                # Check if exist a match object by path in destination
                destination_obj = portal.unrestrictedTraverse(obj.getPath().replace(origin_root_path, destination_root_path), False)
                if destination_obj:
                    origin_state = obj.review_state
                    if origin_state and origin_state != 'Missing.Value' and origin_state in states.keys():
                        api.content.transition(obj=destination_obj, to_state=states[origin_state])

                    try:
                        destination_obj.reindexObject()
                    except:
                        print("##### Not able to reindex %s" % obj.getURL())

                    self.output.append('{0} -> {1}'.format(destination_obj.absolute_url(), origin_state))
                    print('{0} -> {1}'.format(destination_obj.absolute_url(), origin_state))
            self.output = '<br/>'.join(self.output)


class bulkExecuteScriptView(BrowserView):
    """ Execute one action view in all instances passed as a form parameter """

    def __call__(self):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        context = aq_inner(self.context)
        args = self.request.form
        view_name = self.request.form['view']
        exclude_sites = self.request.form.get('exclude_sites', '').split(',')
        plonesites = listPloneSites(context)
        output = []
        for plonesite in plonesites:
            if plonesite.id not in exclude_sites:
                print('======================')
                print('Executing view in {}'.format(plonesite.id))
                print('======================')
                quoted_args = urllib.urlencode(args)
                response = subrequest('/'.join(plonesite.getPhysicalPath()) + '/{}?{}'.format(view_name, quoted_args))
                output.append("""<br/>-- Executed view {} in site {} --""".format(view_name, plonesite.id))
                output.append(response.getBody())
        return '\n'.join(output)


class notSubProcessedBulkExecuteScriptView(BrowserView):
    """
        Execute one action view in all instances passed as a form parameter used
        only in case that something does not work making a subrequest!
    """

    def __call__(self):
        context = aq_inner(self.context)
        args = self.request.form
        view_name = self.request.form['view']
        plonesites = listPloneSites(context)
        output = []
        for plonesite in plonesites:
            view = plonesite.restrictedTraverse(view_name)
            view.render(plonesite, **args)
            output.append('Executed view {} in site {}'.format(view_name, plonesite.id))
        return '\n'.join(output)


class fixRecord(BrowserView):
    """ Fix KeyError problem when plonesite is moved from the original Zeo"""

    def __call__(self, portal=None):
        from zope.component import getUtility
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        output = []
        site = self.context.portal_registry
        registry = getUtility(IRegistry)
        rec = registry.records
        keys = [a for a in rec.keys()]
        for k in keys:
            try:
                rec[k]
            except:
                output.append('{}, '.format(k))
                del site.portal_registry.records._values[k]
                del site.portal_registry.records._fields[k]
        return "S'han purgat les entrades del registre: {}".format(output)


class addPacketInDefaultPageTypes(BrowserView):
    """ Add type packet in default_page_types > site_properties"""

    def __call__(self):
        propsTool = getToolByName(self, 'portal_properties')
        siteProperties = getattr(propsTool, 'site_properties')
        defaultPageTypes = siteProperties.getProperty('default_page_types')
        try:
            types = [typ for typ in defaultPageTypes]
            if 'packet' not in types:
                types.append('packet')
                siteProperties.default_page_types = tuple(types)
                transaction.commit()
                return 'OK'
            return 'KO'
        except:
            return 'KO'
