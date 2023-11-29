# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView

from datetime import date
from plone import api
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.event import _
from plone.app.event.base import guess_date_from
from plone.app.event.base import localized_now
from plone.app.querystring import queryparser
from plone.memoize import view

from genweb6.core.utils import pref_lang


class NewsListing(BrowserView):

    def __init__(self, context, request):
        super(NewsListing, self).__init__(context, request)

        self.now = now = localized_now(context)

        # Request parameter
        req = self.request.form
        self.b_start = 'b_start' in req and int(req['b_start']) or 0
        self.b_size = 'b_size' in req and int(req['b_size']) or 10
        self.orphan = 'orphan' in req and int(req['orphan']) or 1
        self._date = 'date' in req and req['date'] or None
        self.tags = 'tags' in req and req['tags'] or None
        self.searchable_text = 'SearchableText' in req and\
            req['SearchableText'] or None
        self.path = 'path' in req and req['path'] or None

        day = 'day' in req and int(req['day']) or None
        month = 'month' in req and int(req['month']) or None
        year = 'year' in req and int(req['year']) or None

        if not self._date and day or month or year:
            self._date = date(year or now.year,
                              month or now.month,
                              day or now.day).isoformat()

    @property
    def default_context(self):
        # Try to get the default page
        context = self.context
        default = context.getDefaultPage()
        if default:
            context = context[default]
        return context

    @property
    def is_collection(self):
        ctx = self.default_context
        return ICollection and ICollection.providedBy(ctx) or False

    @property
    def date(self):
        dt = None
        if self._date:
            try:
                dt = guess_date_from(self._date)
            except TypeError:
                pass
        return dt


    def get_current_path_news(self):
        lang = pref_lang()
        root_path = '/'.join(api.portal.get().getPhysicalPath())
        if lang == 'ca':
            return root_path + '/' + lang + '/noticies'
        elif lang == 'es':
            return root_path + '/' + lang + '/noticias'
        elif lang == 'en':
            return root_path + '/' + lang + '/news'

    @view.memoize
    def _get_news(self):
        context = self.context
        kw = {}

        if self.path:
            kw['path'] = self.path
        else:
            portal = api.portal.get()
            lang = self.context.language
            news_folder_name = dict(en='news', es='noticias', ca='noticies')
            try:
                news_folder = portal[lang][news_folder_name[lang]]
            except:
                news_folder = context
            kw['path'] = '/'.join(news_folder.getPhysicalPath())

        if self.tags:
            kw['Subject'] = {'query': self.tags, 'operator': 'and'}

        if self.searchable_text:
            kw['SearchableText'] = self.searchable_text

        is_col = self.is_collection
        if is_col:
            ctx = self.default_context
            query = queryparser.parseFormquery(ctx, ctx.getRawQuery())
            kw.update(query)
            kw['sort_on'] = ctx.sort_on
            if ctx.sort_reversed:
                kw['sort_order'] = 'reverse'
        else:
            kw['object_provides'] = (INewsItem.__identifier__)
            kw['sort_on'] = 'Date'
            kw['sort_order'] = 'reverse'

        cat = getToolByName(context, 'portal_catalog')
        result = cat(is_important=True, **kw)
        result2 = cat(is_important=False, **kw)

        return result + result2

    def news(self, batch=True):
        res = self._get_news()

        if batch:
            b_start = self.b_start
            b_size = self.b_size
            res = Batch(res, size=b_size, start=b_start, orphan=self.orphan)

        return res