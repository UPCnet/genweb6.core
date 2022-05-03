# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser import BrowserView
from Products.PythonScripts.standard import url_quote

from plone import api
from plone.app.layout.navigation.defaultpage import getDefaultPage
from plone.registry.interfaces import IRegistry
from plone.subrequest import subrequest
from plone.uuid.interfaces import IMutableUUID
from souper.soup import get_soup
from zope.component import queryUtility
from zope.interface import alsoProvides

import json
import logging
import os
import pkg_resources
import re
import urllib

from genweb5.core import HAS_PAM
from genweb5.core.interfaces import IProtectedContent
from genweb5.core.utils import json_response

logger = logging.getLogger(__name__)

PROPERTIES_MAP = {'titolespai_ca': 'html_title_ca',
                  'titolespai_es': 'html_title_es',
                  'titolespai_en': 'html_title_en',
                  'firmaunitat_ca': 'signatura_unitat_ca',
                  'firmaunitat_es': 'signatura_unitat_es',
                  'firmaunitat_en': 'signatura_unitat_en',
                  'contacteid': 'contacte_id',
                  'especific1': 'especific1',
                  'especific3': 'especific2',
                  'idestudiMaster': 'idestudi_master',
                  'boolmaps': 'contacte_no_upcmaps'}

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
        import ipdb
        ipdb.set_trace()  # Magic! Do not delete!!! :)


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
                all_objects = origin_portal.portal_catalog.searchResults(
                    path=origin_root_path)
            else:
                all_objects = origin_portal.portal_catalog.searchResults(
                    path=origin_root_path, Language='all')
            for obj in all_objects:
                # Check if exist a match object by path in destination
                destination_obj = portal.unrestrictedTraverse(
                    obj.getPath().replace(origin_root_path, destination_root_path), False)
                if destination_obj:
                    origin_uuid = obj.UID
                    IMutableUUID(destination_obj).set(str(origin_uuid))
                    destination_obj.reindexObject()
                    self.output.append(
                        '{0} -> {1}'.format(destination_obj.absolute_url(), origin_uuid))
                    print(
                        '{0} -> {1}'.format(destination_obj.absolute_url(), origin_uuid))
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
            states = {'esborrany': 'visible', 'intranet': 'intranet', 'pending': 'pending',
                      'private': 'private', 'published': 'published', 'restricted-to-managers': 'restricted-to-managers'}

            # Get all eligible objects
            if HAS_PAM:
                all_objects = origin_portal.portal_catalog.searchResults(
                    path=origin_root_path)
            else:
                all_objects = origin_portal.portal_catalog.searchResults(
                    path=origin_root_path, Language='all')
            for obj in all_objects:
                # Check if exist a match object by path in destination
                destination_obj = portal.unrestrictedTraverse(
                    obj.getPath().replace(origin_root_path, destination_root_path), False)
                if destination_obj:
                    origin_state = obj.review_state
                    if origin_state and origin_state != 'Missing.Value' and origin_state in states.keys():
                        api.content.transition(
                            obj=destination_obj, to_state=states[origin_state])

                    try:
                        destination_obj.reindexObject()
                    except:
                        print("##### Not able to reindex %s" % obj.getURL())

                    self.output.append(
                        '{0} -> {1}'.format(destination_obj.absolute_url(), origin_state))
                    print(
                        '{0} -> {1}'.format(destination_obj.absolute_url(), origin_state))
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
                response = subrequest(
                    '/'.join(plonesite.getPhysicalPath()) + '/{}?{}'.format(view_name, quoted_args))
                output.append(
                    """<br/>-- Executed view {} in site {} --""".format(view_name, plonesite.id))
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
            output.append('Executed view {} in site {}'.format(
                view_name, plonesite.id))
        return '\n'.join(output)


class ExportGWConfig(BrowserView):
    """ ExportGWConfig """

    def render(self):
        portal = api.portal.get()
        p_properties = portal.portal_properties
        properties_map = p_properties.genwebupc_properties.propertyMap()
        result = {}
        for gw_property in properties_map:
            result[gw_property['id']] = p_properties.genwebupc_properties.getProperty(
                gw_property['id'])

        # Translation flavour - GW4.2 settings
        legacy_skin = api.portal.get_tool('portal_skins').getDefaultSkin()
        result.update({'legacy_skin': legacy_skin})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(result)


class ChangeEventsView(BrowserView):
    """
        Execute one action view in all instances
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()
        if portal.get('en', False):
            if portal['en'].get('events', False):
                events = portal['en'].get('events')
                events.setLayout('event_listing')
        if portal.get('es', False):
            if portal['es'].get('eventos', False):
                eventos = portal['es'].get('eventos')
                eventos.setLayout('event_listing')
        if portal.get('ca', False):
            if portal['ca'].get('esdeveniments', False):
                esdeveniments = portal['ca'].get('esdeveniments')
                esdeveniments.setLayout('event_listing')


# class ChangeTinyCSS(BrowserView):
#     """
#         Execute one action view in all instances
#     """
#
#     def __call__(self, portal=None):
#         if not portal:
#             portal = api.portal.get()

#         ptiny = api.portal.get_tool('portal_tinymce')
#         ptiny.content_css = u'++genwebupc++stylesheets/genwebupc.css'


class listLDAPInfo(BrowserView):
    """ List LDAP info for each plonesite """

    def __call__(self):
        context = aq_inner(self.context)
        plonesites = listPloneSites(context)
        out = {}
        for plonesite in plonesites:
            acl_users = getToolByName(plonesite, 'acl_users')
            try:
                out[plonesite.id] = acl_users.ldapUPC.acl_users.getServers()
            except:
                print("Plonesite %s doesn't have a valid ldapUPC instance." %
                      plonesite.id)
        return json.dumps(out)


class listLastLogin(BrowserView):
    """ List the last_login information for all the users in this site. """

    def __call__(self):
        pmd = api.portal.get_tool(name='portal_memberdata')
        pm = api.portal.get_tool(name='portal_membership')

        output = []
        for user in pmd._members.items():
            wrapped_user = pm.getMemberById(user[0])
            if wrapped_user:
                fullname = wrapped_user.getProperty('fullname')
                if not fullname:
                    fullname = wrapped_user.getProperty('id')
                last_login = wrapped_user.getProperty('last_login_time')
                output.append('{}; {}'.format(fullname, last_login))
        return '\n'.join(output)


class getRenderedStylesheets(BrowserView):
    """ List the location information for each stylesheet in this site. """

    @json_response
    def __call__(self):
        registry = self.context.portal_css
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)
        portal = api.portal.get()

        styles = registry.getEvaluatedResources(context)
        skinname = url_quote(self.skinname())
        urls = []
        files = []
        for style in styles:
            rendering = style.getRendering()
            if style.isExternalResource():
                src = "%s" % style.getId()
            else:
                src = "%s/%s/%s" % (registry_url, skinname, style.getId())

            try:
                file_path = portal.restrictedTraverse(
                    re.sub(r'(http://[^\/]+)(.*)', r'\2', src)).context.path
            except:
                file_path = 'No path'

            if rendering == 'link':
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'rel': style.getRel(),
                        'title': style.getTitle(),
                        'conditionalcomment': style.getConditionalcomment(),
                        'src': src,
                        'file': file_path}
            elif rendering == 'import':
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment': style.getConditionalcomment(),
                        'src': src,
                        'file': file_path}
            elif rendering == 'inline':
                content = registry.getInlineResource(style.getId(), context)
                data = {'rendering': rendering,
                        'media': style.getMedia(),
                        'conditionalcomment': style.getConditionalcomment(),
                        'content': content}
            else:
                raise ValueError("Unkown rendering method '%s' for style '%s'" % (
                    rendering, style.getId()))
            urls.append(data['src'])
            files.append(data['file'])
        return urls + files

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()


class checkCacheSettings(BrowserView):
    """ Check cache settings """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        return api.portal.get_registry_record(name='plone.app.caching.moderateCaching.etags')


class listDomaninsCache(BrowserView):
    """ Get domains from plone.app.caching """

    def __call__(self, portal=None):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        output = []
        domains = api.portal.get_registry_record(
            name='plone.cachepurging.interfaces.ICachePurgingSettings.domains')
        ppath = api.portal.getSite().getPhysicalPath()
        info = {}
        if len(ppath) > 2:
            path = ppath[1] + '/' + ppath[2] + '/'
            info['gw_id'] = path
            info['domains_list'] = domains
        output.append('{}'.format(info))
        return '\n'.join(output)


class getContactData(BrowserView):
    """ Get Contact data from all instances """

    def __call__(self, portal=None):
        portal = api.portal.get()
        mail = IMailSchema(portal)
        path = portal.absolute_url()
        host = mail.smtp_host
        name = mail.email_from_name
        email = mail.email_from_address
        return (path, host, name, email)


class getConfigGenwebControlPanelSettings(BrowserView):
    """Recordar afegir nous camps quan s'actualitzi el genweb upc ctrlpanel"""

    def __call__(self, portal=None):
        from genweb5.controlpanel.interface import IGenwebControlPanelSettings
        from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
        import unicodedata
        import types
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        mail = IMailSchema(portal)
        name = mail.email_from_name
        if name is not None:
            name = unicodedata.normalize(
                'NFKD', name).encode('utf-8', errors='ignore')
        email = mail.email_from_address
        site = ISiteSchema(portal)
        ga = '\n'.join(site.webstats_js)
        if ga is not '':
            ga = unicodedata.normalize('NFKD', ga).encode(
                'utf-8', errors='ignore')
        registry = queryUtility(IRegistry)
        gwcps = registry.forInterface(IGenwebControlPanelSettings)

        html_title_ca = gwcps.html_title_ca
        if html_title_ca is not None and type(html_title_ca) != types.BooleanType:
            html_title_ca = unicodedata.normalize(
                'NFKD', gwcps.html_title_ca).encode('utf-8', errors='ignore')
        html_title_es = gwcps.html_title_es
        if html_title_es is not None and type(html_title_es) != types.BooleanType:
            html_title_es = unicodedata.normalize(
                'NFKD', gwcps.html_title_es).encode('utf-8', errors='ignore')
        html_title_en = gwcps.html_title_en
        if html_title_en is not None and type(html_title_en) != types.BooleanType:
            html_title_en = unicodedata.normalize(
                'NFKD', gwcps.html_title_en).encode('utf-8', errors='ignore')
        signatura_unitat_ca = gwcps.signatura_unitat_ca
        if signatura_unitat_ca is not None and type(signatura_unitat_ca) != types.BooleanType:
            signatura_unitat_ca = unicodedata.normalize(
                'NFKD', gwcps.signatura_unitat_ca).encode('utf-8', errors='ignore')
        signatura_unitat_es = gwcps.signatura_unitat_es
        if signatura_unitat_es is not None and type(signatura_unitat_es) != types.BooleanType:
            signatura_unitat_es = unicodedata.normalize(
                'NFKD', gwcps.signatura_unitat_es).encode('utf-8', errors='ignore')
        signatura_unitat_en = gwcps.signatura_unitat_en
        if signatura_unitat_en is not None and type(signatura_unitat_en) != types.BooleanType:
            signatura_unitat_en = unicodedata.normalize(
                'NFKD', gwcps.signatura_unitat_en).encode('utf-8', errors='ignore')
        right_logo_enabled = gwcps.right_logo_enabled
        if right_logo_enabled is not None and type(right_logo_enabled) != types.BooleanType:
            right_logo_enabled = unicodedata.normalize(
                'NFKD', gwcps.right_logo_enabled).encode('utf-8', errors='ignore')
        right_logo_alt = gwcps.right_logo_alt
        if right_logo_alt is not None and type(right_logo_alt) != types.BooleanType:
            right_logo_alt = unicodedata.normalize(
                'NFKD', gwcps.right_logo_alt).encode('utf-8', errors='ignore')
        meta_author = gwcps.meta_author
        if meta_author is not None and type(meta_author) != types.BooleanType:
            meta_author = unicodedata.normalize(
                'NFKD', gwcps.meta_author).encode('utf-8', errors='ignore')
        contacte_id = gwcps.contacte_id
        if contacte_id is not None and type(contacte_id) != types.BooleanType:
            contacte_id = unicodedata.normalize(
                'NFKD', gwcps.contacte_id).encode('utf-8', errors='ignore')
        contacte_BBDD_or_page = gwcps.contacte_BBDD_or_page
        if contacte_BBDD_or_page is not None and type(contacte_BBDD_or_page) != types.BooleanType:
            contacte_BBDD_or_page = unicodedata.normalize(
                'NFKD', gwcps.contacte_BBDD_or_page).encode('utf-8', errors='ignore')
        contacte_al_peu = gwcps.contacte_al_peu
        if contacte_al_peu is not None and type(contacte_al_peu) != types.BooleanType:
            contacte_al_peu = unicodedata.normalize(
                'NFKD', gwcps.contacte_al_peu).encode('utf-8', errors='ignore')
        directori_upc = gwcps.directori_upc
        if directori_upc is not None and type(directori_upc) != types.BooleanType:
            directori_upc = unicodedata.normalize(
                'NFKD', gwcps.directori_upc).encode('utf-8', errors='ignore')
        directori_filtrat = gwcps.directori_filtrat
        if directori_filtrat is not None and type(directori_filtrat) != types.BooleanType:
            directori_filtrat = unicodedata.normalize(
                'NFKD', gwcps.directori_filtrat).encode('utf-8', errors='ignore')
        contacte_no_upcmaps = gwcps.contacte_no_upcmaps
        if contacte_no_upcmaps is not None and type(contacte_no_upcmaps) != types.BooleanType:
            contacte_no_upcmaps = unicodedata.normalize(
                'NFKD', gwcps.contacte_no_upcmaps).encode('utf-8', errors='ignore')
        contacte_multi_email = gwcps.contacte_multi_email
        if contacte_multi_email is not None and type(contacte_multi_email) != types.BooleanType:
            contacte_multi_email = unicodedata.normalize(
                'NFKD', gwcps.contacte_multi_email).encode('utf-8', errors='ignore')
        contact_emails_table = gwcps.contact_emails_table
        especific1 = gwcps.especific1
        if especific1 is not None and type(especific1) != types.BooleanType:
            especific1 = unicodedata.normalize(
                'NFKD', gwcps.especific1).encode('utf-8', errors='ignore')
        especific2 = gwcps.especific2
        if especific2 is not None and type(especific2) != types.BooleanType:
            especific2 = unicodedata.normalize(
                'NFKD', gwcps.especific2).encode('utf-8', errors='ignore')
        treu_imatge_capsalera = gwcps.treu_imatge_capsalera
        if treu_imatge_capsalera is not None and type(treu_imatge_capsalera) != types.BooleanType:
            treu_imatge_capsalera = unicodedata.normalize(
                'NFKD', gwcps.treu_imatge_capsalera).encode('utf-8', errors='ignore')
        treu_menu_horitzontal = gwcps.treu_menu_horitzontal
        if treu_menu_horitzontal is not None and type(treu_menu_horitzontal) != types.BooleanType:
            treu_menu_horitzontal = unicodedata.normalize(
                'NFKD', gwcps.treu_menu_horitzontal).encode('utf-8', errors='ignore')
        treu_icones_xarxes_socials = gwcps.treu_icones_xarxes_socials
        if treu_icones_xarxes_socials is not None and type(treu_icones_xarxes_socials) != types.BooleanType:
            treu_icones_xarxes_socials = unicodedata.normalize(
                'NFKD', gwcps.treu_icones_xarxes_socials).encode('utf-8', errors='ignore')
        amaga_identificacio = gwcps.amaga_identificacio
        if amaga_identificacio is not None and type(amaga_identificacio) != types.BooleanType:
            amaga_identificacio = unicodedata.normalize(
                'NFKD', gwcps.amaga_identificacio).encode('utf-8', errors='ignore')
        idiomes_publicats = gwcps.idiomes_publicats
        languages_link_to_root = gwcps.languages_link_to_root
        if languages_link_to_root is not None and type(languages_link_to_root) != types.BooleanType:
            languages_link_to_root = unicodedata.normalize(
                'NFKD', gwcps.languages_link_to_root).encode('utf-8', errors='ignore')
        idestudi_master = gwcps.idestudi_master
        if idestudi_master is not None and type(idestudi_master) != types.BooleanType:
            idestudi_master = unicodedata.normalize(
                'NFKD', gwcps.idestudi_master).encode('utf-8', errors='ignore')
        create_packet = gwcps.create_packet
        if create_packet is not None and type(create_packet) != types.BooleanType:
            create_packet = unicodedata.normalize(
                'NFKD', gwcps.create_packet).encode('utf-8', errors='ignore')
        cl_title_ca = gwcps.cl_title_ca
        if cl_title_ca is not None and type(cl_title_ca) != types.BooleanType:
            cl_title_ca = unicodedata.normalize(
                'NFKD', gwcps.cl_title_ca).encode('utf-8', errors='ignore')
        cl_url_ca = gwcps.cl_url_ca
        cl_img_ca = gwcps.cl_img_ca
        if cl_img_ca is not None and type(cl_img_ca) != types.BooleanType:
            cl_img_ca = unicodedata.normalize(
                'NFKD', gwcps.cl_img_ca).encode('utf-8', errors='ignore')
        cl_open_new_window_ca = gwcps.cl_open_new_window_ca
        if cl_open_new_window_ca is not None and type(cl_open_new_window_ca) != types.BooleanType:
            cl_open_new_window_ca = unicodedata.normalize(
                'NFKD', gwcps.cl_open_new_window_ca).encode('utf-8', errors='ignore')
        cl_enable_ca = gwcps.cl_enable_ca
        if cl_enable_ca is not None and type(cl_enable_ca) != types.BooleanType:
            cl_enable_ca = unicodedata.normalize(
                'NFKD', gwcps.cl_enable_ca).encode('utf-8', errors='ignore')
        cl_title_es = gwcps.cl_title_es
        if cl_title_es is not None and type(cl_title_es) != types.BooleanType:
            cl_title_es = unicodedata.normalize(
                'NFKD', gwcps.cl_title_es).encode('utf-8', errors='ignore')
        cl_url_es = gwcps.cl_url_es
        cl_img_es = gwcps.cl_img_es
        if cl_img_es is not None and type(cl_img_es) != types.BooleanType:
            cl_img_es = unicodedata.normalize(
                'NFKD', gwcps.cl_img_es).encode('utf-8', errors='ignore')
        cl_open_new_window_es = gwcps.cl_open_new_window_es
        if cl_open_new_window_es is not None and type(cl_open_new_window_es) != types.BooleanType:
            cl_open_new_window_es = unicodedata.normalize(
                'NFKD', gwcps.cl_open_new_window_es).encode('utf-8', errors='ignore')
        cl_enable_es = gwcps.cl_enable_es
        if cl_enable_es is not None and type(cl_enable_es) != types.BooleanType:
            cl_enable_es = unicodedata.normalize(
                'NFKD', gwcps.cl_enable_es).encode('utf-8', errors='ignore')
        cl_title_en = gwcps.cl_title_en
        if cl_title_en is not None and type(cl_title_en) != types.BooleanType:
            cl_title_en = unicodedata.normalize(
                'NFKD', gwcps.cl_title_en).encode('utf-8', errors='ignore')
        cl_url_en = gwcps.cl_url_en
        cl_img_en = gwcps.cl_img_en
        if cl_img_en is not None and type(cl_img_en) != types.BooleanType:
            cl_img_en = unicodedata.normalize(
                'NFKD', gwcps.cl_img_en).encode('utf-8', errors='ignore')
        cl_open_new_window_en = gwcps.cl_open_new_window_en
        if cl_open_new_window_en is not None and type(cl_open_new_window_en) != types.BooleanType:
            cl_open_new_window_en = unicodedata.normalize(
                'NFKD', gwcps.cl_open_new_window_en).encode('utf-8', errors='ignore')
        cl_enable_en = gwcps.cl_enable_en
        if cl_enable_en is not None and type(cl_enable_en) != types.BooleanType:
            cl_enable_en = unicodedata.normalize(
                'NFKD', gwcps.cl_enable_en).encode('utf-8', errors='ignore')

        output = """Títol del web amb HTML tags (negretes) [CA]: {}<br/>
                     Títol del web amb HTML tags (negretes) [ES]: {}<br/>
                     Títol del web amb HTML tags (negretes) [EN]: {}<br/>
                     Signatura de la unitat [CA]: {}<br/>
                     Signatura de la unitat [ES]: {}<br/>
                     Signatura de la unitat [EN]: {}<br/>
                     Mostrar logo dret: {}<br/>
                     Text alternatiu del logo dret: {}<br/>
                     Meta author tag content: {}<br/>
                     ID contacte de la unitat: {}<br/>
                     Pàgina de contacte alternativa: {}<br/>
                     Adreça de contacte al peu: {}<br/>
                     Directori UPC a les eines: {}<br/>
                     Filtrat per unitat?: {}<br/>
                     Desactivar UPCmaps: {}<br/>
                     Seleccionar l'adreça d'enviament: {}<br/>
                     Contact emails: {}<br/>
                     Color específic 1: {}<br/>
                     Color específic 2: {}<br/>
                     Treu la imatge de la capçalera: {}<br/>
                     Treu el menú horitzontal: {}<br/>
                     Treu les icones per compartir en xarxes socials: {}<br/>
                     Amaga l'enllaç d'identificació de les eines: {}<br/>
                     Idiomes publicats al web: {}<br/>
                     Redireccionar a l'arrel del lloc al clicar sobre els idiomes del portal: {}<br/>
                     id_estudi: {}<br/>
                     Crear informació general del màster: {}<br/>
                     Link title [CA]: {}<br/>
                     Enllaç per al menú superior: {}<br/>
                     Enllaç per a la icona del menú superior: {}<br/>
                     Obre en una nova finestra: {}<br/>
                     Publica l'enllaç customitzat: {}<br/>
                     Link title [ES]: {}<br/>
                     Enllaç per al menú superior: {}<br/>
                     Enllaç per a la icona del menú superior: {}<br/>
                     Obre en una nova finestra: {}<br/>
                     Publica l'enllaç customitzat: {}<br/>
                     Link title [EN]: {}<br/>
                     Enllaç per al menú superior: {}<br/>
                     Enllaç per a la icona del menú superior: {}<br/>
                     Obre en una nova finestra: {}<br/>
                     Publica l'enllaç customitzat: {}<br/>
                     Nom 'De' del lloc: {}<br/>
                     Adreça 'De' del lloc: {}<br/>
                     Javascript per al suport d'estadístiques web: {}<br/></br>
                     """.format(html_title_ca, html_title_es, html_title_en, signatura_unitat_ca,
                                signatura_unitat_es, signatura_unitat_en,
                                right_logo_enabled, right_logo_alt, meta_author, contacte_id,
                                contacte_BBDD_or_page, contacte_al_peu, directori_upc,
                                directori_filtrat, contacte_no_upcmaps, contacte_multi_email,
                                contact_emails_table, especific1, especific2,
                                treu_imatge_capsalera, treu_menu_horitzontal,
                                treu_icones_xarxes_socials, amaga_identificacio,
                                idiomes_publicats, languages_link_to_root, idestudi_master,
                                create_packet, cl_title_ca, cl_url_ca, cl_img_ca,
                                cl_open_new_window_ca, cl_enable_ca, cl_title_es, cl_url_es,
                                cl_img_es, cl_open_new_window_es, cl_enable_es, cl_title_en,
                                cl_url_en, cl_img_en, cl_open_new_window_en, cl_enable_en,
                                name, email, ga)
        return output


class getUsedGroups(BrowserView):
    """ Return all users from ldap groups that have permissions in any plone object """

    def __call__(self, portal=None):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        res = []
        portal = api.portal.get()
        soup = get_soup('ldap_groups', portal)
        records = [r for r in soup.data.items()]
        ldap_groups = []
        for record in records:
            ldap_groups.append(record[1].attrs['id'])

        pc = api.portal.get_tool('portal_catalog')
        results = pc.searchResults(path='/'.join(portal.getPhysicalPath()))
        for brain in results:
            obj = brain.getObject()
            roles = obj.get_local_roles()
            for rol in roles:
                name = rol[0]
                if name in ldap_groups and name not in res:
                    res.append(name)
        return res


class getCollectionDefaultPages(BrowserView):
    """
    List the value of the property 'default_page' (if defined) for contents
    with type Collection.
    """

    REPORT_TABLE = """
    <table>
       <thead>
         <tr>
           <th>url</th>
           <th>title</th>
           <th>default_page</th>
         </tr>
      </thead>
      <tbody>{body}</tbody>
    </table>
    """

    REPORT_ROW = """
    <tr>
      <td><a href="{url}" target="_blank">{url}</a></td>
      <td>({title})</td>
      <td>{default_page}</td>
    </tr>
    """

    def __call__(self):
        collections = []
        catalog = api.portal.get_tool('portal_catalog')
        for collection in catalog.searchResults(portal_type='Collection'):
            collection_obj = collection.getObject()
            default_page = self._get_default_page(collection_obj)
            if default_page:
                collections.append(dict(
                    url=collection_obj.absolute_url(),
                    title=collection_obj.title,
                    default_page=default_page))
        collections = sorted(collections, key=lambda e: e['url'])
        return self._compose_report(collections)

    def _get_default_page(self, content):
        default_page = getDefaultPage(content)
        if not default_page:
            default_page = content.getProperty('default_page')
        return default_page

    def _compose_report(self, collections):
        if not collections:
            return "No default pages were found"
        return getCollectionDefaultPages.REPORT_TABLE.format(
            **dict(body='\n'.join(
                [getCollectionDefaultPages.REPORT_ROW.format(**default_page)
                 for default_page in collections])))
