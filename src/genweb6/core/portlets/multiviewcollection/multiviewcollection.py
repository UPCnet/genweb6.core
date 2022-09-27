# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import CatalogSource
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import GenwebMessageFactory as _
from genweb6.core.utils import toLocalizedTime

import random
import secrets


VIEW_TYPE_LIST = 'list'
VIEW_TYPE_IMG_LEFT_TITLE_RIGHT = 'img_left_title_right'
VIEW_TYPE_IMG_UP_TITLE_DOWN = 'img_up_title_down'
VIEW_TYPE_IMG_UP_TITLE_DOWN_2COLUMNS = 'img_up_title_down_2columns'
VIEW_TYPE_IMG_UP_TITLE_DOWN_3COLUMNS = 'img_up_title_down_3columns'
VIEW_TYPE_IMG_UP_TITLE_DOWN_4COLUMNS = 'img_up_title_down_4columns'
VIEW_TYPE_SIMPLE_CAROUSEL = 'simple_carousel'
VIEW_TYPE_MULTIPLE_CAROUSEL = 'multiple_carousel'

vocabulary_view_type = SimpleVocabulary([
    SimpleTerm(
        value=VIEW_TYPE_LIST,
        title=_(u'List view')),
    SimpleTerm(
        value=VIEW_TYPE_IMG_LEFT_TITLE_RIGHT,
        title=_(u'Normal view')),
    SimpleTerm(
        value=VIEW_TYPE_IMG_UP_TITLE_DOWN,
        title=_(u'Full view')),
    SimpleTerm(
        value=VIEW_TYPE_IMG_UP_TITLE_DOWN_2COLUMNS,
        title=_(u'Full2cols view')),
    SimpleTerm(
        value=VIEW_TYPE_IMG_UP_TITLE_DOWN_3COLUMNS,
        title=_(u'Full3cols view')),
    SimpleTerm(
        value=VIEW_TYPE_IMG_UP_TITLE_DOWN_4COLUMNS,
        title=_(u'Full4cols view')),
    SimpleTerm(
        value=VIEW_TYPE_SIMPLE_CAROUSEL,
        title=_(u'Simple carousel view')),
    SimpleTerm(
        value=VIEW_TYPE_MULTIPLE_CAROUSEL,
        title=_(u'Multiple carousel view')),
])


class IMultiviewCollectionPortlet(IPortletDataProvider):
    """
    Renders a collection in multiple ways.
    """
    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    show_title = schema.Bool(
        title=_(u"Mostra el títol?"),
        description=_(
            u"Marqueu aquesta casella si voleu que es mostri el títol del portlet"),
        required=False,
        default=True)

    target_collection = RelationChoice(
        title=_(u"Target collection"),
        description=_(u"Find the collection which provides the items to list"),
        required=True,
        source=CatalogSource(portal_type=['Topic', 'Collection']))

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Specify the maximum number of items to show in the "
                      u"portlet. Leave this blank to show all items."),
        required=False)

    random = schema.Bool(
        title=_(u"Select random items"),
        description=_(u"If enabled, items will be selected randomly from the "
                      u"collection, rather than based on its sort order."),
        required=False,
        default=False)

    show_more = schema.Bool(
        title=_(u"Show more... link"),
        description=_(u"If enabled, a more... link will appear in the footer "
                      u"of the portlet, linking to the underlying "
                      u"Collection."),
        required=False,
        default=True)

    show_dates = schema.Bool(
        title=_(u"Show dates"),
        description=_(u"If enabled, effective dates will be shown underneath "
                      u"the items listed."),
        required=False,
        default=False)

    exclude_context = schema.Bool(
        title=_(u"Exclude the Current Context"),
        description=_(
            u"If enabled, the listing will not include the current item the "
            u"portlet is rendered for if it otherwise would be."),
        required=False,
        default=True)

    view_type = schema.Choice(
        title=_(u'View type'),
        description=_(u'Choose how the portlet must be rendered'),
        required=True,
        vocabulary=vocabulary_view_type,
        default=VIEW_TYPE_LIST)


@implementer(IMultiviewCollectionPortlet)
class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    header = u""
    target_collection = None
    limit = None
    random = False
    show_more = True
    show_dates = False
    exclude_context = False
    view_type = VIEW_TYPE_LIST

    def __init__(self, header=u"", show_title=True, target_collection=None,
                 limit=None, random=False, show_more=True, show_dates=False,
                 exclude_context=True, view_type=VIEW_TYPE_LIST):
        self.header = header
        self.show_title = show_title
        self.target_collection = target_collection
        self.limit = limit
        self.random = random
        self.show_more = show_more
        self.show_dates = show_dates
        self.exclude_context = exclude_context
        self.view_type = view_type

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


class Renderer(base.Renderer):

    TEMPLATE_FOLDER = 'templates'
    TEMPLATE_FILE = {
        VIEW_TYPE_LIST: 'list.pt',
        VIEW_TYPE_IMG_LEFT_TITLE_RIGHT: 'img_left_title_right.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN: 'img_up_title_down.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN_2COLUMNS: 'img_up_title_down.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN_3COLUMNS: 'img_up_title_down.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN_4COLUMNS: 'img_up_title_down.pt',
        VIEW_TYPE_SIMPLE_CAROUSEL: 'carousel.pt',
        VIEW_TYPE_MULTIPLE_CAROUSEL: 'multiple_carousel.pt',
    }
    SUMMARY_LENGTH_MAX = 200

    def render(self):
        view_type = getattr(self.data, 'view_type', VIEW_TYPE_LIST)
        return ViewPageTemplateFile('{folder}/{file}'.format(
            folder=Renderer.TEMPLATE_FOLDER,
            file=Renderer.TEMPLATE_FILE[view_type]))(self)

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return len(self.results())

    @property
    def token(self):
        return secrets.token_hex(16)

    def showTitle(self):
        return self.data.show_title

    def show_time(self):
        return self.data.show_dates

    def more_info(self):
        return self.data.show_more

    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()

    def collection_url_rss(self):
        collection = self.collection_url()
        if collection is None:
            return None
        else:
            return collection + "/RSS"

    def css_class(self):
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-collection-%s" % normalizer.normalize(header)

    def published_news_items_group_by_x(self, num):
        result = []
        for count in range(num):
            result.append([])

        pos = 0
        for new in self.result_dicts():
            result[pos].append(new)
            pos = 0 if pos == (num - 1) else pos + 1
        return result

    def published_news_items_group_by_two(self):
        return self.published_news_items_group_by_x(2)

    def published_news_items_group_by_three(self):
        return self.published_news_items_group_by_x(3)

    def published_news_items_group_by_four(self):
        return self.published_news_items_group_by_x(4)

    def result_dicts(self):
        """
        Transform results into dictionaries of results containing only the data
        to render from templates.
        """
        view_type = getattr(self.data, 'view_type', VIEW_TYPE_LIST)
        col = 12
        if view_type == VIEW_TYPE_IMG_UP_TITLE_DOWN_2COLUMNS:
            col = 6
        elif view_type == VIEW_TYPE_IMG_UP_TITLE_DOWN_3COLUMNS:
            col = 4
        elif view_type == VIEW_TYPE_IMG_UP_TITLE_DOWN_4COLUMNS:
            col = 3

        result_dicts = []
        for index, result in enumerate(self.results(), start=0):
            result_obj = result.getObject()
            result_image = getattr(result_obj, 'image', None)
            try:
                result_description = result.description
            except:
                try:
                    result_description = result.Description()
                except:
                    result_description = ''

            date = toLocalizedTime(self, result.EffectiveDate())
            if not date:
                date = toLocalizedTime(self, result.modified)

            result_dicts.append(dict(
                date=date,
                description=self._summarize(result_description),
                col=col,
                image=result_image,
                image_caption=getattr(result_obj, 'image_caption', None),
                image_src=("{0}/@@images/image/large".format(result.getURL()) if result_image else None),
                portal_type=normalizeString(result.portal_type),
                title=result.title_or_id(),
                url=result.getURL(),
                active=index == 0,
                index=index,
            ))

        return result_dicts

    def _summarize(self, text):
        summary = text
        if len(summary) > Renderer.SUMMARY_LENGTH_MAX:
            summary = text[:Renderer.SUMMARY_LENGTH_MAX]
            last_space = summary.rfind(' ')
            last_space = -3 if last_space == -1 else last_space
            summary = summary[:last_space] + '...'
        return summary

    @memoize
    def results(self):
        if self.data.random:
            return self._random_results()
        else:
            return self._standard_results()

    def _standard_results(self):
        results = []
        collection = self.collection()
        if collection is not None:
            context_path = '/'.join(self.context.getPhysicalPath())
            exclude_context = getattr(self.data, 'exclude_context', False)
            limit = self.data.limit
            if limit and limit > 0:
                # pass on batching hints to the catalog
                results = collection.queryCatalog(
                    batch=True, b_size=limit + exclude_context)
                results = results._sequence
            else:
                results = collection.queryCatalog()
            if exclude_context:
                results = [
                    brain for brain in results
                    if brain.getPath() != context_path]
            if limit and limit > 0:
                results = results[:limit]
        return results

    def _random_results(self):
        # intentionally non-memoized
        results = []
        collection = self.collection()
        if collection is not None:
            context_path = '/'.join(self.context.getPhysicalPath())
            exclude_context = getattr(self.data, 'exclude_context', False)
            results = collection.queryCatalog(sort_on=None)
            if results is None:
                return []
            limit = self.data.limit and min(len(results), self.data.limit) or 1

            if exclude_context:
                results = [
                    brain for brain in results
                    if brain.getPath() != context_path]
            if len(results) < limit:
                limit = len(results)
            results = random.sample(results, limit)

        return results

    @memoize
    def collection(self):
        collection_path = self.data.target_collection

        if collection_path and isinstance(collection_path, RelationValue):
            collection_path = collection_path.to_path
        else:
            return None

        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        result = portal.unrestrictedTraverse(collection_path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
        return result

    def include_empty_footer(self):
        """
        Whether or not to include an empty footer element when the more
        link is turned off.
        Always returns True (this method provides a hook for
        sub-classes to override the default behaviour).
        """
        return True


class AddForm(base.AddForm):

    schema = IMultiviewCollectionPortlet
    label = _(u"Add Multi-view Collection Portlet")
    description = _(u"This portlet displays a listing of items from a "
                    u"Collection.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = IMultiviewCollectionPortlet
    label = _(u"Edit Multi-view Collection Portlet")
    description = _(u"This portlet displays a listing of items from a "
                    u"Collection.")
