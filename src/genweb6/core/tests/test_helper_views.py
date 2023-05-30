import unittest
from genweb6.core.testing import GENWEB_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone import api
from zope.component import getMultiAdapter, getAdapter

class ViewsIntegrationTest(unittest.TestCase):
    layer = GENWEB_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
    
    def test_ping(self):
        print(self.portal.keys())
        view = api.content.get_view(
                name='ping',
                context=self.portal,
                request=self.request
            )
        self.assertEqual('1', view())