# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import isExpired
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import GenwebMessageFactory as _
from genweb6.core.interfaces import INewsFolder
from genweb6.core.utils import pref_lang
from genweb6.core.utils import toLocalizedTime

import secrets


viewVocabulary = SimpleVocabulary([
    SimpleTerm(value="id_normal", title=_(u'Normal view')),
    SimpleTerm(value="id_full", title=_(u'Full view')),
    SimpleTerm(value="id_full_2cols", title=_(u'Full2cols view')),
    SimpleTerm(value="id_full_3cols", title=_(u'Full3cols view')),
    SimpleTerm(value="id_full_4cols", title=_(u'Full4cols view')),
    SimpleTerm(value="id_simple_carousel", title=_(u'Simple carousel view')),
    SimpleTerm(value="id_multiple_carousel", title=_(u'Multiple carousel view'))])

countVocabulary = SimpleVocabulary.fromValues(range(1, 15))


class IFullNewsPortlet(IPortletDataProvider):
    """A portlet which can render a list of news.
    """
    view_type = schema.Choice(
        title=_(u'Tipus de vista'),
        description=_(u'Escull com es mostraran les noticies'),
        required=True,
        vocabulary=viewVocabulary,
        default='id_normal'
    )

    count = schema.Choice(
        title=_(u"Numero de noticies a mostrar"),
        description=_(u"Maxim numero de noticies a mostrar (d'1 a 14)"),
        required=True,
        vocabulary=countVocabulary,
        default=5
    )

    showdata = schema.Bool(
        title=_(u"Mostra data?"),
        description=_(
            u"Boolea que indica si s'ha de mostrar la data en les noticies"),
        required=False,
        default=True
    )


@implementer(IFullNewsPortlet)
class Assignment (base.Assignment):

    def __init__(self, count=5, showdata=True, view_type='id_normal'):
        self.count = count
        self.showdata = showdata
        self.view_type = view_type

    @property
    def title(self):
        return _(u"Full News")


class Renderer(base.Renderer):

    TEMPLATE_FOLDER = 'templates'
    TEMPLATE_FILE = {
        'id_normal': 'list.pt',
        'id_full': 'img_up_title_down.pt',
        'id_full_2cols': 'img_up_title_down.pt',
        'id_full_3cols': 'img_up_title_down.pt',
        'id_full_4cols': 'img_up_title_down.pt',
        'id_simple_carousel': 'carousel.pt',
        'id_multiple_carousel': 'carousel_complex.pt',
    }
    SUMMARY_LENGTH_MAX = 200

    def render(self):
        view_type = getattr(self.data, 'view_type', 'id_normal')
        return ViewPageTemplateFile('{folder}/{file}'.format(
            folder=Renderer.TEMPLATE_FOLDER,
            file=Renderer.TEMPLATE_FILE[view_type]))(self)

    @property
    def token(self):
        return secrets.token_hex(16)

    def show_time(self):
        return self.data.showdata

    def published_news_items(self):
        return self._data()

    def published_news_items_odd(self):
        return self._data()[1::2]

    def published_news_items_pair(self):
        return self._data()[0::2]

    def published_news_items_group_by_x(self, num):
        result = []
        for count in range(num):
            result.append([])

        pos = 0
        for new in self._data():
            result[pos].append(new)
            pos = 0 if pos == (num - 1) else pos + 1
        return result

    def published_news_items_group_by_three(self):
        return self.published_news_items_group_by_x(3)

    def published_news_items_group_by_four(self):
        return self.published_news_items_group_by_x(4)

    def mostraData(self):
        return self.data.showdata

    def tipus(self):
        # backwards compatibility: if view_type not set, assign old view equivalent
        if not hasattr(self.data, 'view_type'):
            self.data.view_type = "id_normal"
        return self.data.view_type

    def all_news_link(self):
        pc = api.portal.get_tool('portal_catalog')
        news_folder = pc.searchResults(object_provides=INewsFolder.__identifier__,
                                       Language=pref_lang())

        if news_folder:
            return '%s' % news_folder[0].getURL()
        else:
            return ''

    def rss_news_link(self):
        pc = api.portal.get_tool('portal_catalog')
        news_folder = pc.searchResults(object_provides=INewsFolder.__identifier__,
                                       Language=pref_lang())

        if news_folder:
            return '%s%s' % (news_folder[0].getURL(), '/aggregator/RSS')
        else:
            return ''

    def abrevia(self, obj):
        desc_new = obj.Description

        if len(desc_new) > 200:
            desc_text = desc_new[:200]
            desc_text = desc_text[:desc_text.rfind(' ') - len(desc_text)]
            desc_text = desc_text + '...'
        else:
            desc_text = desc_new
        return desc_text

    def get_current_path_news(self):
        lang = pref_lang()
        root_path = '/'.join(api.portal.get().getPhysicalPath())
        if lang == 'ca':
            return root_path + '/' + lang + '/noticies'
        elif lang == 'es':
            return root_path + '/' + lang + '/noticias'
        elif lang == 'en':
            return root_path + '/' + lang + '/news'

    def _summarize(self, text):
        summary = text
        if len(summary) > Renderer.SUMMARY_LENGTH_MAX:
            summary = text[:Renderer.SUMMARY_LENGTH_MAX]
            last_space = summary.rfind(' ')
            last_space = -3 if last_space == -1 else last_space
            summary = summary[:last_space] + '...'
        return summary

    @memoize
    def _data(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        limit = self.data.count
        state = ['published', 'intranet']
        results = catalog(portal_type=('News Item', 'Link'),
                          review_state=state,
                          is_important=True,
                          Language=pref_lang(),
                          sort_on="getObjPositionInParent",
                          path=self.get_current_path_news())

        importants = []
        for brain in results:
            if not isExpired(brain):
                importants.append(brain)
                if len(importants) == limit:
                    break

        important = len(importants)
        if important < limit:
            normals = catalog(portal_type=('News Item', 'Link'),
                              review_state=state,
                              is_important=False,
                              Language=pref_lang(),
                              sort_on=('Date'),
                              sort_order='reverse',
                              path=self.get_current_path_news())
            normals_limit = []
            path_folder_news = self.all_news_link()
            for brain in normals:
                if not isExpired(brain):
                    brain_url = brain.getURL()
                    brain_type = brain.Type
                    if brain_type == 'Link' and brain_url.startswith(path_folder_news) or brain_type == 'News Item':
                        normals_limit.append(brain)
                    if len(normals_limit) == limit - important:
                        break
            return importants + normals_limit
        else:
            return importants[:limit]

    def result_dicts(self):
        """
        Transform results into dictionaries of results containing only the data
        to render from templates.
        """
        view_type = getattr(self.data, 'view_type', 'id_normal')
        col = 12
        if view_type == 'id_full_2cols':
            col = 6
        elif view_type == 'id_full_3cols':
            col = 4
        elif view_type == 'id_full_4cols':
            col = 3

        result_dicts = []
        for index, result in enumerate(self._data(), start=0):
            result_obj = result.getObject()
            result_image = getattr(result_obj, 'image', None)
            try:
                result_description = result.description
            except:
                try:
                    result_description = result.Description()
                except:
                    result_description = ''

            date = toLocalizedTime(self, result_obj.effective_date)
            if not date:
                date = toLocalizedTime(self, result_obj.modification_date)

            result_dicts.append(dict(
                date=date,
                description=self._summarize(result_description),
                col=col,
                image=result_image,
                image_caption=getattr(result_obj, 'image_caption', None),
                image_src=("{0}/@@images/image/preview".format(result.getURL()) if result_image else None),
                portal_type=normalizeString(result.portal_type),
                title=result_obj.title_or_id(),
                url=result.getURL(),
                active=index == 0,
                index=index,
            ))

        return result_dicts


class AddForm(base.AddForm):
    schema = IFullNewsPortlet
    label = _(u"Add Noticies portlet")
    description = _(u"Aquest portlet mostra noticies")

    def create(self, data):
        return Assignment(count=data.get('count', 5), showdata=data.get('showdata', True), view_type=data.get('view_type', 'id_normal'))


class EditForm(base.EditForm):
    schema = IFullNewsPortlet
    label = _(u"Edit News Portlet")
    description = _(u"This portlet displays recent News Items.")
