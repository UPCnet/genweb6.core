# -*- coding: utf-8 -*-
from genweb6.core.indicators import Calculator

import unittest


class MockCalculator(Calculator):
    pass


class TestCalculator(unittest.TestCase):
    def setUp(self):
        pass

    def test_instance_from_string_nonexistent_module(self):
        with self.assertRaises(ValueError) as context:
            Calculator.instance_from_string(
                "module.does.not.exist.Class", None)
        self.assertEqual(
            "Class 'module.does.not.exist.Class' could not be instantiated "
            "(No module named module.does.not.exist)",
            context.exception.message)

    def test_instance_from_string_empty_module(self):
        with self.assertRaises(ValueError) as context:
            Calculator.instance_from_string(
                "ClassWithoutModule", None)
        self.assertEqual(
            "Class 'ClassWithoutModule' could not be instantiated "
            "(Empty module name)",
            context.exception.message)

    def test_instance_from_string_nonexistent_class(self):
        with self.assertRaises(ValueError) as context:
            Calculator.instance_from_string(
                "sys.Nonexistentclass", None)
        self.assertEqual(
            "Class 'sys.Nonexistentclass' could not be instantiated "
            "('module' object has no attribute 'Nonexistentclass')",
            context.exception.message)

    def test_instance_from_string_valid_class(self):
        calculator = Calculator.instance_from_string(
            'genweb6.core.tests.test_calculator.MockCalculator', "context")
        self.assertIsInstance(calculator, MockCalculator)
        self.assertEqual("context", calculator.context)
