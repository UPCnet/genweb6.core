# # -*- coding: utf-8 -*-
# from datetime import timedelta
# from plone import api
# from plone.app.event.base import localized_now
# from plone.app.event.dx.behaviors import EventAccessor
# from plone.app.testing import login
# from plone.app.testing import setRoles
# from plone.app.testing import TEST_USER_ID
# from plone.app.testing import TEST_USER_NAME
# from plone.portlets.interfaces import IPortletManager
# from plone.portlets.interfaces import IPortletRenderer
# from zope.component import getMultiAdapter
# from zope.component import getUtility
# from zope.component.hooks import setHooks
# from zope.component.hooks import setSite

# from genweb5.core.testing import GENWEB_INTEGRATION_TESTING
# from genweb.theme.portlets import esdeveniments

# import unittest2 as unittest

# TZNAME = 'Europe/Vienna'


# class RendererTest(unittest.TestCase):
#     layer = GENWEB_INTEGRATION_TESTING

#     def setUp(self):
#         portal = self.layer['portal']
#         self.portal = portal
#         self.request = self.layer['request']
#         self.wft = api.portal.get_tool(name='portal_workflow')
#         setRoles(portal, TEST_USER_ID, ['Manager'])
#         setHooks()
#         setSite(portal)
#         folder_id = self.portal.invokeFactory('Folder', 'test-folder')
#         self.folder = self.portal[folder_id]

#         # Make sure Events use simple_publication_workflow
#         self.portal.portal_workflow.setChainForPortalTypes(
#             ['Event'], ['simple_publication_workflow']
#         )

#     def create_event(self, context, id='e1', title='New event', days=(1, 1), start=0, end=1, whole_day=False, open_end=False):
#         """ Creates an event with delta days tuple (start, end) beggining from
#             now. The start and end arguments are also treated as delta hours.
#         """
#         delta_start = timedelta(hours=start, days=days[0])
#         delta_end = timedelta(hours=end, days=days[1])

#         start = localized_now() + delta_start
#         end = localized_now() + delta_end

#         EventAccessor.event_type = 'Event'
#         acc = EventAccessor.create(
#             container=context,
#             content_id=id,
#             title=title,
#             start=start,
#             end=end,
#             timezone=TZNAME,
#             whole_day=whole_day,
#             open_end=open_end
#         )
#         acc.location = u'Graz, Austria'

#         return context[id]

#     def renderer(self, context=None, request=None, view=None, manager=None,
#                  assignment=None):
#         context = context or self.portal
#         request = request or self.request
#         view = view or context.restrictedTraverse('@@plone')
#         manager = manager or getUtility(
#             IPortletManager,
#             name='plone.rightcolumn',
#             context=self.portal
#         )
#         assignment = assignment or esdeveniments.Assignment()

#         return getMultiAdapter(
#             (context, request, view, manager, assignment), IPortletRenderer
#         )

#     def test_basic_event(self):
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
#         login(self.portal, TEST_USER_NAME)

#         event = self.create_event(self.folder)
#         api.content.transition(event, to_state='published')
#         portlet = self.renderer(context=self.folder, assignment=esdeveniments.Assignment())
#         portlet.update()
#         rd = portlet.render()

#         near_event = portlet.published_events()
#         self.assertTrue(len(near_event) == 1)
#         self.assertTrue('e1' in rd)

#     def test_whole_day_event_spanning_one_day(self):
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
#         login(self.portal, TEST_USER_NAME)

#         event = self.create_event(self.folder, whole_day=True)
#         api.content.transition(event, to_state='published')
#         portlet = self.renderer(context=self.folder, assignment=esdeveniments.Assignment())
#         portlet.update()
#         rd = portlet.render()

#         near_event = portlet.published_events()
#         self.assertTrue(len(near_event) == 1)
#         self.assertTrue('e1' in rd)

#     def test_whole_day_event_spanning_two_days(self):
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
#         login(self.portal, TEST_USER_NAME)

#         event = self.create_event(self.folder, days=(1, 2), whole_day=True)
#         api.content.transition(event, to_state='published')
#         portlet = self.renderer(context=self.folder, assignment=esdeveniments.Assignment())
#         portlet.update()
#         rd = portlet.render()

#         near_event = portlet.published_events()
#         self.assertTrue(len(near_event) == 1)
#         self.assertTrue('e1' in rd)
