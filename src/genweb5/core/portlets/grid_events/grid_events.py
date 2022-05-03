# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary

from genweb5.core import GenwebMessageFactory as _
from genweb5.core.interfaces import IEventFolder
from genweb5.core.utils import pref_lang


countVocabulary = SimpleVocabulary.fromValues(range(1, 17))
columnsVocabulary = SimpleVocabulary.fromValues(range(1, 5))
PLMF = MessageFactory('plonelocales')


class IGridEventsPortlet(IPortletDataProvider):
    """A portlet which can render a list of events.
    """
    count = schema.Choice(
        title=_(u"Numero de esdeveniments a mostrar"),
        description=_(u"Maxim numero de esdeveniments a mostrar (d'1 a 16)"),
        required=True,
        vocabulary=countVocabulary,
        default=4
    )

    columns = schema.Choice(
        title=_(u"Numero de columnes"),
        description=_(u"Numero de columnes (d'1 a 4)"),
        required=True,
        vocabulary=columnsVocabulary,
        default=4
    )


@implementer(IGridEventsPortlet)
class Assignment (base.Assignment):

    def __init__(self, count=4, columns=4):
        self.count = count
        self.columns = columns

    @property
    def title(self):
        return _(u"Grid events")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('grid_events.pt')

    def all_events_link(self):
        pc = api.portal.get_tool('portal_catalog')
        events_folder = pc.searchResults(object_provides=IEventFolder.__identifier__,
                                         Language=pref_lang())

        if events_folder:
            return '%s' % events_folder[0].getURL()
        else:
            return ''

    def get_current_path_events(self):
        lang = pref_lang()
        root_path = '/'.join(api.portal.get().getPhysicalPath())
        if lang == 'ca':
            return root_path + '/' + lang + '/esdeveniments'
        elif lang == 'es':
            return root_path + '/' + lang + '/eventos'
        elif lang == 'en':
            return root_path + '/' + lang + '/events'

    def get_span(self):
        columns = self.data.columns
        if columns == 1:
            return 'span12'
        elif columns == 2:
            return 'span6'
        elif columns == 3:
            return 'span4'
        else:
            return 'span3'

    def _data(self):
        return get_events(
            self.context,
            ret_mode=2,
            start=localized_now(),
            expand=True,
            sort='start',
            review_state=['published', 'intranet'])

    @memoize
    def get_events(self):
        events = []
        ts = getToolByName(self.context, 'translation_service')
        results = self._data()
        for event in results:
            if len(events) >= self.data.count:
                break

            if not event.isExpired():
                startDay = DateTime(event.start)
                endDay = DateTime(event.end)
                info = {'url': event.absolute_url(),
                        'firstday': int(startDay.strftime('%d')),
                        'firstmonth': PLMF(ts.month_msgid(int(startDay.strftime('%m')))),
                        'lastday': int(endDay.strftime('%d')),
                        'lastmonth': PLMF(ts.month_msgid(int(endDay.strftime('%m')))),
                        'title': event.Title
                        }
                events.append(info)
        return events

    def dateType(self, event):
        """Select which type of text appears in circle."""
        startday = event['firstday']
        endday = event['lastday']
        startmonth = event['firstmonth']
        endmonth = event['lastmonth']
        if startmonth != endmonth:
            return 'difday_difmonth'
        elif startday != endday:
            return 'difday_samemonth'
        else:
            return 'sameday_samemonth'


class AddForm(base.AddForm):
    schema = IGridEventsPortlet
    label = _(u"Add Grid Events portlet")
    description = _(u"This portlet displays recent Events.")

    def create(self, data):
        return Assignment(count=data.get('count', 4),
                          columns=data.get('columns', 4))


class EditForm(base.EditForm):
    schema = IGridEventsPortlet
    label = _(u"Edit Grid Events Portlet")
    description = _(u"This portlet displays recent Events.")
