# -*- coding: utf-8 -*-
from mock import Mock
from mock import patch

from genweb6.core.indicators import Category
from genweb6.core.indicators import Calculator

import unittest


class MockCalculator(Calculator):
    pass


class TestCategory(unittest.TestCase):
    def setUp(self):
        pass

    def test_instance_from_dict_invalid_type(self):
        with self.assertRaises(TypeError):
            Category.instance_from_dict(None, None)

    def test_instance_from_dict_incomplete_dict_no_id(self):
        category_dict = dict(
            description='Category description',
            calculator='category.calculator',
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "No 'id' found in the dictionary",
            context.exception.message)

    def test_instance_from_dict_incomplete_dict_no_description(self):
        category_dict = dict(
            id='category-id',
            calculator='category.calculator',
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "No 'description' found in the dictionary",
            context.exception.message)

    def test_instance_from_dict_incomplete_dict_no_calculator(self):
        category_dict = dict(
            id='category-id',
            description='Category description',
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "No 'calculator' found in the dictionary",
            context.exception.message)

    def test_instance_from_dict_invalid_type_id(self):
        category_dict = dict(
            id=1,
            description='Category description',
            calculator='category.calculator',
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "'id' must be a string",
            context.exception.message)

    def test_instance_from_dict_should_not_raise_error_for_unicode_id(self):
        category_dict = dict(
            id=u'category-id',
            description='Category description',
            calculator=u'genweb6.core.tests.test_category.MockCalculator',
        )
        Category.instance_from_dict(category_dict, None)

    def test_instance_from_dict_invalid_type_description(self):
        category_dict = dict(
            id="category-id",
            description=None,
            calculator='category.calculator',
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "'description' must be a string",
            context.exception.message)

    def test_instance_from_dict_should_not_raise_error_for_unicode_description(
            self):
        category_dict = dict(
            id="category-id",
            description=u'category-description',
            calculator=u'genweb6.core.tests.test_category.MockCalculator',
        )
        Category.instance_from_dict(category_dict, None)

    def test_instance_from_dict_invalid_type_calculator(self):
        category_dict = dict(
            id="category-id",
            description="Category description",
            calculator=[],
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "'calculator' must be a string",
            context.exception.message)

    def test_instance_from_dict_should_not_raise_error_for_unicode_calculator(
            self):
        category_dict = dict(
            id="category-id",
            description="Category description",
            calculator=u'genweb6.core.tests.test_category.MockCalculator',
        )
        Category.instance_from_dict(category_dict, None)

    def test_instance_from_dict_empty_id(self):
        category_dict = dict(
            id="",
            description='Category description',
            calculator='category.calculator',
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "'id' cannot be empty",
            context.exception.message)

    def test_instance_from_dict_empty_calculator(self):
        category_dict = dict(
            id="category-id",
            description='Category description',
            calculator='',
        )
        with self.assertRaises(ValueError) as context:
            Category.instance_from_dict(category_dict, None)
        self.assertEqual(
            "'calculator' cannot be empty",
            context.exception.message)

    def test_instance_from_dict_valid_dict_should_contain_not_none_values(self):
        category_dict = dict(
            id="category-id",
            description='Category description',
            type='Category type',
            frequency='Category frequency',
            calculator='mock.class_name',
        )

        def mock_instance_from_string(string, context):
            return Mock(string=string, context=context)
        with patch(
                'genweb6.core.indicators.model.Calculator.instance_from_string',
                side_effect=mock_instance_from_string):
            category = Category.instance_from_dict(category_dict, "context")

        self.assertEqual("category-id", category.id)
        self.assertEqual("Category description", category.description)
        self.assertEqual("Category type", category.type)
        self.assertEqual("Category frequency", category.frequency)
        self.assertEqual("mock.class_name", category.calculator.string)
        self.assertEqual("context", category.calculator.context)
        self.assertEqual(category, category.calculator.category)

    def test_instance_from_dict_valid_dict_should_contain_none_values_if_no_type_and_frequency(self):
        category_dict = dict(
            id="category-id",
            description='Category description',
            calculator='mock.class_name',
        )

        def mock_instance_from_string(string, context):
            return Mock(string=string, context=context)
        with patch(
                'genweb6.core.indicators.model.Calculator.instance_from_string',
                side_effect=mock_instance_from_string):
            category = Category.instance_from_dict(category_dict, "context")

        self.assertEqual("category-id", category.id)
        self.assertEqual("Category description", category.description)
        self.assertEqual(None, category.type)
        self.assertEqual(None, category.frequency)
        self.assertEqual("mock.class_name", category.calculator.string)
        self.assertEqual("context", category.calculator.context)
        self.assertEqual(category, category.calculator.category)
