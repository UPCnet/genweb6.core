# -*- coding: utf-8 -*-
from mock import Mock
from mock import patch

from genweb6.core.indicators import CalculatorException
from genweb6.core.indicators import Category
from genweb6.core.indicators import ClientException
from genweb6.core.indicators import Indicator
from genweb6.core.indicators import Registry
from genweb6.core.indicators import ReporterException
from genweb6.core.indicators import WebServiceReporter

import unittest


class TestReporter(unittest.TestCase):
    def setUp(self):
        pass

    def test_report_should_raise_error_if_invalid_type(self):
        reporter = WebServiceReporter("url", "api_key")
        with self.assertRaises(TypeError):
            reporter.report(None)
        with self.assertRaises(TypeError):
            reporter.report([])
        with self.assertRaises(TypeError):
            reporter.report(1)

    def test_report_should_not_raise_error_if_valid_type(self):
        reporter = WebServiceReporter("url", "api_key")
        with patch(
                'genweb6.core.indicators.reporter.WebServiceReporter._report_registry',
                side_effect=(None,)):
            reporter.report(Registry('context'))
        with patch(
                'genweb6.core.indicators.reporter.WebServiceReporter._report_indicator_dict',
                side_effect=(None,)):
            reporter.report({})
        with patch(
                'genweb6.core.indicators.reporter.WebServiceReporter._report_indicator',
                side_effect=(None,)):
            reporter.report(Indicator('service', 'id', 'description'))
        with patch(
                'genweb6.core.indicators.reporter.WebServiceReporter._report_category',
                side_effect=(None,)):
            reporter.report(Category(
                'id', 'description', 'type', 'frequency', 'calculator'))

    def test_report_registry_should_report_indicator_dicts(self):
        reporter = WebServiceReporter("url", "api_key")
        mock_report_indicator_dict = Mock()
        with patch('genweb6.core.indicators.reporter.WebServiceReporter._report_indicator_dict',
                   side_effect=mock_report_indicator_dict):
            reporter._report_registry(
                {'dict-1': 1,
                 'dict-2': 2,
                 'dict-3': 3,
                 'dict-4': 4,
                 })
        self.assertEqual(4, mock_report_indicator_dict.call_count)
        mock_report_indicator_dict.assert_any_call(1)
        mock_report_indicator_dict.assert_any_call(2)
        mock_report_indicator_dict.assert_any_call(3)
        mock_report_indicator_dict.assert_any_call(4)

    def test_report_indicator_dict_should_report_indicators(self):
        reporter = WebServiceReporter("url", "api_key")
        mock_report_indicator = Mock()
        with patch('genweb6.core.indicators.reporter.WebServiceReporter._report_indicator',
                   side_effect=mock_report_indicator):
            reporter._report_indicator_dict(
                {'indicator-1': 1,
                 'indicator-2': 2,
                 'indicator-3': 3,
                 'indicator-4': 4,
                 })
        self.assertEqual(4, mock_report_indicator.call_count)
        mock_report_indicator.assert_any_call(1)
        mock_report_indicator.assert_any_call(2)
        mock_report_indicator.assert_any_call(3)
        mock_report_indicator.assert_any_call(4)

    def test_report_indicator_should_update_indicator_and_categories(self):
        reporter = WebServiceReporter("url", "api_key")
        mock_update_indicator = Mock()
        mock_report_categories = Mock()
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=mock_update_indicator):
            with patch('genweb6.core.indicators.reporter.WebServiceReporter._report_indicator_categories',
                       side_effect=mock_report_categories):
                reporter._report_indicator(Mock())
        self.assertEqual(1, mock_update_indicator.call_count)
        self.assertEqual(1, mock_report_categories.call_count)

    def test_report_indicator_should_not_update_categories_if_specified(self):
        reporter = WebServiceReporter("url", "api_key")
        mock_update_indicator = Mock()
        mock_report_categories = Mock()
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=mock_update_indicator):
            with patch('genweb6.core.indicators.reporter.WebServiceReporter._report_indicator_categories',
                       side_effect=mock_report_categories):
                reporter._report_indicator(Mock(), report_categories=False)
        self.assertEqual(1, mock_update_indicator.call_count)
        self.assertEqual(0, mock_report_categories.call_count)

    def test_report_indicator_should_raise_reporter_exception_if_client_exception(self):
        reporter = WebServiceReporter("url", "api_key")
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=ClientException):
            with self.assertRaises(ReporterException):
                reporter._report_indicator(Mock(), report_categories=False)

    def test_report_indicator_should_raise_reporter_exception_if_calculator_exception(self):
        reporter = WebServiceReporter("url", "api_key")
        with patch('genweb6.core.indicators.client.Client.update_indicator'):
            with patch('genweb6.core.indicators.client.Client.update_category',
                       side_effect=CalculatorException('Oh!')):
                with self.assertRaises(ReporterException) as context:
                    reporter._report_indicator(
                        Mock(categories={'c1': Mock(), '2': Mock()}),
                        report_categories=True)
                self.assertEqual(
                    "Error when calculating category (Oh!)",
                    context.exception.message)

    def test_report_indicator_should_raise_reporter_exception_if_reporter_exception(self):
        reporter = WebServiceReporter("url", "api_key")
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=(None,)):
            with patch('genweb6.core.indicators.reporter.WebServiceReporter._report_indicator_categories',
                       side_effect=ReporterException):
                with self.assertRaises(ReporterException):
                    reporter._report_indicator(Mock(), report_categories=True)

    def test_report_indicator_categories_should_report_categories(self):
        reporter = WebServiceReporter("url", "api_key")
        mock_report_category = Mock()
        mock_categories = {'one': 1, 'two': 2, 'three': 3}
        with patch('genweb6.core.indicators.reporter.WebServiceReporter._report_category',
                   side_effect=mock_report_category):
            reporter._report_indicator_categories(
                Mock(categories=mock_categories))
        self.assertEqual(3, mock_report_category.call_count)
        mock_report_category.assert_any_call(1)
        mock_report_category.assert_any_call(2)
        mock_report_category.assert_any_call(3)

    def test_report_category_should_update_category(self):
        reporter = WebServiceReporter("url", "api_key")
        mock_update_category = Mock()
        with patch('genweb6.core.indicators.client.Client.update_category',
                   side_effect=mock_update_category):
            reporter._report_category(Mock())
        self.assertEqual(1, mock_update_category.call_count)

    def test_report_category_should_raise_reporter_exception_if_client_exception(self):
        reporter = WebServiceReporter("url", "api_key")
        with patch('genweb6.core.indicators.client.Client.update_category',
                   side_effect=ClientException):
            with self.assertRaises(ReporterException):
                reporter._report_category(Mock())
