"""
Reports indicators to the Indicators Web Service.
"""

from .model import Indicator, Category, CalculatorException
from .registry import Registry
from .client import Client, ClientException


class ReporterException(Exception):
    pass


class WebServiceReporter(object):
    def __init__(self, ws_url, ws_key):
        self._client = Client(ws_url, ws_key)

    def report(self, data):
        if type(data) is Registry:
            self._report_registry(data)
        elif type(data) is dict:
            self._report_indicator_dict(data)
        elif type(data) is Indicator:
            self._report_indicator(data)
        elif type(data) is Category:
            self._report_category(data)
        else:
            raise TypeError(
                "Supported types are: Registry, dict, Indicator and Category")

    def _report_category(self, category):
        try:
            self._client.update_category(
                category.indicator.service, category.indicator.id,
                category.id, category.description, category.type,
                category.frequency, category.value)
        except CalculatorException as e:
            raise ReporterException(
                "Error when calculating category ({0})".format(e.message))
        except ClientException as e:
            raise ReporterException(
                "WS client exception ({0})".format(e.message))

    def _report_indicator_categories(self, indicator):
        for category in indicator.categories.values():
            self._report_category(category)

    def _report_indicator(self, indicator, report_categories=True):
        try:
            self._client.update_indicator(
                indicator.service,
                indicator.id,
                indicator.description)
            if report_categories:
                self._report_indicator_categories(indicator)
        except ClientException as e:
            raise ReporterException(
                "WS client exception ({0})".format(e.message))
        except ReporterException:
            raise

    def _report_indicator_dict(self, indicator_dict):
        for indicator in indicator_dict.values():
            self._report_indicator(indicator)

    def _report_registry(self, registry):
        for indicator_dict in registry.values():
            self._report_indicator_dict(indicator_dict)
