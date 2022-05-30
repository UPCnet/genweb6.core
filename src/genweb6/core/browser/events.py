# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import DT
from plone.app.event.base import localized_now, get_events
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import ulocalized_time
from plone.event.interfaces import IEventAccessor
from plone.memoize.instance import memoize
from zope.i18nmessageid import MessageFactory

from genweb6.core import _
from genweb6.core.utils import abrevia
from genweb6.core.utils import abreviaPlainText


PLMF = MessageFactory('plonelocales')


class GridEventsView(FolderView):
    """ Grid view for events. """

    @property
    def no_items_message(self):
        """Translate custom message for no events in this folder."""
        return _(
            'description_no_events_in_folder',
            default=u'There are currently no events in this folder.'
        )

    def _query_events(self):
        """Get all events from this folder."""

        events = self.results(
            batch=True,
            object_provides=IEvent.__identifier__,
            sort_order='descending',
            sort_on='start',
        )
        return events

    def _query_future_events(self):
        """Get all future events from this folder."""
        now = localized_now()
        path = '/'.join(self.context.getPhysicalPath())

        future_events = get_events(context=self.context,
                                   path=path,
                                   start=now,
                                   ret_mode=RET_MODE_OBJECTS, expand=True,
                                   sort_on='start')
        return future_events

    @memoize
    def get_events(self):
        """Customize which properties we want to show in pt."""
        events = []
        ts = api.portal.get_tool(name='translation_service')
        results = self._query_events()

        for event in results:
            description = abrevia(event.description, 100) if event.description else None
            start = event.start
            end = event.end
            location = event.location if event.location else None
            info = {'url': event.getURL(),
                    'firstday': start.day,
                    'firstmonth': PLMF(ts.month_msgid(start.month)),
                    'abbrfirstmonth': PLMF(ts.month_msgid(start.month)),
                    'firstyear': start.year,
                    'lastday': end.day,
                    'lastmonth': PLMF(ts.month_msgid(end.month)),
                    'abbrlastmonth': PLMF(ts.month_msgid(end.month)),
                    'lastyear': end.year,
                    'title': abreviaPlainText(event.title, 60),
                    'descr': description,
                    'location': location,
                    'timezone': event.timezone,
                    'showflip': location or description
                    }

            info.update({'dateType': self.dateType(info)})
            events.append(info)

        return events

    @memoize
    def get_future_events(self):
        """Customize which properties we want to show in pt."""

        events = []
        ts = api.portal.get_tool(name='translation_service')
        results = self._query_future_events()

        for event in results:
            start = event.start
            end = event.end
            if event.portal_type == 'Occurrence':
                ocurrence = event
                event = IEventAccessor(ocurrence)
                event_url = event.url
            else:
                event_url = event.absolute_url()

            current_user = api.user.get_current()
            try:
                format_time = current_user.getProperty('format_time')
            except:
                format_time = ''

            DT_start = DT(start)

            if event.whole_day:
                start_time = ''
            else:
                start_time = ulocalized_time(
                    DT_start, long_format=False, time_only=True, context=event
                )

                if format_time is not None and format_time != '':
                    if start_time is not None:
                        if 'PM' in start_time or 'AM' in start_time or 'pm' in start_time or 'am' in start_time:
                            DT_start_time = datetime.strptime(str(start_time), '%I:%M %p')
                        else:
                            DT_start_time = datetime.strptime(str(start_time), '%H:%M')

                        if 'hh:i A' in format_time:
                            start_time = DT_start_time.strftime('%I:%M %p')
                        else:
                            start_time = DT_start_time.strftime('%H:%M')

            description = abrevia(event.description, 100) if event.description else None
            location = event.location if event.location else None
            info = {'url': event_url,
                    'firstday': start.day,
                    'firstmonth': PLMF(ts.month_msgid(start.month)),
                    'abbrfirstmonth': PLMF(ts.month_msgid(start.month)),
                    'firstyear': start.year,
                    'lastday': end.day,
                    'lastmonth': PLMF(ts.month_msgid(end.month)),
                    'abbrlastmonth': PLMF(ts.month_msgid(end.month)),
                    'lastyear': end.year,
                    'title': abreviaPlainText(event.title, 60),
                    'descr': description,
                    'location': location,
                    'timezone': event.timezone,
                    'showflip': location or description,
                    'starttime': start_time,
                    }

            info.update({'dateType': self.dateType(info)})
            events.append(info)

        return events

    def dateType(self, event):
        """Select which type of text appears in circle."""
        startday = event['firstday']
        endday = event['lastday']
        startmonth = event['firstmonth']
        endmonth = event['lastmonth']
        startyear = event['firstyear']
        endyear = event['lastyear']
        if startyear != endyear:
            return 'difday_difyear'
        elif startmonth != endmonth:
            return 'difday_difmonth'
        elif startday != endday:
            return 'difday_samemonth'
        else:
            return 'sameday_samemonth'
