# -*- coding: utf-8 -*-
from mock import Mock
from mock import patch
from yaml.scanner import ScannerError

from genweb5.core.indicators import Registry
from genweb5.core.indicators import RegistryException

import os
import unittest


class TestRegistry(unittest.TestCase):
    def setUp(self):
        pass

    def test_load_from_path_should_raise_error_if_path_does_not_exist(self):
        registry = Registry('context')
        with self.assertRaises(RegistryException) as context:
            registry.load_from_path("/non/existent/path")
        self.assertEqual(
            "[Errno 2] No such file or directory: '/non/existent/path'",
            str(context.exception))

    def test_load_from_path_should_raise_error_if_path_is_file(self):
        registry = Registry('context')
        with self.assertRaises(RegistryException) as context:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'indicators', 'definitions', 'empty.txt')
            registry.load_from_path(path)
        self.assertEqual(
            "[Errno 20] Not a directory: '{0}'".format(path),
            str(context.exception))

    def test_load_from_path_should_not_load_from_file_path_if_no_files_in_path(
            self):
        registry = Registry('context')
        mock_from_file_path = Mock()
        with patch(
                'genweb5.core.indicators.registry.Registry._load_from_file_path',
                side_effect=mock_from_file_path
        ):
            registry.load_from_path(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'indicators', 'empty'))
        # The folder is not actually empty, it contains a .gitkeep file so that
        # it can be tracked by Git. Ideally it should be empty but there is no
        # way to upload an empty folder to Git.
        self.assertEqual(1, mock_from_file_path.call_count)

    def test_load_from_path_should_load_from_file_path_if_files_in_path(self):
        registry = Registry('context')
        mock_from_file_path = Mock()
        with patch(
                'genweb5.core.indicators.registry.Registry._load_from_file_path',
                side_effect=mock_from_file_path
        ):
            registry.load_from_path(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'indicators', '3-files'))
        self.assertEqual(3, mock_from_file_path.call_count)

    def test_load_from_file_path_should_raise_error_if_invalid_file(self):
        registry = Registry('context')
        with self.assertRaises(ScannerError) as self.context:
            registry._load_from_file_path(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'indicators', 'definitions', 'invalid.yaml'))

    def test_load_from_file_path_should_not_add_from_dict_if_empty_file(self):
        registry = Registry('context')
        mock_add_indicator_from_dict = Mock()
        with patch(
                'genweb5.core.indicators.registry.Registry._add_indicator_from_dict',
                side_effect=mock_add_indicator_from_dict
        ):
            registry._load_from_file_path(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'indicators', 'definitions', 'empty.txt'))
        self.assertEqual(0, mock_add_indicator_from_dict.call_count)

    def test_load_from_file_path_should_add_from_dict_if_valid_file(self):
        registry = Registry('context')
        mock_add_indicator_from_dict = Mock()
        with patch(
                'genweb5.core.indicators.registry.Registry._add_indicator_from_dict',
                side_effect=mock_add_indicator_from_dict
        ):
            registry._load_from_file_path(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'indicators', 'definitions', '3-indicators.yaml'))
        self.assertEqual(3, mock_add_indicator_from_dict.call_count)

    def test_add_indicator_should_override_existent_indicators(self):
        registry = Registry('context')
        mock_indicator_old = Mock(service='s1', id='i1', description='old one')
        mock_indicator_new = Mock(service='s1', id='i1', description='new one')
        with patch('genweb5.core.indicators.model.Indicator.instance_from_dict',
                   side_effect=(mock_indicator_old,
                                mock_indicator_new,
                                mock_indicator_old)):
            registry._add_indicator_from_dict({})
            self.assertEqual(
                mock_indicator_old, registry._indicators['s1']['i1'])
            registry._add_indicator_from_dict({})
            self.assertEqual(
                mock_indicator_new, registry._indicators['s1']['i1'])
            registry._add_indicator_from_dict({})
            self.assertEqual(
                mock_indicator_old, registry._indicators['s1']['i1'])

    def test_getitem_should_return_indicators_dict_getitem(self):
        registry = Registry('context')
        registry._indicators['service1'] = "s1"
        self.assertEqual(
            registry._indicators['service1'], registry['service1'])

    def test_values_should_return_indicators_dict_values(self):
        registry = Registry('context')
        registry._indicators['service1'] = "s1"
        registry._indicators['service2'] = "s2"
        self.assertEqual(
            registry.values(), registry._indicators.values())

    def test_registry_should_be_iterable_on_service_id(self):
        registry = Registry('context')
        registry._indicators['service1'] = "s1"
        registry._indicators['service2'] = "s2"
        self.assertEqual(2, len(list(registry.__iter__())))
        self.assertIn('service1', list(registry.__iter__()))
        self.assertIn('service2', list(registry.__iter__()))
