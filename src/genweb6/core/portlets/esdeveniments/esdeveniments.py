# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from Products.CMFPlone.utils import isExpired
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import date
from datetime import timedelta
from plone import api
from plone.app.event.base import localized_now, get_events
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

from genweb6.core import GenwebMessageFactory as TAM
from genweb6.core.interfaces import IEventFolder
from genweb6.core.utils import pref_lang


PLMF = MessageFactory('plonelocales')


class IEsdevenimentsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5,
                       min=5,
                       max=7
                       )

    state = schema.Tuple(title=_(u"Workflow state"),
                         description=_(
                             u"Items in which workflow state to show."),
                         default=('published', ),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.WorkflowStates")
                         )


@implementer(IEsdevenimentsPortlet)
class Assignment(base.Assignment):

    def __init__(self, count=5, state=('published', )):
        self.count = count
        self.state = state

    @property
    def title(self):
        return TAM(u"Events")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('esdeveniments.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        # self.navigation_root_url = portal_state.navigation_root_url()
        self.portal = api.portal.get()
        self.navigation_root_path = portal_state.navigation_root_path()
        # self.navigation_root_object = getNavigationRootObject(self.context, self.portal)

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())

    def published_events(self):
        return self._data()

    def published_events_expanded(self):
        """
        Return expanded ongoing events, i.e. taking into account their
        occurrences in case they are recurrent events.
        """
        results = []
        for event in get_events(self.context,
                                ret_mode=2,
                                start=localized_now(),
                                expand=True,
                                sort='start',
                                review_state=self.data.state):

            if len(results) >= self.data.count:
                break

            if not isExpired(event):
                results.append(self.event_to_view_obj(event))

        return results

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
            url=event.absolute_url())

    def get_month_name(self, month, month_format=''):
        self._ts = api.portal.get_tool(name='translation_service')
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

    # Deprecated?
    def prev_events_link(self):
        previous_events = self.portal.esdeveniments.aggregator.anteriors.getTranslation()
        if self.have_events_folder:
            return '%s' % previous_events.absolute_url()
        else:
            return None

    @memoize
    def _data(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        limit = self.data.count
        state = self.data.state

        now = localized_now()
        tomorrow = date.today() + timedelta(1)
        yesterday = date.today() - timedelta(1)

        results = catalog(portal_type='Event',
                          review_state=state,
                          end={'query': now,
                               'range': 'min'},
                          start={'query': [yesterday, tomorrow],
                                 'range': 'min:max'},
                          Language=pref_lang(),
                          sort_on='start')

        results_not_expired = []
        for res in results:
            if len(results_not_expired) >= limit:
                break

            if not isExpired(res):
                results_not_expired.append(res)

        count = len(results_not_expired)
        if count < limit:
            results2 = catalog(portal_type=('Event'),
                               review_state=state,
                               end={'query': now,
                                    'range': 'min'},
                               start={'query': yesterday,
                                      'range': 'max'},
                               Language=pref_lang(),
                               sort_on='start')

            results2_not_expired = []
            for res in results2:
                if len(results2_not_expired) >= (limit - count):
                    break

                if not isExpired(res):
                    results2_not_expired.append(res)

            count = len(results_not_expired + results2_not_expired)
            if count < limit:
                results3 = catalog(portal_type=('Event'),
                                   review_state=state,
                                   end={'query': now,
                                        'range': 'min'
                                        },
                                   start={'query': tomorrow,
                                          'range': 'min'},
                                   Language=pref_lang(),
                                   sort_on='start')

                results3_not_expired = []
                for res in results3:
                    if len(results3_not_expired) >= (limit - count):
                        break

                    if not isExpired(res):
                        results3_not_expired.append(res)

                return results_not_expired + results2_not_expired + results3_not_expired
            else:
                return results_not_expired + results2_not_expired
        else:
            return results_not_expired


class AddForm(base.AddForm):
    schema = IEsdevenimentsPortlet
    label = _(u"Add Events Portlet")
    description = _(u"This portlet lists upcoming Events.")

    def create(self, data):
        return Assignment(count=data.get('count', 5), state=data.get('state', ('published', )))


class EditForm(base.EditForm):
    schema = IEsdevenimentsPortlet
    label = _(u"Edit Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
