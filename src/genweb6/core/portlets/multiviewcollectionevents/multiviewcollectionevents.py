# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
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
from genweb6.core.portlets.multiviewcollection.multiviewcollection import Assignment as MultiviewCollectionAssignment
from genweb6.core.portlets.multiviewcollection.multiviewcollection import IMultiviewCollectionPortlet
from genweb6.core.portlets.multiviewcollection.multiviewcollection import Renderer as MultiviewCollectionRenderer
from genweb6.core.utils import toLocalizedTime

import random
import secrets


VIEW_TYPE_LIST = 'list'
VIEW_TYPE_IMG_LEFT_TITLE_RIGHT = 'img_left_title_right'
VIEW_TYPE_IMG_UP_TITLE_DOWN = 'img_up_title_down'
VIEW_TYPE_IMG_UP_TITLE_DOWN_2COLUMNS = 'img_up_title_down_2columns'
VIEW_TYPE_IMG_UP_TITLE_DOWN_3COLUMNS = 'img_up_title_down_3columns'
VIEW_TYPE_IMG_UP_TITLE_DOWN_4COLUMNS = 'img_up_title_down_4columns'

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
])


class IMultiviewCollectionEventsPortlet(IMultiviewCollectionPortlet):

    view_type = schema.Choice(
        title=_(u'View type'),
        description=_(u'Choose how the portlet must be rendered'),
        required=True,
        vocabulary=vocabulary_view_type,
        default=VIEW_TYPE_LIST)


@implementer(IMultiviewCollectionEventsPortlet)
class Assignment(MultiviewCollectionAssignment):
    pass


class Renderer(MultiviewCollectionRenderer):

    TEMPLATE_FOLDER = 'templates'
    TEMPLATE_FILE = {
        VIEW_TYPE_LIST: 'list.pt',
        VIEW_TYPE_IMG_LEFT_TITLE_RIGHT: 'img_left_title_right.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN: 'img_up_title_down.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN_2COLUMNS: 'img_up_title_down.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN_3COLUMNS: 'img_up_title_down.pt',
        VIEW_TYPE_IMG_UP_TITLE_DOWN_4COLUMNS: 'img_up_title_down.pt',
    }
    SUMMARY_LENGTH_MAX = 200

    def render(self):
        view_type = getattr(self.data, 'view_type', VIEW_TYPE_LIST)
        return ViewPageTemplateFile('{folder}/{file}'.format(
            folder=Renderer.TEMPLATE_FOLDER,
            file=Renderer.TEMPLATE_FILE[view_type]))(self)

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
            if result_obj.portal_type == 'Event':

                result_image = getattr(result_obj, 'image', None)
                result_description = ''
                try:
                    result_description = result_obj.description
                except:
                    pass

                date = toLocalizedTime(self, result.end)

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
            results = [
                brain for brain in results
                if brain.portal_type == 'Event']
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
            results = [
                    brain for brain in results
                    if brain.portal_type == 'Event']
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


class AddForm(base.AddForm):

    schema = IMultiviewCollectionEventsPortlet
    label = _(u"Add Event Multi-view Collection Portlet")
    description = _(u"This portlet displays a listing of items from a "
                    u"Collection of events.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = IMultiviewCollectionEventsPortlet
    label = _(u"Edit Event Multi-view Collection Portlet")
    description = _(u"This portlet displays a listing of items from a "
                    u"Collection of events.")
