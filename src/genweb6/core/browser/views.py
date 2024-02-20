# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.login.login import LoginForm
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from bs4 import BeautifulSoup
from plone import api
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.base.interfaces import ILoginForm
from plone.batching import Batch
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.contentprovider import interfaces
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

from genweb6.core import _
from genweb6.core.adapters import IImportant
from genweb6.core.interfaces import IEventFolder
from genweb6.core.interfaces import IHomePage
from genweb6.core.portlets.manage_portlets.manager import ISpanStorage
from genweb6.core.utils import json_response
from genweb6.core.utils import pref_lang
from genweb6.theme.theme.tinymce_templates.templates import templates

from genweb6.core.purge import purge_varnish_paths
from zope.ramcache import ram

import unicodedata

PLMF = MessageFactory('plonelocales')
import time
import logging

LOGGER = logging.getLogger("genweb6.core")


class GetDXDocumentText(BrowserView):

    def __call__(self):
        return self.context.text.output


class GetDXDocumentTextStyle(BrowserView):

    def textOutput(self):
        return self.context.text.output


class GetDXDocumentTextTinyMCE(BrowserView):

    def __call__(self):
        soup = BeautifulSoup(self.context.text.output, "html.parser")
        for mce in soup.find_all('div', class_="mceTmpl"):
            classes = mce.get("class", [])
            classes.remove("mceTmpl")
        return '<div class="mceTmpl">' + soup.decode() + '</div>'


class TemplateList(BrowserView):

    @json_response
    def __call__(self):
        default_templates = templates.copy()
        portal = api.portal.get()
        portal_url = portal.absolute_url()

        lang = pref_lang()
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'

        results = []
        for template in default_templates:
            results.append({'title': template.get('title-' + lang, 'Error title'),
                            'description': template.get('description-' + lang, ''),
                            'url': portal_url + '/' + template.get('url', '')})

        pc = api.portal.get_tool(name='portal_catalog')
        plantilles = pc.searchResults(portal_type='Document',
                                      review_state=['published', 'intranet'],
                                      sort_on='getObjPositionInParent',
                                      path='/'.join(portal.getPhysicalPath()) + '/plantilles')

        for plantilla in plantilles:
            results.append({'title': plantilla.Title,
                            'description': plantilla.Description,
                            'url': plantilla.getURL() + '/genweb.get.dxdocument.text.tinymce'})

        return results


class gwToggleIsImportant(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        is_important = IImportant(context).is_important
        if is_important:
            IImportant(context).is_important = False
            confirm = _(u'L\'element s\'ha desmarcat com important')
        else:
            IImportant(context).is_important = True
            confirm = _(u'L\'element s\'ha marcat com important')

        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())


class HomePageBase(BrowserView):

    """
    Base methods for ease the extension of the genweb homePage view. Just
    define a new class inheriting from this one and redefine the basic
    grokkers like:

    Overriding the one in this module (homePage) with a more specific
    interface.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portlet_container = None

    def getPortletContainer(self):
        # inicio = time.time()
        context = aq_inner(self.context)
        container = context

        # Portlet container will be in the context,
        # Except in the portal root, when we look for an alternative
        if INavigationRoot.providedBy(self.context):
            pc = api.portal.get_tool(name='portal_catalog')
            # Add the use case of mixin types of IHomepages. The main ones of a
            # non PAM-enabled site and the possible inner ones.
            result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                      portal_type='Document',
                                      Language=pref_lang())
            if result:
                # Return the object without forcing a getObject()
                container = getattr(context, result[0].id, context)
        # elapsed_fin= time.time() - inicio
        # LOGGER.error("Tiempo /genweb6/core/browser/views.py getPortletContainer Elapsed time: %0.10f seconds." % elapsed_fin)
        self.portlet_container = container

    def renderProviderByName(self, provider_name):
        #ini_render = time.time()
        provider = queryMultiAdapter(
            (self.portlet_container, self.request, self),
            interfaces.IContentProvider, provider_name)
        provider.update()
        valor = provider.render()
        #elapsed_fin_render= time.time() - ini_render
        #LOGGER.error("Tiempo /genweb6/core/browser/views.py renderProviderByName Elapsed time: %0.10f seconds." % elapsed_fin_render)

        return valor

    def getColValueForManager(self, manager):
        #ini_getcol = time.time()
        portletManager = getUtility(IPortletManager, manager)
        spanstorage = getMultiAdapter(
            (self.portlet_container, portletManager),
            ISpanStorage)
        span = spanstorage.span
        #elapsed_fin_getcol= time.time() - ini_getcol
        #LOGGER.error("Tiempo /genweb6/core/browser/views.py getColValueForManager Elapsed time: %0.10f seconds." % elapsed_fin_getcol)
        if span:
            return span
        else:
            return '4'

    def have_portlets(self, manager_name, view=None):
        """Determine whether a column should be shown. The left column is called
        plone.leftcolumn; the right column is called plone.rightcolumn.
        """
        #ini_havep = time.time()
        force_disable = self.request.get('disable_' + manager_name, None)
        if force_disable is not None:
            return not bool(force_disable)

        context = self.portlet_container
        if view is None:
            view = self

        manager = queryUtility(IPortletManager, name=manager_name)
        if manager is None:
            return False

        renderer = queryMultiAdapter(
            (context, self.request, view, manager),
            IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter(
                (context, self.request, self, manager),
                IPortletManagerRenderer)
        #elapsed_fin_havep= time.time() - ini_havep
        #LOGGER.error("Tiempo /genweb6/core/browser/views.py have_portlets Elapsed time: %0.10f seconds." % elapsed_fin_havep)
        return renderer.visible

    def is_visible(self):
        """ This method lookup for the physical welcome page and checks if the
            user has the permission to view it. If it doesn't raises an
            unauthorized (login)
        """
        #ini_visible = time.time()
        portal = api.portal.get()
        pc = api.portal.get_tool('portal_catalog')
        result = pc.unrestrictedSearchResults(object_provides=IHomePage.__identifier__,
                                              Language=pref_lang())
        #elapsed_fin_visible= time.time() - ini_visible
        #LOGGER.error("Tiempo /genweb6/core/browser/views.py is_visible Elapsed time: %0.10f seconds." % elapsed_fin_visible)
        if result:
            portal.restrictedTraverse(result[0].getPath())
            return True
        else:
            return False


@implementer(IHomePage)
class homePage(HomePageBase):
    """ This is the special view for the homepage containing support for the
        portlet managers provided by the package genweb.portlets.
        It's restrained to IGenwebTheme layer to prevent it will interfere with
        the one defined in the Genweb legacy theme (v3.5).
    """
    pass


@implementer(IHomePage)
class subHomePage(HomePageBase):
    """ This is the special view for the subhomepage containing support for the
        portlet managers provided by the package genweb.portlets.
        This is the PAM aware default LRF homepage view.
        It is also used in IFolderish (DX and AT) content for use in inner landing
        pages.
    """
    pass


@implementer(IHomePage)
class SubhomeView(HomePageBase):
    """ This is the special view for the subhomepage containing support for the
        portlet managers provided by the package genweb.portlets.
        This is the PAM aware default LRF homepage view.
        It is also used in IFolderish (DX and AT) content for use in inner landing
        pages.
    """
    pass


class PortletEventsView(BrowserView):

    def published_events(self):
        return self._data()

    def published_events_expanded(self):
        """
        Return expanded ongoing events, i.e. taking into account their
        occurrences in case they are recurrent events.
        """
        return [self.event_to_view_obj(event) for event in get_events(
            self.context,
            ret_mode=2,
            start=localized_now(),
            expand=True,
            sort='start',
            limit=5 if 'limit' not in self.request.form else self.request.form['limit'],
            review_state='published')]

    def event_to_view_obj(self, event):
        local_start = DateTime(event.start)
        local_start_str = local_start.strftime('%d/%m/%Y')
        local_end = DateTime(event.end)
        local_end_str = local_end.strftime('%d/%m/%Y')
        is_same_day = local_start_str == local_end_str
        return dict(
            class_li='' if is_same_day else 'multidate',
            class_a='' if is_same_day else 'multidate-before',
            date_start=local_start_str,
            date_end=local_end_str,
            day_start=int(local_start.strftime('%d')),
            day_end=int(local_end.strftime('%d')),
            is_multidate=not is_same_day,
            month_start=self.get_month_name(local_start.strftime('%m')),
            month_start_abbr=self.get_month_name(
                local_start.strftime('%m'), month_format='a'),
            month_end=self.get_month_name(local_end.strftime('%m')),
            month_end_abbr=self.get_month_name(
                local_end.strftime('%m'), month_format='a'),
            title=event.Title,
            url=event.absolute_url(),
        )

    def get_month_name(self, month, month_format=''):
        context = aq_inner(self.context)
        self._ts = getToolByName(context, 'translation_service')
        return PLMF(self._ts.month_msgid(int(month), format=month_format),
                    default=self._ts.month_english(int(month)))

    def all_events_link(self):
        pc = api.portal.get_tool('portal_catalog')
        events_folder = pc.searchResults(
            object_provides=IEventFolder.__identifier__, Language=pref_lang())

        if events_folder:
            return '%s' % events_folder[0].getURL()
        else:
            return ''


class FilteredContentsSearchView(BrowserView):
    """ Filtered content search view for every folder. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.query = self.request.form.get('q', '')
        if self.request.form.get('t', ''):
            self.tags = [v for v in self.request.form.get('t').split(',')]
        else:
            self.tags = []

    def getTags(self):
        portal = getSite()
        pc = getToolByName(portal, "portal_catalog")
        tags = []
        results = pc.searchResults(
            path={'query': '/'.join(self.context.getPhysicalPath()),
                  'depth': 1},
            exclude_from_nav=False)
        for recurs in results:
            tags += list(set(recurs.Subject))

        listTags = list(dict.fromkeys(tags))
        listTags.sort(key=lambda key: unicodedata.normalize(
            'NFKD', key).encode('ascii', errors='ignore'))

        return listTags

    def get_batched_contenttags(self, query=None, batch=True, b_size=10, b_start=0):
        pc = getToolByName(self.context, "portal_catalog")
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        r_results = pc.searchResults(path={'query': path, 'depth': 1},
                                     exclude_from_nav=False)
        batch = Batch(r_results, b_size, b_start)
        return batch

    def get_contenttags_by_query(self):
        pc = getToolByName(self.context, "portal_catalog")
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        if not self.query and not self.tags:
            return self.getContent()

        if not self.query == '':
            multispace = u'　'
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query) + '*'

            if self.tags:
                tmp_results = pc.searchResults(
                    path={'query': path, 'depth': 1},
                    exclude_from_nav=False, SearchableText=query,
                    Subject={'query': self.tags, 'operator': 'and'},
                    sort_on='getObjPositionInParent')

                # BUSCAR PER ETIQUETES
                r_results = [item for item in tmp_results
                             if
                             all(
                                 unicodedata.normalize('NFKD', x)
                                 in unicodedata.normalize(
                                     'NFKD', item.Title + " " + item.Description).lower()
                                 + " " + unicodedata.normalize(
                                     'NFKD', ' '.join(item.Subject)).lower()
                                 for x in self.query.split())]
            else:
                tmp_results = pc.searchResults(path={'query': path, 'depth': 1},
                                               exclude_from_nav=False,
                                               SearchableText=query,
                                               sort_on='getObjPositionInParent')

                r_results = [
                    item for item in tmp_results
                    if
                    all(
                        unicodedata.normalize('NFKD', x).
                        lower() in unicodedata.normalize(
                            'NFKD', item.Title + " " + item.Description).lower() + " " +
                        unicodedata.normalize('NFKD', ' '.join(item.Subject)).lower()
                        for x in self.query.split())]

            return r_results
        else:
            r_results = pc.searchResults(
                path={'query': path, 'depth': 1},
                exclude_from_nav=False, Subject={'query': self.tags, 'operator': 'and'},
                sort_on='getObjPositionInParent')

            return r_results
            # return self.get_batched_contenttags(query=None, batch=True, b_size=10, b_start=0)

    def get_tags_by_query(self):
        pc = getToolByName(self.context, "portal_catalog")

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        if not self.query == '':
            multispace = u'　'
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query)
            path = self.context.absolute_url_path()

            r_results = pc.searchResults(path=path,
                                         Subject=query)

            return r_results
        else:
            return self.get_batched_contenttags(
                query=None, batch=True, b_size=10, b_start=0)

    def get_container_path(self):
        return self.context.absolute_url() + '/search_filtered_content_pretty'

    def getContent(self):
        portal = api.portal.get()
        catalog = getToolByName(portal, 'portal_catalog')
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        items = catalog.searchResults(path={'query': path, 'depth': 1},
                                      exclude_from_nav=False,
                                      sort_on='getObjPositionInParent')

        return items


class FilteredContentsSearchCompleteView(FilteredContentsSearchView):
    """ Filtered content search view for every folder. """

    def get_contenttags_by_query(self):
        pc = getToolByName(self.context, "portal_catalog")
        path = self.context.getPhysicalPath()
        path = "/".join(path)

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        if not self.query and not self.tags:
            return self.getContent()

        results = []
        if not self.query == '':
            multispace = u'　'
            for char in ('?', '-', '+', '*', multispace):
                self.query = self.query.replace(char, ' ')

            query = self.query.split()
            query = " AND ".join(query)
            query = quote_bad_chars(query) + '*'

            if self.tags:
                results = pc.searchResults(
                    path={'query': path, 'depth': 1},
                    exclude_from_nav=False, SearchableText=query,
                    Subject={'query': self.tags, 'operator': 'and'},
                    sort_on='getObjPositionInParent')

            else:
                results = pc.searchResults(path={'query': path, 'depth': 1},
                                           exclude_from_nav=False,
                                           SearchableText=query,
                                           sort_on='getObjPositionInParent')

        else:
            results = pc.searchResults(path={'query': path, 'depth': 1},
                                       exclude_from_nav=False,
                                       Subject={'query': self.tags, 'operator': 'and'},
                                       sort_on='getObjPositionInParent')

        return results

    def get_container_path(self):
        return self.context.absolute_url() + '/search_complete_filtered_content_pretty'


class FolderIndexView(BrowserView):
    """ Render the title of items and its children
    """

    # number of levels to show, if greater than 3 should modify template
    MAX_LEVEL = 3

    def update(self):
        self.theme = 'Genweb'

    def genwebTheme(self):
        return self.theme == 'Genweb'

    def upcTheme(self):
        return self.theme == 'UPC'

    def items(self):
        return self._data()

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        self.catalog = getToolByName(context, 'portal_catalog')
        folder_path = '/'.join(context.getPhysicalPath())
        results = self.find_items_in_path(folder_path, 1)

        return results

    def find_items_in_path(self, folder_path, level):
        # find items in folder sorted manually by user
        query_results = self.catalog(
            path={'query': folder_path, 'depth': 1},
            sort_on='getObjPositionInParent')
        # list of objects (brain, results2) results2 only has value if item is a Folder
        results = []
        for item in query_results:
            results2 = []
            if level < FolderIndexView.MAX_LEVEL:
                if item.Type == 'Folder':  # find its children
                    folder_path_2 = folder_path + '/' + item.id
                    results2 = self.find_items_in_path(folder_path_2, level + 1)
            result = FolderIndexItem(item, results2, self)

            results.append(result)
        return results


class FolderIndexItem():
    """ Brain and its children
    """

    def __init__(self, brain, children, context):
        self.brain = brain
        self.children = children
        self.context = context

    def getChildren(self):
        return self.children

    def getClass(self):
        if self.isFolder():
            return 'span4'
        else:
            return 'span12'

    def hasImg(self):
        pathImg = self.brain.getPath() + '-img'
        if self.context.catalog.searchResults(path=pathImg):
            return True
        else:
            return False

    def getDescription(self):
        return self.brain.Description

    def getPath(self):
        return self.brain.getURL()

    def getPathImg(self):
        return self.brain.getURL() + '-img'

    def getTitle(self):
        return self.brain.Title

    def isLink(self):
        return self.brain.Type == "Link"

    def isFolder(self):
        return self.brain.Type == "Folder"

    def isVisible(self):
        # test if excluded from nav and has valid title
        return not self.brain.exclude_from_nav and len(self.brain.Title) > 0


@implementer(ILoginForm)
class GWLoginForm(LoginForm):
    pass


class GWPurgeCacheVarnish(BrowserView):

    def __call__(self):

        ram.caches.clear()
        paths = []
        paths.append('/_purge_all')

        purge_varnish_paths(self, paths)

        message = _(u'Purged')

        IStatusMessage(self.request).addStatusMessage(message, type='info')
        return self.request.response.redirect(self.context.absolute_url())
