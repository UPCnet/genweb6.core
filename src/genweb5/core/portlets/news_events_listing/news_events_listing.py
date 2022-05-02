# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from calendar import monthrange
from datetime import date
from datetime import timedelta
from plone import api
from plone.app.event.base import guess_date_from
from plone.app.event.base import localized_now
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

import re


PLMF = MessageFactory('plonelocales')


class INewsEventsListingPortlet(IPortletDataProvider):
    tags = schema.List(title=_(u"Tags"),
                       required=False,
                       value_type=schema.Choice(vocabulary=u'plone.app.vocabularies.Keywords'))

    typetag = schema.Choice(title=_(u"Type"),
                            required=True,
                            values=['News', 'Events'])


@implementer(INewsEventsListingPortlet)
class Assignment (base.Assignment):

    def __init__(self, tags, typetag):
        self.tags = tags
        self.typetag = typetag

    @property
    def title(self):
        return _(u"Categories")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('news_events_listing.pt')

    def update(self):
        try:
            self.now = now = self.context.start
        except:
            self.now = now = localized_now(self.context)

        # Request parameter
        req = self.request.form
        self.b_start = 'b_start' in req and int(req['b_start']) or 0
        self.b_size = 'b_size' in req and int(req['b_size']) or 10
        self.orphan = 'orphan' in req and int(req['orphan']) or 1
        self.mode = 'mode' in req and req['mode'] or None
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
        if self.mode is None:
            self.mode = self._date and 'day' or 'future'

    def get_tags(self):
        return self.data.tags

    def get_type(self):
        return self.data.typetag

    def _data(self):
        return self.data

    @property
    def date(self):
        dt = None
        if self._date:
            try:
                dt = guess_date_from(self._date)
            except TypeError:
                pass
        return dt

    # MODE URLs
    def _date_nav_url(self, mode, datestr=''):
        portal_url = api.portal.get().absolute_url()
        lang = self.context.language
        event_folder_name = dict(en='events', es='eventos', ca='esdeveniments')

        return '%s/%s/%s/event_listing?mode=%s%s' % (
            portal_url,
            lang,
            event_folder_name[lang],
            mode,
            datestr and '&date=%s' % datestr or ''
        )

    def _news_nav_url(self, tag=None):
        portal_url = api.portal.get().absolute_url()
        lang = self.context.language
        news_folder_name = dict(en='news', es='noticias', ca='noticies')

        if tag:
            return '%s/%s/%s/news_listing?tags=%s' % (
                portal_url,
                lang,
                news_folder_name[lang],
                tag)
        else:
            return '%s/%s/%s/news_listing' % (
                portal_url,
                lang,
                news_folder_name[lang])

    @property
    def mode_all_url(self):
        return self._date_nav_url('all')

    @property
    def mode_future_url(self):
        return self._date_nav_url('future')

    @property
    def mode_past_url(self):
        return self._date_nav_url('past')

    @property
    def mode_day_url(self):
        now = self.date or self.now
        return self._date_nav_url('day', now.date().isoformat())

    @property
    def mode_week_url(self):
        now = self.date or self.now
        return self._date_nav_url('week', now.date().isoformat())

    @property
    def mode_month_url(self):
        now = self.date or self.now
        return self._date_nav_url('month', now.date().isoformat())

    # DAY NAV
    @property
    def next_day_url(self):
        now = self.date or self.now
        datestr = (now + timedelta(days=1)).date().isoformat()
        return self._date_nav_url('day', datestr)

    @property
    def today_url(self):
        return self._date_nav_url('day')

    @property
    def prev_day_url(self):
        now = self.date or self.now
        datestr = (now - timedelta(days=1)).date().isoformat()
        return self._date_nav_url('day', datestr)

    # WEEK NAV
    @property
    def next_week_url(self):
        now = self.date or self.now
        datestr = (now + timedelta(days=7)).date().isoformat()
        return self._date_nav_url('week', datestr)

    @property
    def this_week_url(self):
        return self._date_nav_url('week')

    @property
    def prev_week_url(self):
        now = self.date or self.now
        datestr = (now - timedelta(days=7)).date().isoformat()
        return self._date_nav_url('week', datestr)

    # MONTH NAV
    @property
    def next_month_url(self):
        now = self.date or self.now
        last_day = monthrange(now.year, now.month)[1]  # (wkday, days)
        datestr = (now.replace(day=last_day)
                   + timedelta(days=1)).date().isoformat()
        return self._date_nav_url('month', datestr)

    @property
    def this_month_url(self):
        return self._date_nav_url('month')

    @property
    def prev_month_url(self):
        now = self.date or self.now
        datestr = (now.replace(day=1) - timedelta(days=1)).date().isoformat()
        return self._date_nav_url('month', datestr)

    @property
    def ical_url(self):
        date = self.date
        mode = self.mode
        qstr = (date or mode) and '?%s%s%s' % (
            mode and 'mode=%s' % mode,
            mode and date and '&' or '',
            date and 'date=%s' % date or '') or ''

        try:
            obj = self.context.unrestrictedTraverse(
                self.context.virtual_url_path())

            if obj.Type() in ('Event', 'Collection'):
                return '%s/ics_view' % (self.context.absolute_url())
            else:
                return '%s/@@event_listing_ical%s' % (self.context.absolute_url(), qstr)
        except:
            # esdeveniment recursiu
            return '%s/ics_view' % (self.context.absolute_url())


class AddForm(base.AddForm):
    schema = INewsEventsListingPortlet
    label = _(u"Add Tags portlet")
    description = _(u"This portlet lists tags by type and context.")

    def create(self, data):
        return Assignment(tags=data.get('tags'), typetag=data.get('typetag'))


class EditForm(base.EditForm):
    schema = INewsEventsListingPortlet
    label = _(u"Edit Tags Portlet")
    description = _(u"This portlet lists tags by type and context.")
