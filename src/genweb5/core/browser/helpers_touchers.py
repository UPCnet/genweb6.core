# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IApplication
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PortalTransforms.transforms.pdf_to_text import pdf_to_text

from plone import api
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.upgrades import use_new_view_names
from plone.dexterity.content import Container
from plone.dexterity.utils import createContentInContainer
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.subrequest import subrequest
from souper.soup import get_soup
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import alsoProvides

from genweb5.core import HAS_DXCT
from genweb5.core import HAS_PAM
from genweb5.core.browser.helpers import listPloneSites
from genweb5.core.browser.helpers import setupInstallProfile
from genweb5.core.browser.plantilles import get_plantilles
from genweb5.core.interfaces import IHomePage
from genweb5.core.utils import json_response

import pkg_resources
import transaction

try:
    pkg_resources.get_distribution('plone4.csrffixes')
except pkg_resources.DistributionNotFound:
    CSRF = False
else:
    from plone.protect.interfaces import IDisableCSRFProtection
    CSRF = True

if HAS_PAM:
    from plone.app.multilingual.browser.setup import SetupMultilingualSite


class makeMeaHomePage(BrowserView):
    """ makeMeaHomePage """

    def __call__(self):
        alsoProvides(self.context, IHomePage)
        if HAS_DXCT:
            from plone.app.contenttypes.interfaces import IFolder
            if IFolder.providedBy(self.context):
                self.context.setLayout('homepage')
        return self.request.response.redirect(self.context.absolute_url())


class makeMeaSubHomePage(BrowserView):
    """ makeMeaSubHomePage """

    def __call__(self):
        alsoProvides(self.context, IHomePage)
        if HAS_DXCT:
            from plone.app.contenttypes.interfaces import IFolder
            if IFolder.providedBy(self.context):
                self.context.setLayout('subhomepage')
        return self.request.response.redirect(self.context.absolute_url())


class resetLanguage(BrowserView):
    """
        Re-set the language of each LRF according to its name. Execute in an LRF
    """

    def __call__(self):
        from plone.app.multilingual.interfaces import ILanguage
        context = aq_inner(self.context)
        pc = api.portal.get_tool('portal_catalog')
        results = pc.unrestrictedSearchResults(path='/'.join(context.getPhysicalPath()))

        for brain in results:
            ob = brain._unrestrictedGetObject()
            language_aware = ILanguage(ob, None)
            if language_aware is not None:
                language_aware.set_language(self.context.id)
                ob.reindexObject(idxs=['Language', 'TranslationGroup'])


class enablePDFIndexing(BrowserView):
    """ Enable PDF indexing """

    def __call__(self):
        pt = api.portal.get_tool('portal_transforms')
        pt.registerTransform(pdf_to_text())

        return 'Done'


class updateFolderViews(BrowserView):
    """ Update view methods for folder type in the current Plone site. """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        portal.portal_types['Folder'].view_methods = ('listing_view', 'folder_extended', 'album_view', 'summary_view', 'tabular_view', 'full_view', 'folder_index_view', 'filtered_contents_search_pretty_view')
        import transaction
        transaction.commit()
        output.append('{}: Successfully reinstalled'.format(portal.id))
        return '\n'.join(output)


class addFolderView(BrowserView):
    """ Add view method for folder type in the current Plone site. """

    def __call__(self, portal=None):
        output = []
        if 'addview' in self.request.form:
            if not portal:
                portal = api.portal.get()

            views = list(portal.portal_types['Folder'].view_methods)
            view = self.request.form['addview']
            if view not in views:
                views.append(view)
            portal.portal_types['Folder'].view_methods = tuple(views)
            import transaction
            transaction.commit()
            output.append('{}: Successfully added view'.format(portal.id))
            return '\n'.join(output)

        output.append('{}: Error added view, not defined view'.format(portal.id))
        return '\n'.join(output)


class removeFolderView(BrowserView):
    """ Remove view method for folder type in the current Plone site. """

    def __call__(self, portal=None):
        output = []
        if 'removeview' in self.request.form:
            if not portal:
                portal = api.portal.get()

            views = list(portal.portal_types['Folder'].view_methods)
            view = self.request.form['removeview']
            if view in views:
                views.remove(view)
            portal.portal_types['Folder'].view_methods = tuple(views)
            import transaction
            transaction.commit()
            output.append('{}: Successfully removed view'.format(portal.id))
            return '\n'.join(output)

        output.append('{}: Error removed view, not defined view'.format(portal.id))
        return '\n'.join(output)


class checkPloneProductIsInstalled(BrowserView):
    """ Check is installed a product passed by form parameter in the current Plone site. """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        product_name = self.request.form['product_name']
        qi = getToolByName(portal, 'portal_quickinstaller')

        if qi.isProductInstalled(product_name):
            return 'OK\n'


class reinstallPloneProduct(BrowserView):
    """ Reinstalls a product passed by form parameter in the current Plone site. """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        product_name = self.request.form['product_name']
        output = []
        qi = getToolByName(portal, 'portal_quickinstaller')

        if qi.isProductInstalled(product_name):
            qi.uninstallProducts([product_name, ], reinstall=True)
            qi.installProducts([product_name], reinstall=True)
            output.append('{}: Successfully reinstalled {}'.format(portal.id, product_name))
        return '\n'.join(output)


class uninstallPloneProduct(BrowserView):
    """ Uninstall a product passed by form parameter in the current Plone site. """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        product_name = self.request.form['product_name']
        output = []
        qi = getToolByName(portal, 'portal_quickinstaller')

        if qi.isProductInstalled(product_name):
            qi.uninstallProducts([product_name, ], reinstall=False)
            output.append('{}: Successfully uninstalled {}'.format(portal.id, product_name))
        return '\n'.join(output)


class upgradePloneVersion(BrowserView):
    """ Upgrade to the latest Plone version in code """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        # pm = getattr(self.context, 'portal_migration')
        pm = api.portal.get_tool('portal_migration')
        self.request.method = 'POST'
        report = pm.upgrade(
            REQUEST=self.request,
            dry_run=False,
        )
        return report


class setupPAMAgain(BrowserView):
    """ Reinstalls a product passed by form parameter in the current Plone site. """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        from plone.app.multilingual.browser.setup import SetupMultilingualSite
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.context, False)


class deleteNavPortletFromRoot(BrowserView):
    """ Delete NavPortlet from Root """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        # Delete default Navigation portlet on root
        target_manager_root = queryUtility(IPortletManager, name='plone.leftcolumn', context=portal)
        target_manager_root_assignments = getMultiAdapter((portal, target_manager_root), IPortletAssignmentMapping)
        if 'navigation' in target_manager_root_assignments:
            del target_manager_root_assignments['navigation']


class reinstallGWTinyTemplates(BrowserView):
    """ Reinstalls all TinyMCE Templates """

    def __call__(self, portal=None):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        if not portal:
            portal = api.portal.get()

        templates = portal.get('templates', None)
        if templates:
            self.delete_templates(templates)
            for plt in get_plantilles():
                plantilla = self.create_content(templates, 'Document', normalizeString(plt['titol']), title=plt['titol'], description=plt['resum'])
                plantilla.text = IRichText['text'].fromUnicode(plt['cos'])
                plantilla.reindexObject()

    def delete_templates(self, templates):
        for template in templates.objectIds():
            api.content.delete(obj=templates[template])

    def create_content(self, container, portal_type, id, publish=True, **kwargs):
        if not getattr(container, id, False):
            obj = createContentInContainer(container, portal_type, checkConstraints=False, **kwargs)
            if publish:
                self.publish_content(obj)
        return getattr(container, id)

    def publish_content(self, context):
        """ Make the content visible either in both possible genweb.simple and
            genweb.review workflows.
        """
        pw = getToolByName(context, "portal_workflow")
        object_workflow = pw.getWorkflowsFor(context)[0].id
        object_status = pw.getStatusOf(object_workflow, context)
        if object_status:
            api.content.transition(obj=context, transition={'genweb_simple': 'publish', 'genweb_review': 'publicaalaintranet'}[object_workflow])


class removeDuplicatedGenwebSettings(BrowserView):
    """ Remove duplicate (old) Genweb UPC settings in Control Panel """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        portal_controlpanel = api.portal.get_tool('portal_controlpanel')
        portal_controlpanel.unregisterConfiglet('genweb')


class PortalSetupImport(BrowserView):
    """
    Go to portal setup, select profile and import step.
    URL parameters:
      - step: id of the step to import, e.g. 'portlets'.
      - profile: id of the profile or snapshot to select, e.g. 'genweb.upc'.
      - profile_type: type of the selected profile, 'default' by default.
    """

    DEFAULT_PROFILE_TYPE = 'default'

    def __call__(self):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        portal = api.portal.get()
        ps = getToolByName(portal, 'portal_setup')
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
            'profile_type', PortalSetupImport.DEFAULT_PROFILE_TYPE)
        return dict(step=step, profile=profile, profile_type=profile_type)


class changeNewsEventsPortlets(BrowserView):
    """ Replace navigation portlet by categories portlet from news and events
    view methods in the current Plone site. """

    def __call__(self, portal=None):
        output = []
        portal = api.portal.get()

        ps = getToolByName(portal, 'portal_setup')
        ps.runImportStepFromProfile('profile-genweb.theme:default', 'portlets')

        portal_ca = portal['ca']
        portal_es = portal['es']
        portal_en = portal['en']

        self.disinherit_from_parent(portal_ca, portal_es, portal_en)

        self.assign_news_events_listing_portlet(portal_ca['noticies'], 'News')
        self.assign_news_events_listing_portlet(portal_ca['esdeveniments'], 'Events')
        self.assign_news_events_listing_portlet(portal_es['noticias'], 'News')
        self.assign_news_events_listing_portlet(portal_es['eventos'], 'Events')
        self.assign_news_events_listing_portlet(portal_en['news'], 'News')
        self.assign_news_events_listing_portlet(portal_en['events'], 'Events')

        # Set layout for news folders
        portal_en['news'].setLayout('news_listing')
        portal_es['noticias'].setLayout('news_listing')
        portal_ca['noticies'].setLayout('news_listing')

        # Set layout for events folders
        portal_en['events'].setLayout('event_listing')
        portal_es['eventos'].setLayout('event_listing')
        portal_ca['esdeveniments'].setLayout('event_listing')

        import transaction
        transaction.commit()

        output.append('{}: Successfully replaced news_events_listing portlet'.format(portal.id))
        return '\n'.join(output)

    def disinherit_from_parent(self, portal_ca, portal_es, portal_en):
        # Blacklist the left column on portal_ca['noticies'] and portal_ca['esdeveniments'],
        # portal_es['noticias'] and portal_es['eventos'],
        # portal_en['news'] and portal_en['events']
        left_manager = queryUtility(IPortletManager, name=u'plone.leftcolumn')
        blacklist_ca = getMultiAdapter((portal_ca['noticies'], left_manager), ILocalPortletAssignmentManager)
        blacklist_ca.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_ca = getMultiAdapter((portal_ca['esdeveniments'], left_manager), ILocalPortletAssignmentManager)
        blacklist_ca.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_es = getMultiAdapter((portal_es['noticias'], left_manager), ILocalPortletAssignmentManager)
        blacklist_es.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_es = getMultiAdapter((portal_es['eventos'], left_manager), ILocalPortletAssignmentManager)
        blacklist_es.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_en = getMultiAdapter((portal_en['news'], left_manager), ILocalPortletAssignmentManager)
        blacklist_en.setBlacklistStatus(CONTEXT_CATEGORY, True)
        blacklist_en = getMultiAdapter((portal_en['events'], left_manager), ILocalPortletAssignmentManager)
        blacklist_en.setBlacklistStatus(CONTEXT_CATEGORY, True)

    def assign_news_events_listing_portlet(self, portal, obj_type):
        from genweb.theme.portlets.news_events_listing import Assignment as news_events_Assignment

        target_manager_left = queryUtility(IPortletManager, name='plone.leftcolumn', context=portal)
        target_manager_assignments_left = getMultiAdapter((portal, target_manager_left), IPortletAssignmentMapping)
        for portlet in target_manager_assignments_left:
            del target_manager_assignments_left[portlet]
        if 'news_events_listing' not in target_manager_assignments_left:
            target_manager_assignments_left['news_events_listing'] = news_events_Assignment([], obj_type)


class setSitemapDepth(BrowserView):
    """ Set 3 levels of sitemap  """

    def __call__(self, portal=None):
        output = []
        portal = api.portal.get()
        navtree_props = portal.portal_properties.navtree_properties
        navtree_props.sitemapDepth = 4
        import transaction
        transaction.commit()
        output.append('{}: Successfully setted 3 levels in sitemap'.format(portal.id))
        return '\n'.join(output)


class updateLIF_LRF(BrowserView):
    """ Update view methods for LIf and LRF types in the current Plone site """

    def __call__(self, portal=None):
        if not portal:
            portal = api.portal.get()

        output = []
        portal.portal_types['LIF'].view_methods = ('listing_view', 'summary_view', 'tabular_view', 'full_view', 'album_view')
        portal.portal_types['LIF'].default_view = 'tabular_view'
        portal.portal_types['LRF'].view_methods = ('listing_view', 'summary_view', 'tabular_view', 'full_view', 'album_view')
        portal.portal_types['LRF'].default_view = 'tabular_view'
        import transaction
        transaction.commit()
        output.append('{}: Successfully reinstalled'.format(portal.id))
        return '\n'.join(output)


class reinstallGenwebUPCWithLanguages(BrowserView):
    """ Reinstalls genweb.upc keeping published languages in the current Plone site. """

    def __call__(self, portal=None):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        defaultLanguage = api.portal.get_default_language()
        languages = api.portal.get_registry_record(name='genweb.controlpanel.interface.IGenwebControlPanelSettings.idiomes_publicats')
        context = aq_inner(self.context)
        output = []
        qi = getToolByName(context, 'portal_quickinstaller')

        if qi.isProductInstalled('genweb.upc'):
            qi.uninstallProducts(['genweb.upc'], reinstall=True)
            qi.installProducts(['genweb.upc'], reinstall=True)
            pl = api.portal.get_tool('portal_languages')
            pl.setDefaultLanguage(defaultLanguage)
            pl.supported_langs = ['ca', 'es', 'en']
            api.portal.set_registry_record(name='genweb.controlpanel.interface.IGenwebControlPanelSettings.idiomes_publicats', value=languages)
            output.append('{}: Successfully reinstalled genweb upc'.format(context))
        return '\n'.join(output)


class reindexAllPages(BrowserView):
    """ reindexAllPages """

    def __call__(self, portal=None):
        output = []
        portal = api.portal.get()
        context = aq_inner(self.context)
        pc = getToolByName(context, 'portal_catalog')
        brains = pc.searchResults(portal_type='Document')
        for result in brains:
            obj = result.getObject()
            obj.reindexObject()
        import transaction
        transaction.commit()
        output.append('{}: Documents successfully reindexed'.format(portal.id))
        return '\n'.join(output)


class addPermissionsContributor(BrowserView):
    """ add permission to folder contentes when rol is Contributor """

    def __call__(self, portal=None):
        if CSRF:
            alsoProvides(self.request, IDisableCSRFProtection)
        output = []
        portal = api.portal.get()
        roles_of_permission = portal.rolesOfPermission('List folder contents')
        portlets = portal.rolesOfPermission('Portlets: Manage portlets')
        output.append('PREVIOUS (List folder contents): name = {}, selected = {}'.format(roles_of_permission[2]['name'], roles_of_permission[2]['selected']))
        output.append('PREVIOUS (Portlets: Manage portlets): name = {}, selected = {}'.format(portlets[2]['name'], portlets[2]['selected']))
        ps = getToolByName(portal, 'portal_setup')
        ps.runImportStepFromProfile('profile-genweb.core:default', 'rolemap')
        roles_of_permission = portal.rolesOfPermission('List folder contents')
        portlets = portal.rolesOfPermission('Portlets: Manage portlets')
        output.append('AFTER (List folder contents): name = {}, selected = {}'.format(roles_of_permission[2]['name'], roles_of_permission[2]['selected']))
        output.append('AFTER (Portlets: Manage portlets): name = {}, selected = {}'.format(portlets[2]['name'], portlets[2]['selected']))
        output.append('{}: Permissions added'.format(portal.id))
        return '\n'.join(output)


class setFolderIndexViewasDefault(BrowserView):
    """ Set all folders views of this site with the view passed by param """

    def __call__(self, portal=None):
        output = []
        context = aq_inner(self.context)
        view_method = self.request.form['view_method']
        pc = getToolByName(context, 'portal_catalog')
        brains = pc.searchResults(portal_type='Folder')
        for result in brains:
            obj = result.getObject()
            if obj.getDefaultPage() is None:
                obj.setLayout(view_method)
        import transaction
        transaction.commit()
        output.append('{}: Folder view successfully changed'.format(api.portal.get().id))
        return '\n'.join(output)


class addLinkIntoFolderNews(BrowserView):
    """ addLinkIntoFolderNews """

    def __call__(self, portal=None):
        output = []
        portal = api.portal.get()
        noticies = portal['ca']['noticies']
        noticias = portal['es']['noticias']
        news = portal['en']['news']
        from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
        behavior = ISelectableConstrainTypes(noticies)
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(('News Item', 'Folder', 'Image', 'Link'))
        behavior.setImmediatelyAddableTypes(('News Item', 'Folder', 'Image', 'Link'))
        behavior = ISelectableConstrainTypes(noticias)
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(('News Item', 'Folder', 'Image', 'Link'))
        behavior.setImmediatelyAddableTypes(('News Item', 'Folder', 'Image', 'Link'))
        behavior = ISelectableConstrainTypes(news)
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(('News Item', 'Folder', 'Image', 'Link'))
        behavior.setImmediatelyAddableTypes(('News Item', 'Folder', 'Image', 'Link'))
        import transaction
        transaction.commit()
        output.append('{}: Link type added successfully to news folder in'.format(portal.id))
        return '\n'.join(output)


class refactorAggregatorNewsCollection(BrowserView):
    """ refactorAggregatorNewsCollection """

    def __call__(self, portal=None):
        output = []
        NEWS_QUERY = [{'i': u'portal_type', 'o': u'plone.app.querystring.operation.selection.is', 'v': [u'News Item', u'Link']},
                      {'i': u'review_state', 'o': u'plone.app.querystring.operation.selection.is', 'v': [u'published']},
                      {'i': u'path', 'o': u'plone.app.querystring.operation.string.relativePath', 'v': u'..'}]
        portal = api.portal.get()
        noticies = portal['ca']['noticies']['aggregator']
        noticias = portal['es']['noticias']['aggregator']
        news = portal['en']['news']['aggregator']
        noticies.query = NEWS_QUERY
        noticias.query = NEWS_QUERY
        news.query = NEWS_QUERY
        import transaction
        transaction.commit()
        output.append('{}: Aggregator News collection successfully updated in'.format(portal.id))
        return '\n'.join(output)


class translateNews(BrowserView):
    """ translate title and description spanish news"""

    def __call__(self, portal=None):
        output = []
        portal = api.portal.get()
        newsfolder = portal['es']['noticias']
        newsfolder.setTitle('Noticias')
        newsfolder.setDescription('Noticias del sitio')
        newsfolder.reindexObject()

        output.append('{}: Successfully translated news'.format(portal.id))
        return '\n'.join(output)


class bulkChangeCreator(BrowserView):
    """ If the creator of the content is X, change it to Y """

    STATUS_oldcreators = u"You must select one old creator."
    STATUS_newcreators = u"You must select one new creator."
    STATUS_samecreator = u"You must select different creators."
    STATUS_updated = u"%s objects updated."
    status = []

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
        ret_list.sort(lambda a, b:
                      cmp(str(a['id']).lower(), str(b['id']).lower()))
        return ret_list

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

        return ViewPageTemplateFile('helpers_touchers_templates'
                                    '/bulk_change_creator.pt')(self)


class addPermissionsPlantilles(BrowserView):
    """ add permissions in plantilles folder """

    def __call__(self, portal=None):
        try:
            portal = api.portal.get()
            plantilles = portal['plantilles']
            plantilles.manage_permission('Add portal content', ['Contributor', 'Manager', 'Owner', 'WebMaster', 'Editor'], acquire=0)
            plantilles.manage_permission('plone.app.contenttypes: Add Document', ['Contributor', 'Manager', 'Owner', 'Site Administrator', 'WebMaster', 'Editor'], acquire=0)
            plantilles.manage_permission('plone.app.contenttypes: Add Folder', ['Contributor', 'Manager', 'Owner', 'Site Administrator', 'WebMaster', 'Editor'], acquire=0)
            transaction.commit()
            return 'OK'
        except:
            return 'KO'


class preserveUUIDs(BrowserView):

    def __call__(self):
        portal = api.portal.get()
        soup = get_soup('uuid_preserver', portal)
        pc = api.portal.get_tool('portal_catalog')
        results = pc.searchResults()

        for result in results:
            record = Record()
            record.attrs['uuid'] = result.UID
            record.attrs['path'] = result.getPath()
            soup.add(record)
            logger.warning('Preserving {}: {}'.format(result.getPath(), result.UID))


class rebuildUUIDs(BrowserView):

    def __call__(self):
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
                    logger.warning('Can\'t set UUID for {}'.format(result.getPath()))
