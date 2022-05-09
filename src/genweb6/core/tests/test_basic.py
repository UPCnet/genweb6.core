# -*- coding: utf-8 -*-
from AccessControl import Unauthorized

from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.testing.z2 import Browser
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides

from genweb6.core.interfaces import IHomePage
from genweb6.core.portlets.homepage import homepage
from genweb6.core.testing import GENWEB_FUNCTIONAL_TESTING
from genweb6.core.testing import GENWEB_INTEGRATION_TESTING

import unittest2 as unittest
import transaction


class IntegrationTest(unittest.TestCase):

    layer = GENWEB_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def testPortalConstrains(self):
        portal_allowed_types = ['Folder', 'File', 'Image', 'Document']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(sorted(
            [ct.id for ct in self.portal.allowedContentTypes()]), sorted(portal_allowed_types))

    def testLinkBehavior(self):
        """Test for Link behavior and related index and metadata"""
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'f2', title=u"Soc una carpeta")
        f2 = portal['f2']
        f2.invokeFactory('Link', 'enllac', title=u"Soc un link")
        link = f2['enllac']
        link.open_link_in_new_window = False
        link.reindexObject()

        self.assertEqual(link.open_link_in_new_window, False)

        results = portal.portal_catalog.searchResults(portal_type='Link')
        self.assertEqual(results[0].open_link_in_new_window, False)

        link.open_link_in_new_window = True
        link.reindexObject()

        results = portal.portal_catalog.searchResults(portal_type='Link')
        self.assertEqual(results[0].open_link_in_new_window, True)

    def testHomePageMarkerInterface(self):
        self.assertTrue(IHomePage.providedBy(self.portal['front-page']))

    def testAdapters(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(
            'Document', 'test_adapter', title=u"Soc una pagina")
        from genweb6.core.adapters import IImportant
        obj = IImportant(self.portal.test_adapter)
        self.assertEqual(obj.is_important, False)
        obj.is_important = True
        obj2 = IImportant(self.portal.test_adapter)
        self.assertEqual(obj2.is_important, True)

    def test_favorites(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'prova', title=u"Soc una carpeta")
        prova = self.portal['prova']
        prova.invokeFactory('Folder', 'prova', title=u"Soc una carpeta")
        prova2 = prova['prova']

        from genweb6.core.adapters.favorites import IFavorite
        IFavorite(prova2).add(TEST_USER_NAME)
        self.assertTrue(TEST_USER_NAME in IFavorite(prova2).get())
        self.assertTrue(TEST_USER_NAME not in IFavorite(prova).get())

    def test_protected_content(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(
            'Folder', 'test_folder', title=u"Soc una carpeta")
        self.portal.test_folder.invokeFactory(
            'Document', 'test_document', title=u"Soc un document")
        from genweb6.core.interfaces import IProtectedContent
        alsoProvides(self.portal.test_folder, IProtectedContent)
        setRoles(self.portal, TEST_USER_ID, ['Reader', 'Editor'])

        self.portal.test_folder.manage_delObjects('test_document')

        self.assertRaises(
            Unauthorized, self.portal.manage_delObjects, 'test_folder')


class FunctionalTest(unittest.TestCase):

    layer = GENWEB_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.app = self.layer['app']
        self.browser = Browser(self.app)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Create a portlet in a slot
        benvingut = self.portal['front-page']
        manager = queryUtility(IPortletManager, name='genweb.portlets.HomePortletManager2', context=benvingut)
        assignments = getMultiAdapter((benvingut, manager), IPortletAssignmentMapping)
        homepage_assignment = homepage.Assignment()
        assignments['homepage'] = homepage_assignment
        transaction.commit()
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def testHomePagePortlet(self):
        portalURL = self.portal.absolute_url()

        self.browser.open(portalURL)

        self.assertTrue('Congratulations! You have successfully installed Plone.' in self.browser.contents)
