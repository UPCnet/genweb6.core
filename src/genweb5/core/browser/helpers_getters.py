# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IApplication
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser import BrowserView
from Products.PythonScripts.standard import url_quote

from plone.app.contenttypes.interfaces import IFolder
from plone.app.layout.navigation.defaultpage import getDefaultPage
from plone.registry.interfaces import IRegistry
from plone import api
from souper.soup import get_soup
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import Interface

from genweb5.core.browser.helpers import listPloneSites
from genweb5.core.utils import json_response

import json
import pkg_resources
import re

try:
    pkg_resources.get_distribution('plone4.csrffixes')
except pkg_resources.DistributionNotFound:
    CSRF = False
else:
    from plone.protect.interfaces import IDisableCSRFProtection
    CSRF = True


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
                print("Plonesite %s doesn't have a valid ldapUPC instance." % plonesite.id)
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
                file_path = portal.restrictedTraverse(re.sub(r'(http://[^\/]+)(.*)', r'\2', src)).context.path
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
                raise ValueError("Unkown rendering method '%s' for style '%s'" % (rendering, style.getId()))
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
        domains = api.portal.get_registry_record(name='plone.cachepurging.interfaces.ICachePurgingSettings.domains')
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
            name = unicodedata.normalize('NFKD', name).encode('utf-8',errors='ignore')
        email = mail.email_from_address
        site = ISiteSchema(portal)
        ga = '\n'.join(site.webstats_js)
        if ga is not '':
            ga = unicodedata.normalize('NFKD', ga).encode('utf-8',errors='ignore')
        registry = queryUtility(IRegistry)
        gwcps = registry.forInterface(IGenwebControlPanelSettings)

        html_title_ca = gwcps.html_title_ca
        if html_title_ca is not None and type(html_title_ca) != types.BooleanType:
            html_title_ca = unicodedata.normalize('NFKD', gwcps.html_title_ca).encode('utf-8',errors='ignore')
        html_title_es = gwcps.html_title_es
        if html_title_es is not None and type(html_title_es) != types.BooleanType:
            html_title_es = unicodedata.normalize('NFKD', gwcps.html_title_es).encode('utf-8',errors='ignore')
        html_title_en = gwcps.html_title_en
        if html_title_en is not None and type(html_title_en) != types.BooleanType:
            html_title_en = unicodedata.normalize('NFKD', gwcps.html_title_en).encode('utf-8',errors='ignore')
        signatura_unitat_ca = gwcps.signatura_unitat_ca
        if signatura_unitat_ca is not None and type(signatura_unitat_ca) != types.BooleanType:
            signatura_unitat_ca = unicodedata.normalize('NFKD', gwcps.signatura_unitat_ca).encode('utf-8',errors='ignore')
        signatura_unitat_es = gwcps.signatura_unitat_es
        if signatura_unitat_es is not None and type(signatura_unitat_es) != types.BooleanType:
            signatura_unitat_es = unicodedata.normalize('NFKD', gwcps.signatura_unitat_es).encode('utf-8',errors='ignore')
        signatura_unitat_en = gwcps.signatura_unitat_en
        if signatura_unitat_en is not None and type(signatura_unitat_en) != types.BooleanType:
            signatura_unitat_en = unicodedata.normalize('NFKD', gwcps.signatura_unitat_en).encode('utf-8',errors='ignore')
        right_logo_enabled = gwcps.right_logo_enabled
        if right_logo_enabled is not None and type(right_logo_enabled) != types.BooleanType:
            right_logo_enabled = unicodedata.normalize('NFKD', gwcps.right_logo_enabled).encode('utf-8',errors='ignore')
        right_logo_alt = gwcps.right_logo_alt
        if right_logo_alt is not None and type(right_logo_alt) != types.BooleanType:
            right_logo_alt = unicodedata.normalize('NFKD', gwcps.right_logo_alt).encode('utf-8',errors='ignore')
        meta_author = gwcps.meta_author
        if meta_author is not None and type(meta_author) != types.BooleanType:
            meta_author = unicodedata.normalize('NFKD', gwcps.meta_author).encode('utf-8',errors='ignore')
        contacte_id = gwcps.contacte_id
        if contacte_id is not None and type(contacte_id) != types.BooleanType:
            contacte_id = unicodedata.normalize('NFKD', gwcps.contacte_id).encode('utf-8',errors='ignore')
        contacte_BBDD_or_page = gwcps.contacte_BBDD_or_page
        if contacte_BBDD_or_page is not None and type(contacte_BBDD_or_page) != types.BooleanType:
            contacte_BBDD_or_page = unicodedata.normalize('NFKD', gwcps.contacte_BBDD_or_page).encode('utf-8',errors='ignore')
        contacte_al_peu = gwcps.contacte_al_peu
        if contacte_al_peu is not None and type(contacte_al_peu) != types.BooleanType:
            contacte_al_peu = unicodedata.normalize('NFKD', gwcps.contacte_al_peu).encode('utf-8',errors='ignore')
        directori_upc = gwcps.directori_upc
        if directori_upc is not None and type(directori_upc) != types.BooleanType:
            directori_upc = unicodedata.normalize('NFKD', gwcps.directori_upc).encode('utf-8',errors='ignore')
        directori_filtrat = gwcps.directori_filtrat
        if directori_filtrat is not None and type(directori_filtrat) != types.BooleanType:
            directori_filtrat = unicodedata.normalize('NFKD', gwcps.directori_filtrat).encode('utf-8',errors='ignore')
        contacte_no_upcmaps = gwcps.contacte_no_upcmaps
        if contacte_no_upcmaps is not None and type(contacte_no_upcmaps) != types.BooleanType:
            contacte_no_upcmaps = unicodedata.normalize('NFKD', gwcps.contacte_no_upcmaps).encode('utf-8',errors='ignore')
        contacte_multi_email = gwcps.contacte_multi_email
        if contacte_multi_email is not None and type(contacte_multi_email) != types.BooleanType:
            contacte_multi_email = unicodedata.normalize('NFKD', gwcps.contacte_multi_email).encode('utf-8',errors='ignore')
        contact_emails_table = gwcps.contact_emails_table
        especific1 = gwcps.especific1
        if especific1 is not None and type(especific1) != types.BooleanType:
            especific1 = unicodedata.normalize('NFKD', gwcps.especific1).encode('utf-8',errors='ignore')
        especific2 = gwcps.especific2
        if especific2 is not None and type(especific2) != types.BooleanType:
            especific2 = unicodedata.normalize('NFKD', gwcps.especific2).encode('utf-8',errors='ignore')
        treu_imatge_capsalera = gwcps.treu_imatge_capsalera
        if treu_imatge_capsalera is not None and type(treu_imatge_capsalera) != types.BooleanType:
            treu_imatge_capsalera = unicodedata.normalize('NFKD', gwcps.treu_imatge_capsalera).encode('utf-8',errors='ignore')
        treu_menu_horitzontal = gwcps.treu_menu_horitzontal
        if treu_menu_horitzontal is not None and type(treu_menu_horitzontal) != types.BooleanType:
            treu_menu_horitzontal = unicodedata.normalize('NFKD', gwcps.treu_menu_horitzontal).encode('utf-8',errors='ignore')
        treu_icones_xarxes_socials = gwcps.treu_icones_xarxes_socials
        if treu_icones_xarxes_socials is not None and type(treu_icones_xarxes_socials) != types.BooleanType:
            treu_icones_xarxes_socials = unicodedata.normalize('NFKD', gwcps.treu_icones_xarxes_socials).encode('utf-8',errors='ignore')
        amaga_identificacio = gwcps.amaga_identificacio
        if amaga_identificacio is not None and type(amaga_identificacio) != types.BooleanType:
            amaga_identificacio = unicodedata.normalize('NFKD', gwcps.amaga_identificacio).encode('utf-8',errors='ignore')
        idiomes_publicats = gwcps.idiomes_publicats
        languages_link_to_root = gwcps.languages_link_to_root
        if languages_link_to_root is not None and type(languages_link_to_root) != types.BooleanType:
            languages_link_to_root = unicodedata.normalize('NFKD', gwcps.languages_link_to_root).encode('utf-8',errors='ignore')
        idestudi_master = gwcps.idestudi_master
        if idestudi_master is not None and type(idestudi_master) != types.BooleanType:
            idestudi_master = unicodedata.normalize('NFKD', gwcps.idestudi_master).encode('utf-8',errors='ignore')
        create_packet = gwcps.create_packet
        if create_packet is not None and type(create_packet) != types.BooleanType:
            create_packet = unicodedata.normalize('NFKD', gwcps.create_packet).encode('utf-8',errors='ignore')
        cl_title_ca = gwcps.cl_title_ca
        if cl_title_ca is not None and type(cl_title_ca) != types.BooleanType:
            cl_title_ca = unicodedata.normalize('NFKD', gwcps.cl_title_ca).encode('utf-8',errors='ignore')
        cl_url_ca = gwcps.cl_url_ca
        cl_img_ca = gwcps.cl_img_ca
        if cl_img_ca is not None and type(cl_img_ca) != types.BooleanType:
            cl_img_ca = unicodedata.normalize('NFKD', gwcps.cl_img_ca).encode('utf-8',errors='ignore')
        cl_open_new_window_ca = gwcps.cl_open_new_window_ca
        if cl_open_new_window_ca is not None and type(cl_open_new_window_ca) != types.BooleanType:
            cl_open_new_window_ca = unicodedata.normalize('NFKD', gwcps.cl_open_new_window_ca).encode('utf-8',errors='ignore')
        cl_enable_ca = gwcps.cl_enable_ca
        if cl_enable_ca is not None and type(cl_enable_ca) != types.BooleanType:
            cl_enable_ca = unicodedata.normalize('NFKD', gwcps.cl_enable_ca).encode('utf-8',errors='ignore')
        cl_title_es = gwcps.cl_title_es
        if cl_title_es is not None and type(cl_title_es) != types.BooleanType:
            cl_title_es = unicodedata.normalize('NFKD', gwcps.cl_title_es).encode('utf-8',errors='ignore')
        cl_url_es = gwcps.cl_url_es
        cl_img_es = gwcps.cl_img_es
        if cl_img_es is not None and type(cl_img_es) != types.BooleanType:
            cl_img_es = unicodedata.normalize('NFKD', gwcps.cl_img_es).encode('utf-8',errors='ignore')
        cl_open_new_window_es = gwcps.cl_open_new_window_es
        if cl_open_new_window_es is not None and type(cl_open_new_window_es) != types.BooleanType:
            cl_open_new_window_es = unicodedata.normalize('NFKD', gwcps.cl_open_new_window_es).encode('utf-8',errors='ignore')
        cl_enable_es = gwcps.cl_enable_es
        if cl_enable_es is not None and type(cl_enable_es) != types.BooleanType:
            cl_enable_es = unicodedata.normalize('NFKD', gwcps.cl_enable_es).encode('utf-8',errors='ignore')
        cl_title_en = gwcps.cl_title_en
        if cl_title_en is not None and type(cl_title_en) != types.BooleanType:
            cl_title_en = unicodedata.normalize('NFKD', gwcps.cl_title_en).encode('utf-8',errors='ignore')
        cl_url_en = gwcps.cl_url_en
        cl_img_en = gwcps.cl_img_en
        if cl_img_en is not None and type(cl_img_en) != types.BooleanType:
            cl_img_en = unicodedata.normalize('NFKD', gwcps.cl_img_en).encode('utf-8',errors='ignore')
        cl_open_new_window_en = gwcps.cl_open_new_window_en
        if cl_open_new_window_en is not None and type(cl_open_new_window_en) != types.BooleanType:
            cl_open_new_window_en = unicodedata.normalize('NFKD', gwcps.cl_open_new_window_en).encode('utf-8',errors='ignore')
        cl_enable_en = gwcps.cl_enable_en
        if cl_enable_en is not None and type(cl_enable_en) != types.BooleanType:
            cl_enable_en = unicodedata.normalize('NFKD', gwcps.cl_enable_en).encode('utf-8',errors='ignore')

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
                     """.format(html_title_ca, html_title_es, html_title_en,
                     signatura_unitat_ca, signatura_unitat_es, signatura_unitat_en,
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
