# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import isExpired
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.app.portlets.portlets.news import Renderer as news_renderer
from plone.memoize.view import memoize_contextless
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.interface import implementer

from genweb6.core.interfaces import INewsFolder
from genweb6.core.utils import pref_lang


class INewsPortlet(IPortletDataProvider):
    """A portlet which can render a list of news.
    """
    count = schema.Int(
        title=_(u"Numero de noticies a mostrar"),
        description=_(u"Maxim numero de noticies a mostrar (5 o 7)"),
        required=True,
        default=5,
        min=5,
        max=7
    )

    showdata = schema.Bool(
        title=_(u"Mostra data?"),
        description=_(
            u"Boolea que indica si s'ha de mostrar la data en les noticies"),
        required=False,
        default=True,
    )


@implementer(INewsPortlet)
class Assignment(base.Assignment):

    def __init__(self, count=5, showdata=True):
        self.count = count
        self.showdata = showdata

    @property
    def title(self):
        return _(u"News")


class Renderer(news_renderer):
    render = ViewPageTemplateFile('news.pt')

    def mostraData(self):
        return self.data.showdata

    def all_news_link(self):
        pc = api.portal.get_tool('portal_catalog')
        news_folder = pc.searchResults(
            object_provides=INewsFolder.__identifier__, Language=pref_lang())

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

    def get_current_path_news(self):
        lang = pref_lang()
        root_path = '/'.join(api.portal.get().getPhysicalPath())
        if lang == 'ca':
            return root_path + '/' + lang + '/noticies'
        elif lang == 'es':
            return root_path + '/' + lang + '/noticias'
        elif lang == 'en':
            return root_path + '/' + lang + '/news'

    @memoize_contextless
    def _data(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        limit = self.data.count
        state = ['published', 'intranet']
        allresults = catalog(portal_type=('News Item', 'Link'),
                             review_state=state,
                             is_important=True,
                             Language=pref_lang(),
                             sort_on="getObjPositionInParent",
                             path=self.get_current_path_news())

        results = []
        for brain in allresults:
            if not isExpired(brain):
                results.append(brain)
                if len(results) == limit:
                    break

        important = len(results)
        if important < limit:
            results2 = catalog(portal_type=('News Item', 'Link'),
                               review_state=state,
                               is_important=False,
                               Language=pref_lang(),
                               sort_on=('Date'),
                               sort_order='reverse',
                               path=self.get_current_path_news())
            results3 = []
            for brain in results2:
                if not isExpired(brain):
                    results3.append(brain)
                    if len(results3) == limit - important:
                        break
            return results + results3
        else:
            return results


class AddForm(base.AddForm):
    schema = INewsPortlet
    label = _(u"Add Noticies portlet")
    description = _(u"Aquest portlet mostra noticies")

    def create(self, data):
        return Assignment(count=data.get('count', 5), showdata=data.get('showdata', True))


class EditForm(base.EditForm):
    schema = INewsPortlet
    label = _(u"Edit News Portlet")
    description = _(u"This portlet displays recent News Items.")
