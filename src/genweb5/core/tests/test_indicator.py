# -*- coding: utf-8 -*-
from mock import Mock
from mock import patch

from genweb5.core.indicators import Indicator

import unittest


class TestIndicator(unittest.TestCase):
    def setUp(self):
        pass

    def test_instance_from_dict_invalid_type(self):
        with self.assertRaises(TypeError):
            Indicator.instance_from_dict(None, context=None)

    def test_instance_from_dict_no_service(self):
        indicator_dict = dict(
            id='indicator-id',
            description='Indicator description',
            categories=[],
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "No 'service' found in the dictionary", context.exception.message)

    def test_instance_from_dict_no_id(self):
        indicator_dict = dict(
            service='service',
            description='Indicator description',
            categories=[],
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "No 'id' found in the dictionary", context.exception.message)

    def test_instance_from_dict_no_description(self):
        indicator_dict = dict(
            service='service',
            id='indicator-id',
            categories=[],
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "No 'description' found in the dictionary",
            context.exception.message)

    def test_instance_from_dict_no_categories(self):
        indicator_dict = dict(
            service='service',
            id='indicator-id',
            description='Indicator description',
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "No 'categories' found in the dictionary",
            context.exception.message)

    def test_instance_from_dict_invalid_type_service(self):
        indicator_dict = dict(
            service=None,
            id='indicator-id',
            description='Indicator description',
            categories=[]
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "'service' must be a string",
            context.exception.message)

    def test_instance_from_dict_should_not_raise_error_for_unicode_service(self):
        indicator_dict = dict(
            service=u'service',
            id='indicator-id',
            description='Indicator description',
            categories=[]
        )
        Indicator.instance_from_dict(indicator_dict, context=None)

    def test_instance_from_dict_invalid_type_id(self):
        indicator_dict = dict(
            service='service',
            id=1,
            description='Indicator description',
            categories=[]
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "'id' must be a string",
            context.exception.message)

    def test_instance_from_dict_should_not_raise_error_for_unicode_id(self):
        indicator_dict = dict(
            service='service',
            id=u'indicator-id',
            description='Indicator description',
            categories=[]
        )
        Indicator.instance_from_dict(indicator_dict, context=None)

    def test_instance_from_dict_invalid_type_description(self):
        indicator_dict = dict(
            service='service',
            id='indicator-id',
            description=None,
            categories=[]
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "'description' must be a string",
            context.exception.message)

    def test_instance_from_dict_should_not_raise_error_for_unicode_description(
            self):
        indicator_dict = dict(
            service='service',
            id='indicator-id',
            description=u'descripcio',
            categories=[]
        )
        Indicator.instance_from_dict(indicator_dict, context=None)

    def test_instance_from_dict_invalid_type_categories(self):
        indicator_dict = dict(
            service='service',
            id='indicator-id',
            description='Indicator description',
            categories='categories'
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "'categories' must be a list",
            context.exception.message)

    def test_instance_from_dict_empty_service(self):
        indicator_dict = dict(
            service='',
            id='indicator-id',
            description='Indicator description',
            categories=[]
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "'service' cannot be empty",
            context.exception.message)

    def test_instance_from_dict_empty_id(self):
        indicator_dict = dict(
            service='service',
            id='',
            description='Indicator description',
            categories=[]
        )
        with self.assertRaises(ValueError) as context:
            Indicator.instance_from_dict(indicator_dict, context=None)
        self.assertEqual(
            "'id' cannot be empty",
            context.exception.message)

    def test_instance_from_dict_valid(self):
        indicator_dict = dict(
            service='service',
            id='indicator-id',
            description='indicator-description',
            categories=[dict(id='category-id-1'), dict(id='category-id-2')]
        )

        def mock_instance_from_dict(category_dict, context):
            return Mock(id=category_dict['id'], context=context)
        with patch(
                'genweb5.core.indicators.model.Category.instance_from_dict',
                side_effect=mock_instance_from_dict):
            indicator = Indicator.instance_from_dict(indicator_dict, "context")

        self.assertEqual('service', indicator.service)
        self.assertEqual('indicator-id', indicator.id)
        self.assertEqual('indicator-description', indicator.description)
        self.assertEqual(2, len(indicator.categories))
        self.assertEqual(
            "context", indicator.categories['category-id-1'].context)
        self.assertEqual(
            indicator, indicator.categories['category-id-1'].indicator)
        self.assertEqual(
            "context", indicator.categories['category-id-2'].context)
        self.assertEqual(
            indicator, indicator.categories['category-id-2'].indicator)
