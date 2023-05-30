# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from genweb6.core.testing import GENWEB6_CORE_INTEGRATION_TESTING  # noqa: E501

import unittest

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that genweb6.core is properly installed."""

    layer = GENWEB6_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if genweb6.core is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'genweb6.core'))

    def test_browserlayer(self):
        """Test that IGenweb6CoreLayer is registered."""
        from genweb6.core.interfaces import (
            IGenweb6CoreLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IGenweb6CoreLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = GENWEB6_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['genweb6.core'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if genweb6.core is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'genweb6.core'))

    def test_browserlayer_removed(self):
        """Test that IGenweb6CoreLayer is removed."""
        from genweb6.core.interfaces import \
            IGenweb6CoreLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IGenweb6CoreLayer,
            utils.registered_layers())
