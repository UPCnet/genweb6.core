# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone.controlpanel.browser.quickinstaller import InstallerView
from Products.CMFPlone.utils import get_installer
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PortalTransforms.transforms.pdf_to_text import pdf_to_text

from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from plone.uuid import interfaces
from plone.uuid.interfaces import IMutableUUID
from plone.uuid.interfaces import IUUIDGenerator
from repoze.catalog.query import Eq
from souper.soup import get_soup
from souper.soup import Record
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import alsoProvides

from genweb6.core import HAS_DXCT
from genweb6.core.interfaces import IHomePage

import logging
import os
import pkg_resources
import transaction

logger = logging.getLogger(__name__)


try:
    pkg_resources.get_distribution('plone4.csrffixes')
except pkg_resources.DistributionNotFound:
    CSRF = False
else:
    from plone.protect.interfaces import IDisableCSRFProtection
    CSRF = True


class make_me_a_homepage(BrowserView):
    """
Habilita el layout de homepage en el contingut, ha de ser una carpeta
    """

    def __call__(self):
        alsoProvides(self.context, IHomePage)
        if HAS_DXCT:
            from plone.app.contenttypes.interfaces import IFolder
            if IFolder.providedBy(self.context):
                self.context.setLayout('homepage')
        return self.request.response.redirect(self.context.absolute_url())


class make_me_a_subhome_page(BrowserView):
    """
Habilita el layout de subhomepage en el contingut, ha de ser una carpeta
    """

    def __call__(self):
        alsoProvides(self.context, IHomePage)
        if HAS_DXCT:
            from plone.app.contenttypes.interfaces import IFolder
            if IFolder.providedBy(self.context):
                self.context.setLayout('subhomepage')
        return self.request.response.redirect(self.context.absolute_url())


class reset_language(BrowserView):
    """
Torna a establir l'idioma de cada LRF segons el seu nom. Executar en un LRF
LRF -> Language Root Folder
    """

    def __call__(self):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        from Products.CMFPlone.interfaces import ILanguage
        context = aq_inner(self.context)
        pc = api.portal.get_tool('portal_catalog')
        results = pc.unrestrictedSearchResults(
            path='/'.join(context.getPhysicalPath()))

        for brain in results:
            ob = brain._unrestrictedGetObject()
            language_aware = ILanguage(ob, None)
            if language_aware is not None:
                language_aware.set_language(self.context.id)
                ob.reindexObject(idxs=['Language', 'TranslationGroup'])


class enable_pdf_indexing(BrowserView):
    """
Activa la indexació de PDF
    """

    def __call__(self):
        pt = api.portal.get_tool('portal_transforms')
        pt.registerTransform(pdf_to_text())

        return 'Done'


class update_folder_views(BrowserView):
    """
Actualitza les vistes per al tipus de carpeta
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        portal.portal_types['Folder'].view_methods = (
            'listing_view', 'album_view', 'summary_view', 'tabular_view',
            'full_view', 'folder_index_view', 'filtered_contents_search_pretty_view')
        import transaction
        transaction.commit()
        output.append('{}: Successfully reinstalled'.format(portal.id))
        return '\n'.join(output)


class add_folder_view(BrowserView):
    """
Afegeix una vista nova al tipus de contingut carpeta

Paràmetre:
- addview: nom de la vista
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        if 'addview' in self.request.form:

            views = list(portal.portal_types['Folder'].view_methods)
            view = self.request.form['addview']
            if view not in views:
                views.append(view)
            portal.portal_types['Folder'].view_methods = tuple(views)
            import transaction
            transaction.commit()
            output.append('{}: Successfully added view'.format(portal.id))
            return '\n'.join(output)

        output.append(
            '{}: Error parameter addview, not defined'.format(portal.id))
        return '\n'.join(output)


class remove_folder_view(BrowserView):
    """
Elimina una vista al tipus de contingut carpeta

Paràmetre:
- removeview: nom de la vista
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        if 'removeview' in self.request.form:
            views = list(portal.portal_types['Folder'].view_methods)
            view = self.request.form['removeview']
            if view in views:
                views.remove(view)
            portal.portal_types['Folder'].view_methods = tuple(views)
            import transaction
            transaction.commit()
            output.append('{}: Successfully removed view'.format(portal.id))
            return '\n'.join(output)

        output.append(
            '{}: Error parameter removeview, not defined'.format(portal.id))
        return '\n'.join(output)


class install_product(BrowserView):
    """
Instal·la un paquet

Paràmetre:
- product_name: id del paquet
    """

    def __call__(self, portal=None):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        if 'product_name' in self.request.form:
            if not portal:
                portal = api.portal.get()

            product_name = self.request.form['product_name']
            output = []
            qi = get_installer(self.context)

            if qi.is_product_installed(product_name):
                qi.uninstall_product(product_name)

            qi.install_product(product_name)
            output.append('{}: Successfully installed {}'.format(
                portal.id, product_name))

            return '\n'.join(output)

        return 'Error parameter product_name, not defined'


class reinstall_product(InstallerView):
    """
Reinstal·la un paquet

Paràmetre:
- product_name: id del paquet
    """

    def __call__(self, portal=None):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        if 'product_name' in self.request.form:
            if not portal:
                portal = api.portal.get()

            product_name = self.request.form['product_name']
            output = []
            qi = get_installer(self.context)

            if qi.is_product_installed(product_name):
                qi.upgrade_product(product_name)
                output.append('{}: Successfully reinstalled {}'.format(
                    portal.id, product_name))
            return '\n'.join(output)

        return 'Error parameter product_name, not defined'


class uninstall_product(BrowserView):
    """
Desinstal·la un paquet

Paràmetre:
- product_name: id del paquet
    """

    def __call__(self, portal=None):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        if 'product_name' in self.request.form:
            if not portal:
                portal = api.portal.get()

            product_name = self.request.form['product_name']
            output = []
            qi = get_installer(self.context)

            if qi.is_product_installed(product_name):
                qi.uninstall_product(product_name)
                output.append('{}: Successfully uninstalled {}'.format(portal.id, product_name))
            return '\n'.join(output)

        return 'Error parameter product_name, not defined'


class upgrade_plone_version(BrowserView):
    """
Upgrada a la última versió de Plone
    """

    def __call__(self, portal=None):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        if not portal:
            portal = api.portal.get()

        pm = api.portal.get_tool('portal_migration')
        self.request.method = 'POST'
        report = pm.upgrade(
            REQUEST=self.request,
            dry_run=False,
        )
        return report


class setup_pam_again(BrowserView):
    """
setup_pam_again
    """

    def __call__(self):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        from plone.app.multilingual.browser.setup import SetupMultilingualSite
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.context, False)


class delete_navportlet_from_root(BrowserView):
    """
Elimina el portlet de navegació de l'arrel
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        # Delete default Navigation portlet on root
        target_manager_root = queryUtility(
            IPortletManager, name='plone.leftcolumn', context=portal)
        target_manager_root_assignments = getMultiAdapter(
            (portal, target_manager_root), IPortletAssignmentMapping)
        if 'navigation' in target_manager_root_assignments:
            del target_manager_root_assignments['navigation']


class portal_setup_import(BrowserView):
    """
Reinstal·la un step específic

Paràmetres:
- step: id del step a importar, ex: 'portlets'.
- profile: identificador del perfil o de la instantània a seleccionar, ex: 'genweb.upc'.
- profile_type: tipus del perfil seleccionat, 'default' per defecte.
    """

    DEFAULT_PROFILE_TYPE = 'default'

    def __call__(self):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)

        ps = api.portal.get_tool(name='portal_setup')
        params = self._parse_params()
        ps.runImportStepFromProfile(
            'profile-{profile}:{profile_type}'.format(**params),
            params['step'])
        return ('{step} from {profile}:{profile_type} '
                'successfully imported').format(**params)

    def _parse_params(self):
        if 'step' not in self.request.form:
            raise ValueError("Mandatory parameter 'step' was not specified")
        if 'profile' not in self.request.form:
            raise ValueError("Mandatory parameter 'profile' was not specified")
        step = self.request.form['step']
        profile = self.request.form['profile']
        profile_type = self.request.form.get(
            'profile_type', portal_setup_import.DEFAULT_PROFILE_TYPE)
        return dict(step=step, profile=profile, profile_type=profile_type)


class set_sitemap_depth(BrowserView):
    """
Assigna 3 nivells en el sitemap
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        navtree_props = portal.portal_properties.navtree_properties
        navtree_props.sitemapDepth = 4
        import transaction
        transaction.commit()
        output.append(
            '{}: Successfully setted 3 levels in sitemap'.format(portal.id))
        return '\n'.join(output)


class update_lif_lrf(BrowserView):
    """
Actualitza les vistes de LIf i LRF
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        portal.portal_types['LIF'].view_methods = (
            'listing_view', 'summary_view', 'tabular_view', 'full_view', 'album_view')
        portal.portal_types['LIF'].default_view = 'tabular_view'
        portal.portal_types['LRF'].view_methods = (
            'listing_view', 'summary_view', 'tabular_view', 'full_view', 'album_view')
        portal.portal_types['LRF'].default_view = 'tabular_view'
        import transaction
        transaction.commit()
        output.append('{}: Successfully reinstalled'.format(portal.id))
        return '\n'.join(output)


class reindex_all_pages(BrowserView):
    """
Reindeixa tots els continguts de tipus Document
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        pc = api.portal.get_tool(name='portal_catalog')
        brains = pc.searchResults(portal_type='Document')
        for result in brains:
            obj = result.getObject()
            obj.reindexObject()
        import transaction
        transaction.commit()
        output.append('{}: Documents successfully reindexed'.format(portal.id))
        return '\n'.join(output)


class refactor_news_collection(BrowserView):
    """
refactor_news_collection
    """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        NEWS_QUERY = [{'i': u'portal_type', 'o': u'plone.app.querystring.operation.selection.is', 'v': [u'News Item', u'Link']},
                      {'i': u'review_state', 'o': u'plone.app.querystring.operation.selection.is', 'v': [
                          u'published']},
                      {'i': u'path', 'o': u'plone.app.querystring.operation.string.relativePath', 'v': u'..'}]

        noticies = portal['ca']['noticies']['aggregator']
        noticias = portal['es']['noticias']['aggregator']
        news = portal['en']['news']['aggregator']
        noticies.query = NEWS_QUERY
        noticias.query = NEWS_QUERY
        news.query = NEWS_QUERY
        import transaction
        transaction.commit()
        output.append(
            '{}: Aggregator News collection successfully updated in'.format(portal.id))
        return '\n'.join(output)


class bulk_change_creator(BrowserView):
    """
Modifica el creador dels contingut de X a Y

Paràmetres:
- old_creator
- new_creator
- change_modification_date
    """

    STATUS_oldcreators = u"You must select one old creator."
    STATUS_newcreators = u"You must select one new creator."
    STATUS_samecreator = u"You must select different creators."
    STATUS_updated = u"%s objects updated."
    status = []

    render = ViewPageTemplateFile("templates/bulk_change_creator.pt")

    @property
    def catalog(self):
        return api.portal.get_tool(name='portal_catalog')

    @property
    def membership(self):
        return api.portal.get_tool(name='portal_membership')

    def old_creator(self):
        return self.request.form.get('old_creator', '')

    def new_creator(self):
        return self.request.form.get('new_creator', '')

    def change_modification_date(self):
        return self.request.form.get('change_modification_date', False)

    def get_sorted_list(self, user_list, user_old, user_id_lambda):
        ret_list = []
        for user in user_list:
            if not user:
                continue
            userid = user_id_lambda(user)
            info = self.membership.getMemberInfo(userid)
            if info and info['fullname']:
                d = dict(id=userid, name="%s (%s)" %
                         (info['fullname'], userid))
            else:
                d = dict(id=userid, name=userid)
            d['selected'] = 1 if userid in user_old else 0
            ret_list.append(d)

        return sorted(ret_list, key=lambda a: str(a['id']).lower())

    def list_creators(self):
        creator_list = []
        for brain in self.catalog(path=self.context.absolute_url_path()):
            creators = brain.getObject().listCreators()
            for creator in creators:
                if creator not in creator_list:
                    creator_list.append(creator)
        return self.get_sorted_list(
            creator_list,  # list of creators
            self.old_creator(),  # prev selected creators
            lambda element: element)

    def __call__(self):
        """ Main method """
        if 'submit' in self.request.form:

            old_creator = self.old_creator()
            new_creator = self.new_creator()
            change_modification_date = self.change_modification_date()
            self.status = []

            ok = True
            if old_creator == '':
                self.status.append(self.STATUS_oldcreators)
                ok = False
            if new_creator == '':
                self.status.append(self.STATUS_newcreators)
                ok = False
            if old_creator == new_creator:
                self.status.append(self.STATUS_samecreator)
                ok = False

            if ok:
                count = 0
                acl_users = getattr(self.context, 'acl_users')
                user = acl_users.getUserById(new_creator)

                valid_user = True
                if user is None:
                    user = self.membership.getMemberById(new_creator)
                    if user is None:
                        valid_user = False
                        self.status.append('WARNING: Could not find '
                                           'user %s !' % new_creator)

                header_index = len(self.status)
                self.status.append('')
                abspath = self.context.absolute_url_path()
                for brain in self.catalog(path=abspath):
                    obj = brain.getObject()
                    creators = list(obj.listCreators())
                    if old_creator in creators:
                        if valid_user:
                            obj.changeOwnership(user)
                        if new_creator in creators:
                            index1 = creators.index(old_creator)
                            index2 = creators.index(new_creator)
                            creators[min(index1, index2)] = new_creator
                            del creators[max(index1, index2)]
                        else:
                            creators[creators.index(old_creator)] = new_creator

                        obj.setCreators(creators)
                        if change_modification_date:
                            obj.reindexObject()
                        else:
                            old_modification_date = obj.ModificationDate()
                            obj.reindexObject()
                            obj.setModificationDate(old_modification_date)
                            obj.reindexObject(idxs=['modified'])

                        self.status.append(brain.getPath())
                        count += 1

                self.status[header_index] = self.STATUS_updated % count

        return self.render()


class add_permissions_plantilles(BrowserView):
    """
Afegir permissos en la carpeta de plantilles
    """

    def __call__(self, portal=None):
        try:
            portal = api.portal.get()
            plantilles = portal['plantilles']
            plantilles.manage_permission('Add portal content', [
                                         'Contributor', 'Manager', 'Owner', 'WebMaster', 'Editor'], acquire=0)
            plantilles.manage_permission('plone.app.contenttypes: Add Document', [
                                         'Contributor', 'Manager', 'Owner', 'Site Administrator', 'WebMaster', 'Editor'], acquire=0)
            plantilles.manage_permission('plone.app.contenttypes: Add Folder', [
                                         'Contributor', 'Manager', 'Owner', 'Site Administrator', 'WebMaster', 'Editor'], acquire=0)
            transaction.commit()
            return 'OK'
        except:
            return 'KO'


class preserveUUIDs(BrowserView):
    """
preserveUUIDs
    """

    def __call__(self):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        portal = api.portal.get()
        soup = get_soup('uuid_preserver', portal)
        pc = api.portal.get_tool('portal_catalog')
        results = pc.searchResults()

        for result in results:
            record = Record()
            record.attrs['uuid'] = result.UID
            record.attrs['path'] = result.getPath()
            soup.add(record)
            logger.warning('Preserving {}: {}'.format(
                result.getPath(), result.UID))


class rebuildUUIDs(BrowserView):
    """
rebuildUUIDs
    """

    def __call__(self):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        portal = api.portal.get()
        soup = get_soup('uuid_preserver', portal)
        pc = api.portal.get_tool('portal_catalog')
        results = pc.searchResults()

        for result in results:
            obj = [r for r in soup.query(Eq('path', result.getPath()))]
            if obj:
                try:
                    realobj = result.getObject()
                    IMutableUUID(realobj).set(str(obj[0].attrs['uuid']))
                    realobj.reindexObject(idxs=['UID'])
                    logger.warning('Set UUID per {}'.format(result.getPath()))
                except:
                    logger.warning(
                        'Can\'t set UUID for {}'.format(result.getPath()))


class configure_site_cache(BrowserView):
    """
Vista que configura la caché
    """

    def __call__(self):
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)

        context = aq_inner(self.context)
        from Products.GenericSetup.tests.common import DummyImportContext
        from plone.app.registry.exportimport.handler import RegistryImporter
        from genweb6.core.browser.cachesettings import cacheprofile
        from plone.cachepurging.interfaces import ICachePurgingSettings
        contextImport = DummyImportContext(context, purge=False)
        registry = queryUtility(IRegistry)
        importer = RegistryImporter(registry, contextImport)
        importer.importDocument(cacheprofile)

        cachepurginsettings = registry.forInterface(ICachePurgingSettings)

        varnish_url = os.environ.get('varnish_url', False)
        logger = logging.getLogger(
            'Genweb: Executing configure cache on site -')
        logger.info('%s' % self.context.id)
        if varnish_url:
            cachepurginsettings.cachingProxies = (varnish_url,)
            logger.info('Successfully set caching for this site')
            return 'Successfully set caching for this site.'
        else:
            logger.info(
                'There are not any varnish_url in the environment. No caching proxy could be configured.')
            return 'There are not any varnish_url in the environment. No caching proxy could be configured.'


class refresh_uids(BrowserView):
    """
Refresca les UIDs
    """

    render = ViewPageTemplateFile("templates/origin_root_path.pt")

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

        return self.render()


class fix_record(BrowserView):
    """
Soluciona el problema de KeyError quan la plonesite es mou del Zeo original
    """

    def __call__(self):
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


class change_tiny_css(BrowserView):
    """
Canvia la url dels css del TinyMCE
    """

    def __call__(self):
        api.portal.set_registry_record('plone.content_css', ['++theme++genweb6.theme/theme.min.css'])
        transaction.commit()
        return 'OK'
