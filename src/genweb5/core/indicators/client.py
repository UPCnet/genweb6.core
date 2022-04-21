"""
Web client for the API specified on
https://indicadorstic.upc.edu/indicadorstic/
"""

import requests
import json
from requests.exceptions import (
    ConnectionError, ReadTimeout, MissingSchema, InvalidSchema)
from simplejson.decoder import JSONDecodeError
from datetime import datetime


class ClientException(Exception):
    pass


class Client(object):
    class Indicator(object):
        def __init__(self, identifier, description, date_modified):
            self.identifier = identifier
            self.description = description
            self.date_modified = date_modified

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

    class Category(object):
        def __init__(self, identifier, description, type, frequency,
                     value, date_modified):
            self.identifier = identifier
            self.description = description
            self.type = type
            self.frequency = frequency
            self.value = value
            self.date_modified = date_modified

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

    ENDPOINT_INDICATORS = "indicadors"
    ENDPOINT_CATEGORIES = "categories"
    KEY_INDICATOR_LIST = "indicadors"
    KEY_INDICATOR_IDENTIFIER = "idIndicador"
    KEY_INDICATOR_DESCRIPTION = "descripcioIndicador"
    KEY_INDICATOR_DATE_MODIFIED = "dataModificacioIndicador"
    KEY_CATEGORY_LIST = "categories"
    KEY_CATEGORY_IDENTIFIER = "idCategoria"
    KEY_CATEGORY_DESCRIPTION = "descripcioCategoria"
    KEY_CATEGORY_TYPE = "tipusIndicador"
    KEY_CATEGORY_FREQUENCY = "frequencia"
    KEY_CATEGORY_VALUE = "valor"
    KEY_CATEGORY_DATE_MODIFIED = "dataModificacioCategoria"

    def __init__(self, url_base,
                 api_key=None,
                 header_accept='application/json',
                 header_content_type='application/json',
                 timeout=25):
        self.url_base = url_base.rstrip('/') if url_base else url_base
        self.api_key = api_key
        self.header_accept = header_accept
        self.header_content_type = header_content_type
        self.timeout = timeout

    def _get_headers(self):
        headers = {
            'Accept': self.header_accept,
            'Content-type': self.header_content_type,
        }
        if self.api_key:
            headers['api_key'] = str(self.api_key)
        return headers

    def _parse_response_result(self, response):
        if 'status' in response and 'message' in response:
            raise ClientException("Error status {0}: {1}".format(
                response['status'], response['message']))

    def _parse_date_modified(self, date_modified_str):
        try:
            date_modified = datetime.strptime(
                date_modified_str[:19], '%Y-%m-%dT%H:%M:%S')
        except (TypeError, ValueError):
            date_modified = None
        return date_modified

    def _parse_response_list_indicators(self, response):
        self._parse_response_result(response)
        if Client.KEY_INDICATOR_LIST not in response:
            raise ClientException(
                "'{0}' is not present in the response".format(
                    Client.KEY_INDICATOR_LIST))
        if not isinstance(response[Client.KEY_INDICATOR_LIST], list):
            raise ClientException("Invalid type of '{0}'".format(
                Client.KEY_INDICATOR_LIST))
        indicators = []
        for indicator_dict in response[Client.KEY_INDICATOR_LIST]:
            if isinstance(indicator_dict, dict):
                indicators.append(Client.Indicator(
                    identifier=indicator_dict.get(
                        Client.KEY_INDICATOR_IDENTIFIER, u''),
                    description=indicator_dict.get(
                        Client.KEY_INDICATOR_DESCRIPTION, u''),
                    date_modified=self._parse_date_modified(
                        indicator_dict.get(
                            Client.KEY_INDICATOR_DATE_MODIFIED, None))))
        return indicators

    def _parse_response_list_categories(self, response):
        self._parse_response_result(response)
        if 'categories' not in response:
            raise ClientException(
                "'{0}' is not present in the response".format(
                    Client.KEY_CATEGORY_LIST))
        if not isinstance(response[Client.KEY_CATEGORY_LIST], list):
            raise ClientException("Invalid type of '{0}'".format(
                Client.KEY_CATEGORY_LIST))
        categories = []
        for category_dict in response[Client.KEY_CATEGORY_LIST]:
            if isinstance(category_dict, dict):
                categories.append(Client.Category(
                    identifier=category_dict.get(
                        Client.KEY_CATEGORY_IDENTIFIER, u''),
                    description=category_dict.get(
                        Client.KEY_CATEGORY_DESCRIPTION, u''),
                    type=category_dict.get(
                        Client.KEY_CATEGORY_TYPE, u''),
                    frequency=category_dict.get(
                        Client.KEY_CATEGORY_FREQUENCY, u''),
                    value=category_dict.get(
                        Client.KEY_CATEGORY_VALUE, u''),
                    date_modified=self._parse_date_modified(
                        category_dict.get(
                            Client.KEY_CATEGORY_DATE_MODIFIED, None))))
        return categories

    def list_indicators(self, service_id, count=None):
        """
        Return a list containing the <Indicator>s associated with the specified
        service.
        """
        try:
            if not service_id or not str(service_id).strip():
                raise ClientException("Parameter 'service_id' cannot be empty")
            response = requests.get(
                '{0}/{1}?idServei={2}'.format(
                    self.url_base, Client.ENDPOINT_INDICATORS, service_id),
                headers=self._get_headers(), verify=False, timeout=self.timeout)
            if response.status_code != requests.codes.ok:
                raise ClientException("Status code is not OK ({0})".format(
                    response.status_code))
            if response.text == u'':
                return []
            indicators = self._parse_response_list_indicators(response.json())
            return indicators[:count] if count is not None else indicators
        except ClientException:
            raise
        except (MissingSchema, InvalidSchema) as e:
            raise ClientException(e)
        except JSONDecodeError:
            raise ClientException("The response contains invalid JSON data")
        except ConnectionError:
            raise ClientException("The connection with '{0}' could not be "
                                  "established".format(self.url_base))
        except ReadTimeout:
            raise ClientException(
                "There was a timeout while waiting for server")

    def list_categories(self, service_id, indicator_id, count=None):
        """
        Return a list containing the <Client.Category>s associated with the
        specified indicator.
        """
        try:
            if not service_id or not str(service_id).strip():
                raise ClientException("Parameter 'service_id' cannot be empty")
            if not indicator_id or not str(indicator_id).strip():
                raise ClientException(
                    "Parameter 'indicator_id' cannot be empty")
            response = requests.get(
                '{0}/{1}?idServei={2}&idIndicador={3}'.format(
                    self.url_base, Client.ENDPOINT_CATEGORIES,
                    service_id, indicator_id),
                headers=self._get_headers(), verify=False, timeout=self.timeout)
            if response.status_code != requests.codes.ok:
                raise ClientException("Status code is not OK ({0})".format(
                    response.status_code))
            if response.text == u'':
                return []
            categories = self._parse_response_list_categories(response.json())
            return categories[:count] if count is not None else categories
        except ClientException:
            raise
        except (MissingSchema, InvalidSchema) as e:
            raise ClientException(e)
        except JSONDecodeError:
            raise ClientException("The response contains invalid JSON data")
        except ConnectionError:
            raise ClientException("The connection with '{0}' could not be "
                                  "established".format(self.url_base))
        except ReadTimeout:
            raise ClientException(
                "There was a timeout while waiting for server")

    def _validate_param_has_value(self, name, value):
        try:
            self._validate_param_is_not_none(name, value)
            self._validate_param_is_not_empty_string(name, value)
        except ClientException:
            raise ClientException(
                "Parameter '{0}' cannot be empty or None".format(name))

    def _validate_param_is_not_none(self, name, value):
        if value is None:
            raise ClientException(
                "Parameter '{0}' cannot be None".format(name))

    def _validate_param_is_not_empty_string(self, name, value):
        if value is not None and type(value) is str:
            if not value or not str(value).strip():
                raise ClientException(
                    "Parameter '{0}' cannot be empty string".format(name))

    def _parse_update_response(self, response):
        if response.status_code != requests.codes.ok:
            message = str(response.status_code)
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    response_data = json.loads(response.text)
                    if (type(response_data) is dict and
                            'message' in response_data and
                            response_data['message']):
                        message += ': ' + response_data['message'].encode(
                            'utf-8')
                except ValueError:
                    message = str(response.status_code)

            raise ClientException(
                "Status code is not OK ({0})".format(message))
        else:
            return True

    def _validate_update_indicator_parameters(
            self, service_id, indicator_id, indicator_description):
        self._validate_param_has_value('service_id', service_id)
        self._validate_param_has_value('indicator_id', indicator_id)
        self._validate_param_is_not_none('indicator_description',
                                         indicator_description)

    def _build_update_indicator_url(self, service_id):
        return '{0}/{1}?idServei={2}'.format(
            self.url_base, Client.ENDPOINT_INDICATORS, service_id)

    def update_indicator(self, service_id, indicator_id,
                         indicator_description):
        try:
            self._validate_update_indicator_parameters(
                service_id, indicator_id, indicator_description)

            data = {
                Client.KEY_INDICATOR_IDENTIFIER: indicator_id,
                Client.KEY_INDICATOR_DESCRIPTION: indicator_description}

            return self._parse_update_response(
                requests.put(
                    self._build_update_indicator_url(service_id),
                    headers=self._get_headers(),
                    data=json.dumps(data),
                    verify=False,
                    timeout=self.timeout))
        except ClientException:
            raise
        except (MissingSchema, InvalidSchema) as e:
            raise ClientException(e)
        except ConnectionError:
            raise ClientException("The connection with '{0}' could not be "
                                  "established".format(self.url_base))
        except ReadTimeout:
            raise ClientException(
                "There was a timeout while waiting for server")

    def _validate_update_category_parameters(
            self, service_id, indicator_id,
            category_id, category_description, category_type,
            category_frequency, category_value):
        self._validate_param_has_value('service_id', service_id)
        self._validate_param_has_value('indicator_id', indicator_id)
        self._validate_param_has_value('category_id', category_id)
        self._validate_param_is_not_none('category_description',
                                         category_description)
        self._validate_param_is_not_none('category_value', category_value)

    def _build_update_category_url(self, service_id, indicator_id):
        return '{0}/{1}?idServei={2}&idIndicador={3}'.format(
            self.url_base, Client.ENDPOINT_CATEGORIES,
            service_id, indicator_id)

    def update_category(self, service_id, indicator_id,
                        category_id, category_description, category_type,
                        category_frequency, category_value):
        try:
            self._validate_update_category_parameters(
                service_id, indicator_id,
                category_id, category_description, category_type,
                category_frequency, category_value)

            data = {
                Client.KEY_CATEGORY_IDENTIFIER: category_id,
                Client.KEY_CATEGORY_DESCRIPTION: category_description,
                Client.KEY_CATEGORY_TYPE: category_type,
                Client.KEY_CATEGORY_FREQUENCY: category_frequency,
                Client.KEY_CATEGORY_VALUE: category_value}

            return self._parse_update_response(
                requests.put(
                    self._build_update_category_url(service_id, indicator_id),
                    headers=self._get_headers(),
                    data=json.dumps(data),
                    verify=False,
                    timeout=self.timeout))
        except ClientException:
            raise
        except (MissingSchema, InvalidSchema) as e:
            raise ClientException(e)
        except ConnectionError:
            raise ClientException("The connection with '{0}' could not be "
                                  "established".format(self.url_base))
        except ReadTimeout:
            raise ClientException(
                "There was a timeout while waiting for server")
