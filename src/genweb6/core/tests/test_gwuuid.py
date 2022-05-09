# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.uuid.interfaces import IUUID

from genweb6.core.gwuuid import ATTRIBUTE_NAME
from genweb6.core.gwuuid import IGWUUID
from genweb6.core.testing import GENWEB_INTEGRATION_TESTING

import unittest2 as unittest


class IntegrationTest(unittest.TestCase):

    layer = GENWEB_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_basic_gwuuid(self):
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'f1', title=u"Soc una carpeta")
        folder = self.portal['f1']

        self.assertTrue(IGWUUID(folder).get())

    def test_different_from_uuid(self):
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'f1', title=u"Soc una carpeta")
        folder = self.portal['f1']

        self.assertNotEqual(IGWUUID(folder).get(), IUUID(folder))

    def test_mutable(self):
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'f1', title=u"Soc una carpeta")
        folder = self.portal['f1']
        original_uuid = IGWUUID(folder).get()

        mutated = IGWUUID(folder).set('not equal')

        self.assertNotEqual(original_uuid, mutated)

    def test_access_by_attr(self):
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'f1', title=u"Soc una carpeta")
        folder = self.portal['f1']

        self.assertTrue(getattr(folder, ATTRIBUTE_NAME, False))
