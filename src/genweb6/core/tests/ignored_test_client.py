# -*- coding: utf-8 -*-

"""Unit tests for the Indicators Web Service client."""

from mock import MagicMock
from mock import patch
from requests.exceptions import ConnectionError

from genweb6.core.indicators.client import Client
from genweb6.core.indicators.client import ClientException

import json
import unittest
import datetime


class TestWSClient(unittest.TestCase):
    def setUp(self):
        self.client = Client(
            url_base='http://url_base')

    def test_get_headers(self):
        client = Client('')
        self.assertEquals(
            client._get_headers(),
            {'Accept': 'application/json',
             'Content-type': 'application/json'})

    def test_get_headers_with_nondefault_accept(self):
        client = Client('', header_accept='application/cooltype')
        self.assertEquals(
            client._get_headers(),
            {'Accept': 'application/cooltype',
             'Content-type': 'application/json'})

    def test_get_headers_with_nondefault_content_type(self):
        client = Client('', header_content_type='application/cooltype')
        self.assertEquals(
            client._get_headers(),
            {'Accept': 'application/json',
             'Content-type': 'application/cooltype'})

    def test_get_headers_with_key(self):
        client = Client('', api_key='abc123')
        self.assertEquals(
            client._get_headers(),
            {'Accept': 'application/json',
             'Content-type': 'application/json',
             'api_key': 'abc123'})

    def test_get_headers_with_numeric_key(self):
        client = Client('', api_key=123)
        self.assertEquals(
            client._get_headers(),
            {'Accept': 'application/json',
             'Content-type': 'application/json',
             'api_key': '123'})

    def test_get_headers_with_list_key(self):
        client = Client('', api_key=[1, 2, 3])
        self.assertEquals(
            client._get_headers(),
            {'Accept': 'application/json',
             'Content-type': 'application/json',
             'api_key': '[1, 2, 3]'})

    def test_parse_date_modified(self):
        date_modified_str = '2016-06-13T17:39:44.545+02:00'
        date_modified_gold = datetime.datetime(2016, 6, 13, 17, 39, 44)
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

    def test_parse_date_modified_is_empty(self):
        date_modified_str = ''
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

    def test_parse_date_modified_is_none(self):
        date_modified_str = None
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

    def test_parse_date_modified_has_wrong_type(self):
        date_modified_str = 20160613
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

        date_modified_str = [20160613]
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

    def test_parse_date_modified_has_wrong_format(self):
        # Time not provided
        date_modified_str = '2016-06-13'
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

        # Seconds not provided
        date_modified_str = '2016-06-13T17:39'
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

        # Month is not zero-padded
        date_modified_str = '2016-6-13T17:39:44.545+02:00'
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

        # Date separator is not dash
        date_modified_str = '2016/06/13T17:39:44.545+02:00'
        date_modified_gold = None
        self.assertEqual(
            date_modified_gold,
            self.client._parse_date_modified(date_modified_str))

    def test_parse_response_result_with_defined_exception(self):
        response = json.loads('''
            {
                "status": "ERROR",
                "message": "This is the message"
            }''')
        try:
            self.client._parse_response_result(response)
            self.fail("ClientException should have been raised")
        except ClientException as cexception:
            self.assertEqual(
                "Error status ERROR: This is the message",
                cexception.message)

    def test_parse_response_list_indicators_empty(self):
        response = json.loads('''
            {
            }''')
        try:
            self.client._parse_response_list_indicators(response)
            self.fail("ClientException should have been raised")
        except ClientException as cexception:
            self.assertEqual(
                "'indicadors' is not present in the response",
                cexception.message)

    def test_parse_response_list_categories_empty(self):
        response = json.loads('''
            {
            }''')
        try:
            self.client._parse_response_list_categories(response)
            self.fail("ClientException should have been raised")
        except ClientException as cexception:
            self.assertEqual(
                "'categories' is not present in the response",
                cexception.message)

    def test_parse_response_list_indicators_invalid_type(self):
        response = json.loads('''
{
   "idServei": "7887",
   "indicadors":
   {
      "dataModificacioIndicador": "2016-04-13T15:35:00.123",
      "descripcioIndicador": "centenars de centenars",
      "idIndicador": "Nombre d'usuaris"
   }
}''')
        try:
            self.client._parse_response_list_indicators(response)
            self.fail("ClientException should have been raised")
        except ClientException as cexception:
            self.assertEqual(
                "Invalid type of 'indicadors'",
                cexception.message)

        response = json.loads('''
{
   "idServei": "7887",
   "indicadors": 123
}''')
        try:
            self.client._parse_response_list_indicators(response)
            self.fail("ClientException should have been raised")
        except ClientException as cexception:
            self.assertEqual(
                "Invalid type of 'indicadors'",
                cexception.message)

    def test_parse_response_list_categories_invalid_type(self):
        response = json.loads('''
{
   "idServei": "7887",
   "idIndicador": "indicador_1",
   "categories":
   {
      "dataModificacioCategoria": "2015-12-03T19:15:50.231",
      "descripcioCategoria": "categoria important",
      "idCategoria": "Nombre d'usuaris",
      "valor": "578"
   }
}''')
        try:
            self.client._parse_response_list_categories(response)
            self.fail("ClientException should have been raised")
        except ClientException as cexception:
            self.assertEqual(
                "Invalid type of 'categories'",
                cexception.message)

        response = json.loads('''
{
   "idServei": "7887",
   "idIndicador": "indicador-1",
   "categories": 123
}''')
        try:
            self.client._parse_response_list_categories(response)
            self.fail("ClientException should have been raised")
        except ClientException as cexception:
            self.assertEqual(
                "Invalid type of 'categories'",
                cexception.message)

    def test_parse_response_list_indicators_not_empty(self):
        response = json.loads('''
{
   "idServei": "7887",
   "indicadors":
   [
       {
          "dataModificacioIndicador": "2016-04-13T15:35:00.123",
          "descripcioIndicador": "centenars de centenars",
          "idIndicador": "Nombre d'usuaris"
       },
       {
          "dataModificacioIndicador": "wrong format",
          "descripcioIndicador": "centenars de centenars 2",
          "idIndicador": "Nombre d'usuaris 2"
       },
       {}
   ]
}
''')
        results = self.client._parse_response_list_indicators(response)
        self.assertEqual(len(results), 3)
        self.assertEqual(
            results[0],
            Client.Indicator(
                date_modified=datetime.datetime(2016, 4, 13, 15, 35, 0),
                description=u"centenars de centenars",
                identifier=u"Nombre d'usuaris"))

        self.assertEqual(
            results[1],
            Client.Indicator(
                date_modified=None,
                description=u"centenars de centenars 2",
                identifier=u"Nombre d'usuaris 2"))

        self.assertEqual(
            results[2],
            Client.Indicator(
                date_modified=None,
                description=u'',
                identifier=u''))

    def test_parse_response_list_categories_not_empty(self):
        response = json.loads('''
{
   "idServei": "7887",
   "idIndicador": "indicador-1",
   "categories":
   [
       {
          "dataModificacioCategoria": "2015-12-03T19:15:50.231",
          "descripcioCategoria": "categoria important",
          "idCategoria": "categoria-1",
          "tipusIndicador": "online",
          "frequencia": "dia",
          "valor": "578"
       },
       {
          "dataModificacioCategoria": "wrong date",
          "descripcioCategoria": "categoria important 2",
          "idCategoria": "categoria-2",
          "tipusIndicador": "diferit",
          "frequencia": "hora",
          "valor": "678"
       },
       {}
   ]
}
''')
        results = self.client._parse_response_list_categories(response)
        self.assertEqual(len(results), 3)
        self.assertEqual(
            results[0],
            Client.Category(
                date_modified=datetime.datetime(2015, 12, 3, 19, 15, 50),
                description=u"categoria important",
                identifier=u"categoria-1",
                type=u"online",
                frequency=u"dia",
                value=u"578"))

        self.assertEqual(
            results[1],
            Client.Category(
                date_modified=None,
                description=u'categoria important 2',
                identifier=u'categoria-2',
                type=u"diferit",
                frequency=u"hora",
                value=u'678'))

        self.assertEqual(
            results[2],
            Client.Category(
                date_modified=None,
                description=u'',
                identifier=u'',
                type=u'',
                frequency=u'',
                value=u''))

    def test_list_indicators(self):
        # Parameter service_id empty
        try:
            self.client.list_indicators("  \n   \t  ")
            self.fail("ClientException should have been raised")
        except ClientException as exception:
            self.assertEqual("Parameter 'service_id' cannot be empty",
                             exception.message)
        try:
            self.client.list_indicators(None)
            self.fail("ClientException should have been raised")
        except ClientException as exception:
            self.assertEqual("Parameter 'service_id' cannot be empty",
                             exception.message)

        # Connection error
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=ConnectionError):
            try:
                self.client.list_indicators(1)
                self.fail("ClientException should have been raised")
            except ClientException as exception:
                self.assertEqual("The connection with '{0}' could not be "
                                 "established".format(self.client.url_base),
                                 exception.message)
        # Response status is not OK
        response_mock = MagicMock(status_code=500)
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)):
            try:
                self.client.list_indicators(1)
                self.fail("ClientException should have been raised")
            except ClientException as exception:
                self.assertEqual("Status code is not OK (500)",
                                 exception.message)

        # Response status is OK
        response_mock = MagicMock(status_code=200)
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)), patch(
                'genweb6.core.indicators.client.Client._parse_response_list_indicators',
                side_effect=([],)):
            self.assertEqual([], self.client.list_indicators(1))

        # Response text is empty
        response_mock = MagicMock(status_code=200, text=u'')
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)):
            self.assertEqual([], self.client.list_indicators(1))

        response_mock = MagicMock(status_code=200, text='')
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)):
            self.assertEqual([], self.client.list_indicators(1))

    def test_list_indicators_with_count_parameter(self):
        response_mock = MagicMock(status_code=200)
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock for _ in range(5))), patch(
                'genweb6.core.indicators.client.Client._parse_response_list_indicators',
                side_effect=([1, 2, 3, 4, 5, 6, 7, 8] for _ in range(5))):

            self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8],
                             self.client.list_indicators(1))
            self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8],
                             self.client.list_indicators(1, None))
            self.assertEqual([],
                             self.client.list_indicators(1, 0))
            self.assertEqual([1, 2, 3, 4, 5],
                             self.client.list_indicators(1, 5))
            self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8],
                             self.client.list_indicators(1, 10))

    def test_list_indicators_should_raise_client_exception_when_url_is_none(self):
        client = Client(
            url_base=None)
        with self.assertRaises(ClientException):
            client.list_indicators('service-id')

    def test_list_indicators_should_raise_client_exception_when_url_is_empty(self):
        client = Client(
            url_base='')
        with self.assertRaises(ClientException):
            client.list_indicators('service-id')

    def test_list_indicators_should_raise_client_exception_when_url_is_invalid(self):
        client = Client(
            url_base='http://invalid')
        with self.assertRaises(ClientException):
            client.list_indicators('service-id')

    def test_list_indicators_should_raise_client_exception_when_url_has_invalid_schema(self):
        client = Client(
            url_base='ttp://example.com')
        with self.assertRaises(ClientException):
            client.list_indicators('service-id')

    def test_list_categories(self):
        # Parameter service_id empty
        try:
            self.client.list_categories("  \n   \t  ", "indicator-1")
            self.fail("ClientException should have been raised")
        except ClientException as exception:
            self.assertEqual("Parameter 'service_id' cannot be empty",
                             exception.message)
        try:
            self.client.list_categories(None, "indicator-1")
            self.fail("ClientException should have been raised")
        except ClientException as exception:
            self.assertEqual("Parameter 'service_id' cannot be empty",
                             exception.message)

        # Parameter indicator_id empty
        try:
            self.client.list_categories("service-1", "  \n   \t  ")
            self.fail("ClientException should have been raised")
        except ClientException as exception:
            self.assertEqual("Parameter 'indicator_id' cannot be empty",
                             exception.message)
        try:
            self.client.list_categories("service-1", None)
            self.fail("ClientException should have been raised")
        except ClientException as exception:
            self.assertEqual("Parameter 'indicator_id' cannot be empty",
                             exception.message)

        # Connection error
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=ConnectionError):
            try:
                self.client.list_categories(1, 1)
                self.fail("ClientException should have been raised")
            except ClientException as exception:
                self.assertEqual("The connection with '{0}' could not be "
                                 "established".format(self.client.url_base),
                                 exception.message)
        # Response status is not OK
        response_mock = MagicMock(status_code=500)
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)):
            try:
                self.client.list_categories(1, 1)
                self.fail("ClientException should have been raised")
            except ClientException as exception:
                self.assertEqual("Status code is not OK (500)",
                                 exception.message)

        # Response status is OK
        response_mock = MagicMock(status_code=200)
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)), patch(
                'genweb6.core.indicators.client.Client._parse_response_list_categories',
                side_effect=([],)):
            self.assertEqual([], self.client.list_categories(1, 1))

        # Response text is empty
        response_mock = MagicMock(status_code=200, text=u'')
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)):
            self.assertEqual([], self.client.list_categories(1, 1))

        response_mock = MagicMock(status_code=200, text='')
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock,)):
            self.assertEqual([], self.client.list_categories(1, 1))

    def test_list_categories_with_count_parameter(self):
        response_mock = MagicMock(status_code=200)
        with patch('genweb6.core.indicators.client.requests.get',
                   side_effect=(response_mock for _ in range(5))), patch(
                'genweb6.core.indicators.client.Client._parse_response_list_categories',
                side_effect=([1, 2, 3, 4, 5, 6, 7, 8] for _ in range(5))):

            self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8],
                             self.client.list_categories(1, 1))
            self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8],
                             self.client.list_categories(1, 1, count=None))
            self.assertEqual([],
                             self.client.list_categories(1, 1, count=0))
            self.assertEqual([1, 2, 3, 4, 5],
                             self.client.list_categories(1, 1, count=5))
            self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8],
                             self.client.list_categories(1, 1, count=10))

    def test_list_categories_should_raise_client_exception_when_url_is_none(self):
        client = Client(
            url_base=None)
        with self.assertRaises(ClientException):
            client.list_categories('service-id', 'indicator-id')

    def test_list_categories_should_raise_client_exception_when_url_is_empty(self):
        client = Client(
            url_base='')
        with self.assertRaises(ClientException):
            client.list_categories('service-id', 'indicator-id')

    def test_list_categories_should_raise_client_exception_when_url_is_invalid(self):
        client = Client(
            url_base='http://invalid')
        with self.assertRaises(ClientException):
            client.list_categories('service-id', 'indicator-id')

    def test_list_categories_should_raise_client_exception_when_url_has_invalid_schema(self):
        client = Client(
            url_base='ttp://example.com')
        with self.assertRaises(ClientException):
            client.list_categories('service-id', 'indicator-id')

    def test_validate_param_is_not_empty_string_should_raise_when_blanks(self):
        with self.assertRaises(ClientException) as context:
            self.client._validate_param_is_not_empty_string(
                'value', ' \t  \n  ')
        self.assertEqual(
            "Parameter 'value' cannot be empty string",
            context.exception.message)

    def test_validate_param_is_not_empty_string_should_not_raise_when_0(self):
        self.assertIsNone(
            self.client._validate_param_is_not_empty_string('value', 0))

    def test_validate_update_indicator_parameters_with_correct_params(self):
        self.assertEqual(
            None,
            self.client._validate_update_indicator_parameters(
                service_id='service_id',
                indicator_id='indicator_id',
                indicator_description='indicator_description',
            ))

    def test_validate_update_indicator_parameters_with_empty_service(self):
        for service_id in (None, '', '\n\t   \n\t\t'):
            with self.assertRaises(ClientException) as context:
                self.client._validate_update_indicator_parameters(
                    service_id=service_id,
                    indicator_id='indicator_id',
                    indicator_description='indicator_description',
                )
            self.assertEqual(
                context.exception.message,
                "Parameter 'service_id' cannot be empty or None")

    def test_validate_update_indicator_parameters_with_empty_indicator(self):
        for indicator_id in (None, '', '\n\t   \n\t\t'):
            with self.assertRaises(ClientException) as context:
                self.client._validate_update_indicator_parameters(
                    service_id='service_id',
                    indicator_id=indicator_id,
                    indicator_description='indicator_description',
                )
            self.assertEqual(
                context.exception.message,
                "Parameter 'indicator_id' cannot be empty or None")

    def test_validate_update_indicator_parameters_with_none_indicator_desc(self):
        with self.assertRaises(ClientException) as context:
            self.client._validate_update_indicator_parameters(
                service_id='service_id',
                indicator_id='indicator_id',
                indicator_description=None,
            )
        self.assertEqual(
            context.exception.message,
            "Parameter 'indicator_description' cannot be None")

    def test_validate_update_category_parameters_with_correct_params(self):
        self.assertEqual(
            None,
            self.client._validate_update_category_parameters(
                service_id='service_id',
                indicator_id='indicator_id',
                category_id='category_id',
                category_description='category_description',
                category_type='category_type',
                category_frequency='category_frequency',
                category_value='category_value',
            ))

    def test_validate_update_category_parameters_with_empty_service(self):
        for service_id in (None, '', '\n\t   \n\t\t'):
            with self.assertRaises(ClientException) as context:
                self.client._validate_update_category_parameters(
                    service_id=service_id,
                    indicator_id='indicator_id',
                    category_id='category_id',
                    category_description='category_description',
                    category_type='category_type',
                    category_frequency='category_frequency',
                    category_value='category_value',
                )
            self.assertEqual(
                context.exception.message,
                "Parameter 'service_id' cannot be empty or None")

    def test_validate_update_category_parameters_with_empty_indicator(self):
        for indicator_id in (None, '', '\n\t   \n\t\t'):
            with self.assertRaises(ClientException) as context:
                self.client._validate_update_category_parameters(
                    service_id='service_id',
                    indicator_id=indicator_id,
                    category_id='category_id',
                    category_description='category_description',
                    category_type='category_type',
                    category_frequency='category_frequency',
                    category_value='category_value',
                )
            self.assertEqual(
                context.exception.message,
                "Parameter 'indicator_id' cannot be empty or None")

    def test_validate_update_category_parameters_with_empty_category_id(self):
        for category_id in (None, '', '\n\t   \n\t\t'):
            with self.assertRaises(ClientException) as context:
                self.client._validate_update_category_parameters(
                    service_id='service_id',
                    indicator_id='indicator_id',
                    category_id=category_id,
                    category_description='category_description',
                    category_type='category_type',
                    category_frequency='category_frequency',
                    category_value='category_value',
                )
            self.assertEqual(
                context.exception.message,
                "Parameter 'category_id' cannot be empty or None")

    def test_validate_update_category_parameters_with_none_category_desc(self):
        with self.assertRaises(ClientException) as context:
            self.client._validate_update_category_parameters(
                service_id='service_id',
                indicator_id='indicator_id',
                category_id='category_id',
                category_description=None,
                category_type='category_type',
                category_frequency='category_frequency',
                category_value='category_value',
            )
        self.assertEqual(
            context.exception.message,
            "Parameter 'category_description' cannot be None")

    def test_validate_update_category_parameters_with_empty_category_desc_should_not_raise(self):
        for category_description in ('', '\n\t   \n\t\t'):
            self.assertEqual(
                None,
                self.client._validate_update_category_parameters(
                    service_id='service_id',
                    indicator_id='indicator_id',
                    category_id='category_id',
                    category_description=category_description,
                    category_type='category_type',
                    category_frequency='category_frequency',
                    category_value='category_value',
                ))

    def test_validate_update_category_parameters_with_empty_category_type_should_not_raise(self):
        for category_type in ('', '\n\t   \n\t\t'):
            self.assertEqual(
                None,
                self.client._validate_update_category_parameters(
                    service_id='service_id',
                    indicator_id='indicator_id',
                    category_id='category_id',
                    category_description='category_description',
                    category_type=category_type,
                    category_frequency='category_frequency',
                    category_value='category_value',
                ))

    def test_validate_update_category_parameters_with_none_category_type_should_not_raise(self):
        self.assertEqual(
            None,
            self.client._validate_update_category_parameters(
                service_id='service_id',
                indicator_id='indicator_id',
                category_id='category_id',
                category_description='category_description',
                category_type=None,
                category_frequency='category_frequency',
                category_value='category_value',
            ))

    def test_validate_update_category_parameters_with_empty_category_frequency_should_not_raise(self):
        for category_frequency in ('', '\n\t   \n\t\t'):
            self.assertEqual(
                None,
                self.client._validate_update_category_parameters(
                    service_id='service_id',
                    indicator_id='indicator_id',
                    category_id='category_id',
                    category_description='category_description',
                    category_type='category_type',
                    category_frequency=category_frequency,
                    category_value='category_value',
                ))

    def test_validate_update_category_parameters_with_none_category_frequency_should_not_raise(self):
        self.assertEqual(
            None,
            self.client._validate_update_category_parameters(
                service_id='service_id',
                indicator_id='indicator_id',
                category_id='category_id',
                category_description='category_description',
                category_type='category_type',
                category_frequency=None,
                category_value='category_value',
            ))

    def test_validate_update_category_parameters_with_none_category_val_should_raise(self):
        with self.assertRaises(ClientException) as context:
            self.client._validate_update_category_parameters(
                service_id='service_id',
                indicator_id='indicator_id',
                category_id='category_id',
                category_description='category_description',
                category_type='category_type',
                category_frequency='category_frequency',
                category_value=None,
            )
        self.assertEqual(
            context.exception.message,
            "Parameter 'category_value' cannot be None")

    def test_validate_update_category_parameters_with_empty_category_val_should_not_raise(self):
        for category_value in ('', '\n\t   \n\t\t'):
            self.assertEqual(
                None,
                self.client._validate_update_category_parameters(
                    service_id='service_id',
                    indicator_id='indicator_id',
                    category_id='category_id',
                    category_description='category_description',
                    category_type='category_type',
                    category_frequency='category_frequency',
                    category_value=category_value,
                ))

    def test_update_category_should_raise_client_exception_when_url_is_none(self):
        client = Client(
            url_base=None)
        with self.assertRaises(ClientException):
            client.update_category(
                'service-id', 'indicator-id',
                'category-id', 'category-description', 'category-type',
                'category-frequency', 'category-value')

    def test_update_category_should_raise_client_exception_when_url_is_empty(self):
        client = Client(
            url_base='')
        with self.assertRaises(ClientException):
            client.update_category(
                'service-id', 'indicator-id',
                'category-id', 'category-description', 'category-type',
                'category-frequency', 'category-value')

    def test_update_category_should_raise_client_exception_when_url_is_invalid(self):
        client = Client(
            url_base='http://invalid')
        with self.assertRaises(ClientException):
            client.update_category(
                'service-id', 'indicator-id',
                'category-id', 'category-description', 'category-type',
                'category-frequency', 'category-value')

    def test_update_category_should_raise_client_exception_when_url_has_invalid_schema(self):
        client = Client(
            url_base='ttp://exampl.com')
        with self.assertRaises(ClientException):
            client.update_category(
                'service-id', 'indicator-id',
                'category-id', 'category-description', 'category-type',
                'category-frequency', 'category-value')

    def test_parse_update_response_code_200(self):
        response_mock = MagicMock(status_code=200)
        self.assertEqual(
            True, self.client._parse_update_response(response_mock))

    def test_parse_update_response_code_non200(self):
        response_mock = MagicMock(
            status_code=400,
            headers={})
        with self.assertRaises(ClientException) as context:
            self.client._parse_update_response(response_mock)
        self.assertEqual(
            context.exception.message, "Status code is not OK (400)")

    def test_parse_update_response_code_non200_with_xml(self):
        response_mock = MagicMock(
            status_code=400,
            headers={'Content-Type': 'application/xml'})
        with self.assertRaises(ClientException) as context:
            self.client._parse_update_response(response_mock)
        self.assertEqual(
            context.exception.message, "Status code is not OK (400)")

    def test_parse_update_response_should_raise_str_message_when_code_non200_and_message_none(self):
        response_mock = MagicMock(
            status_code=400,
            headers={'Content-Type': 'application/json'},
            text=u'{"message": null}')
        with self.assertRaises(ClientException) as context:
            self.client._parse_update_response(response_mock)
        self.assertEqual(
            context.exception.message,
            "Status code is not OK (400)")

    def test_parse_update_response_should_raise_str_message_when_code_non200_and_message_ascii(self):
        response_mock = MagicMock(
            status_code=400,
            headers={'Content-Type': 'application/json'},
            text=u'{"message": "Something went wrong"}')
        with self.assertRaises(ClientException) as context:
            self.client._parse_update_response(response_mock)
        self.assertEqual(
            context.exception.message,
            "Status code is not OK (400: Something went wrong)")

    def test_parse_update_response_should_raise_str_message_when_code_non200_and_message_nonascii(self):
        response_mock = MagicMock(
            status_code=400,
            headers={'Content-Type': 'application/json'},
            text=u'{"message": "Something went wroöòóng"}')
        with self.assertRaises(ClientException) as context:
            self.client._parse_update_response(response_mock)
        self.assertEqual(
            context.exception.message,
            u"Status code is not OK (400: Something went wroöòóng)".encode(
                'utf-8'))

    def test_parse_update_response_code_non200_with_json_list(self):
        response_mock = MagicMock(
            status_code=400,
            headers={'Content-Type': 'application/json'},
            text='["message", "Something went wrong"]')
        with self.assertRaises(ClientException) as context:
            self.client._parse_update_response(response_mock)
        self.assertEqual(
            context.exception.message,
            "Status code is not OK (400)")

    def test_parse_update_response_code_non200_with_json_wrong(self):
        response_mock = MagicMock(
            status_code=400,
            headers={'Content-Type': 'application/json'},
            text='')
        with self.assertRaises(ClientException) as context:
            self.client._parse_update_response(response_mock)
        self.assertEqual(
            context.exception.message,
            "Status code is not OK (400)")

    def test_update_indicator_should_raise_client_exception_when_url_is_none(self):
        client = Client(
            url_base=None)
        with self.assertRaises(ClientException):
            client.update_indicator(
                'service-id', 'indicator-id', 'indicator-description')

    def test_update_indicator_should_raise_client_exception_when_url_is_empty(self):
        client = Client(
            url_base='')
        with self.assertRaises(ClientException):
            client.update_indicator(
                'service-id', 'indicator-id', 'indicator-description')

    def test_update_indicator_should_raise_client_exception_when_url_is_invalid(self):
        client = Client(
            url_base='http://invalid')
        with self.assertRaises(ClientException):
            client.update_indicator(
                'service-id', 'indicator-id', 'indicator-description')

    def test_update_indicator_should_raise_client_exception_when_url_has_invalid_schema(self):
        client = Client(
            url_base='ttp://example.com')
        with self.assertRaises(ClientException):
            client.update_indicator(
                'service-id', 'indicator-id', 'indicator-description')
