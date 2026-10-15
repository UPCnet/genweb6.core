# -*- coding: utf-8 -*-
"""Los serializadores propios deben aceptar los argumentos de plone.restapi 9."""
from genweb6.core.interfaces import IGenweb6CoreLayer
from genweb6.core.testing import GENWEB_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import unittest


class TestSerializers(unittest.TestCase):

    layer = GENWEB_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IGenweb6CoreLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _serialize(self, obj, **kwargs):
        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer(**kwargs)

    def test_site_root_accepts_restapi_9_arguments(self):
        # plone.restapi.serializer.catalog llama con include_items=False
        result = self._serialize(self.portal, include_items=False)
        self.assertNotIn('creators', result)
        self.assertNotIn('items', result)

    def test_site_root_include_items_is_respected(self):
        with_items = self._serialize(self.portal)
        self.assertIn('items', with_items)

    def test_folder_and_content_serializers_accept_restapi_9_arguments(self):
        # La capa de test no tiene tipos de contenido instalados: se comprueba
        # que los argumentos se reenvian al serializador original.
        from genweb6.core import serializer
        from unittest import mock
        for cls in (serializer.CustomSerializeFolderToJson,
                    serializer.CustomSerializeToJson):
            base = cls.__mro__[1]
            with mock.patch.object(
                    base, '__call__', return_value={'creators': 1, 'x': 2}) as call:
                result = cls(self.portal, self.request)(
                    include_items=False, include_expansion=False)
            call.assert_called_once_with(
                include_items=False, include_expansion=False)
            self.assertEqual(result, {'x': 2})
