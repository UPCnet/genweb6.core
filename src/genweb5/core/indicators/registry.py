"""
Indicator registry that loads and stores indicators from a path containing yaml
files.
"""

from collections import defaultdict
from os import listdir
from os.path import isfile, join
import yaml
from yaml.scanner import ScannerError

from .model import Indicator


class RegistryException(Exception):
    pass


class Registry(object):
    def __init__(self, context):
        self._context = context
        self._indicators = defaultdict(dict)

    def load_from_path(self, path):
        try:
            file_paths = [
                join(path, file_name) for file_name in listdir(path)
                if isfile(join(path, file_name))]
        except OSError as e:
            raise RegistryException(e)
        for file_path in file_paths:
            try:
                self._load_from_file_path(file_path)
            except (TypeError, ValueError) as e:
                self._indicators = defaultdict(dict)
                raise RegistryException(
                    "File '{0}' contains malformed indicators ({1})".format(
                        file_path, e))
            except ScannerError as e:
                self._indicators = defaultdict(dict)
                raise RegistryException(
                    "File '{0}' is not a valid yaml file ({1})".format(
                        file_path, e))

    def _add_indicator_from_dict(self, indicator_dict):
        try:
            indicator = Indicator.instance_from_dict(
                indicator_dict, self._context)
            self._indicators[indicator.service][indicator.id] = indicator
        except (TypeError, ValueError) as e:
            raise e

    def _load_from_file_path(self, path):
        with open(path) as source_file:
            for document in yaml.load_all(source_file):
                self._add_indicator_from_dict(document)

    def __getitem__(self, item):
        return self._indicators[item]

    def __iter__(self):
        return (key for key in self._indicators)

    def values(self):
        return self._indicators.values()
