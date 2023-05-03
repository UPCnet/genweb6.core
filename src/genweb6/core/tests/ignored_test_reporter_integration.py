# -*- coding: utf-8 -*-
from mock import Mock
from mock import patch

from genweb6.core.indicators import ClientException
from genweb6.core.indicators import Registry
from genweb6.core.indicators import ReporterException
from genweb6.core.indicators import WebServiceReporter

import os
import unittest


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.reporter = WebServiceReporter("url", "api_key")
        self.registry = Registry("context")
        self.registry.load_from_path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'indicators', '2-services.3-indicators'))
        self.registry_with_exception = Registry("context")
        self.registry_with_exception.load_from_path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'indicators', '1-service.1-indicator.1-category_exception'))

    def test_report_registry_should_update_indicators_and_categories(self):
        mock_update_indicator = Mock()
        mock_update_category = Mock()
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=mock_update_indicator):
            with patch(
                    'genweb6.core.indicators.client.Client.update_category',
                    side_effect=mock_update_category):
                self.reporter.report(self.registry)
        self.assertEqual(3, mock_update_indicator.call_count)
        mock_update_indicator.assert_any_call(
            'service-1', 'indicator-1', 'Indicator 1')
        mock_update_indicator.assert_any_call(
            'service-2', 'indicator-1', 'Indicator 1')
        mock_update_indicator.assert_any_call(
            'service-2', 'indicator-2', 'Indicator 2')

        self.assertEqual(6, mock_update_category.call_count)
        mock_update_category.assert_any_call(
            'service-1', 'indicator-1', 'category-1.1', 'Category 1.1',
            'type 1.1', 'frequency 1.1', 111)
        mock_update_category.assert_any_call(
            'service-1', 'indicator-1', 'category-1.2', 'Category 1.2',
            None, None, 112)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-1', 'category-1.1', 'Category 1.1',
            None, None, 211)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-1', 'category-1.2', 'Category 1.2',
            None, None, 212)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-2', 'category-2.1', 'Category 2.1',
            None, None, 221)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-2', 'category-2.2', 'Category 2.2',
            None, None, 222)

    def test_report_registry_should_raise_reporter_exception_if_client_exception(self):
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=ClientException('Something wrong with WS')):
            with patch(
                    'genweb6.core.indicators.client.Client.update_category',
                    side_effect=ClientException('Something wrong with WS')):
                with self.assertRaises(ReporterException) as context:
                    self.reporter.report(self.registry)
        self.assertEqual(
            'WS client exception (Something wrong with WS)',
            context.exception.message)

    def test_report_registry_should_raise_reporter_exception_if_calculator_exception(self):
        with patch('genweb6.core.indicators.client.Client.update_indicator'):
            with patch('genweb6.core.indicators.client.Client.update_category'):
                with self.assertRaises(ReporterException) as context:
                    self.reporter.report(self.registry_with_exception)
        self.assertEqual(
            'Error when calculating category (Oh!)',
            context.exception.message)

    def test_report_dict_should_update_indicators_and_categories(self):
        mock_update_indicator = Mock()
        mock_update_category = Mock()
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=mock_update_indicator):
            with patch(
                    'genweb6.core.indicators.client.Client.update_category',
                    side_effect=mock_update_category):
                self.reporter.report(self.registry['service-2'])
        self.assertEqual(2, mock_update_indicator.call_count)
        mock_update_indicator.assert_any_call(
            'service-2', 'indicator-1', 'Indicator 1')
        mock_update_indicator.assert_any_call(
            'service-2', 'indicator-2', 'Indicator 2')

        self.assertEqual(4, mock_update_category.call_count)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-1', 'category-1.1', 'Category 1.1',
            None, None, 211)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-1', 'category-1.2', 'Category 1.2',
            None, None, 212)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-2', 'category-2.1', 'Category 2.1',
            None, None, 221)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-2', 'category-2.2', 'Category 2.2',
            None, None, 222)

    def test_report_indicator_should_update_indicators_and_categories(self):
        mock_update_indicator = Mock()
        mock_update_category = Mock()
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=mock_update_indicator):
            with patch(
                    'genweb6.core.indicators.client.Client.update_category',
                    side_effect=mock_update_category):
                self.reporter.report(self.registry['service-2']['indicator-2'])
        self.assertEqual(1, mock_update_indicator.call_count)
        mock_update_indicator.assert_any_call(
            'service-2', 'indicator-2', 'Indicator 2')

        self.assertEqual(2, mock_update_category.call_count)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-2', 'category-2.1', 'Category 2.1',
            None, None, 221)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-2', 'category-2.2', 'Category 2.2',
            None, None, 222)

    def test_report_category_should_update_indicators_and_categories(self):
        mock_update_indicator = Mock()
        mock_update_category = Mock()
        with patch('genweb6.core.indicators.client.Client.update_indicator',
                   side_effect=mock_update_indicator):
            with patch(
                    'genweb6.core.indicators.client.Client.update_category',
                    side_effect=mock_update_category):
                self.reporter.report(
                    self.registry['service-2']['indicator-2']['category-2.2'])
        self.assertEqual(0, mock_update_indicator.call_count)

        self.assertEqual(1, mock_update_category.call_count)
        mock_update_category.assert_any_call(
            'service-2', 'indicator-2', 'category-2.2', 'Category 2.2',
            None, None, 222)

    def test_report_category_should_raise_reporter_exception_if_client_exception(self):
        with patch(
                'genweb6.core.indicators.client.Client.update_category',
                side_effect=ClientException('Something wrong with WS')):
            with self.assertRaises(ReporterException) as context:
                self.reporter.report(
                    self.registry['service-2']['indicator-2']['category-2.2'])
        self.assertEqual(
            'WS client exception (Something wrong with WS)',
            context.exception.message)
