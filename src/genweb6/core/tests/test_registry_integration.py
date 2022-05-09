# -*- coding: utf-8 -*-
from genweb6.core.indicators import Calculator
from genweb6.core.indicators import CalculatorException
from genweb6.core.indicators import Registry
from genweb6.core.indicators import RegistryException

import os
import unittest


class MockCalculator111(Calculator):
    def calculate(self):
        return 111


class MockCalculator112(Calculator):
    def calculate(self):
        return 112


class MockCalculator211(Calculator):
    def calculate(self):
        return 211


class MockCalculator212(Calculator):
    def calculate(self):
        return 212


class MockCalculator221(Calculator):
    def calculate(self):
        return 221


class MockCalculator222(Calculator):
    def calculate(self):
        return 222


class MockCalculatorWithException(Calculator):
    def calculate(self):
        raise CalculatorException('Oh!')


class TestRegistry(unittest.TestCase):
    def setUp(self):
        pass

    def test_load_from_empty_path_should_not_add_indicators(self):
        registry = Registry("context")
        registry.load_from_path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'indicators', 'empty'))
        self.assertEqual(0, len(registry._indicators))

    def test_load_from_path_with_invalid_files_should_not_add_indicators(
            self):
        registry = Registry("context")
        with self.assertRaises(RegistryException):
            registry.load_from_path(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'indicators', '2-services.4-indicators.2-invalid'))
        self.assertEqual(0, len(registry._indicators))

    def test_load_from_non_empty_path_should_add_indicators(self):
        registry = Registry("context")
        registry.load_from_path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'indicators', '2-services.3-indicators'))
        self.assertEqual(2, len(registry._indicators))
        self.assertEqual(1, len(registry._indicators['service-1']))
        self.assertEqual(2, len(registry._indicators['service-2']))

        self.assertEqual(
            'indicator-1', registry['service-1']['indicator-1'].id)
        self.assertEqual(
            'Indicator 1', registry['service-1']['indicator-1'].description)
        self.assertEqual(
            'category-1.1',
            registry['service-1']['indicator-1']['category-1.1'].id)
        self.assertEqual(
            'Category 1.1',
            registry['service-1']['indicator-1']['category-1.1'].description)
        self.assertEqual(
            'type 1.1',
            registry['service-1']['indicator-1']['category-1.1'].type)
        self.assertEqual(
            'frequency 1.1',
            registry['service-1']['indicator-1']['category-1.1'].frequency)
        self.assertEqual(
            111,
            registry['service-1']['indicator-1']['category-1.1'].value)
        self.assertEqual(
            'category-1.2',
            registry['service-1']['indicator-1']['category-1.2'].id)
        self.assertEqual(
            'Category 1.2',
            registry['service-1']['indicator-1']['category-1.2'].description)
        self.assertEqual(
            None,
            registry['service-1']['indicator-1']['category-1.2'].type)
        self.assertEqual(
            None,
            registry['service-1']['indicator-1']['category-1.2'].frequency)
        self.assertEqual(
            112,
            registry['service-1']['indicator-1']['category-1.2'].value)

        self.assertEqual(
            'indicator-1', registry['service-2']['indicator-1'].id)
        self.assertEqual(
            'Indicator 1', registry['service-2']['indicator-1'].description)
        self.assertEqual(
            'category-1.1',
            registry['service-2']['indicator-1']['category-1.1'].id)
        self.assertEqual(
            'Category 1.1',
            registry['service-2']['indicator-1']['category-1.1'].description)
        self.assertEqual(
            211,
            registry['service-2']['indicator-1']['category-1.1'].value)
        self.assertEqual(
            'category-1.2',
            registry['service-2']['indicator-1']['category-1.2'].id)
        self.assertEqual(
            'Category 1.2',
            registry['service-2']['indicator-1']['category-1.2'].description)
        self.assertEqual(
            212,
            registry['service-2']['indicator-1']['category-1.2'].value)

        self.assertEqual(
            'indicator-2', registry['service-2']['indicator-2'].id)
        self.assertEqual(
            'Indicator 2', registry['service-2']['indicator-2'].description)
        self.assertEqual(
            'category-2.1',
            registry['service-2']['indicator-2']['category-2.1'].id)
        self.assertEqual(
            'Category 2.1',
            registry['service-2']['indicator-2']['category-2.1'].description)
        self.assertEqual(
            221,
            registry['service-2']['indicator-2']['category-2.1'].value)
        self.assertEqual(
            'category-2.2',
            registry['service-2']['indicator-2']['category-2.2'].id)
        self.assertEqual(
            'Category 2.2',
            registry['service-2']['indicator-2']['category-2.2'].description)
        self.assertEqual(
            222,
            registry['service-2']['indicator-2']['category-2.2'].value)
