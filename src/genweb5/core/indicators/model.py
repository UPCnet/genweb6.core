"""
Classes that model indicator data structures.
"""

import importlib


class Indicator(object):
    def __init__(self, service, id, description):
        self.service = service
        self.id = id
        self.description = description
        self._categories = {}

    def add_category(self, category):
        self._categories[category.id] = category

    def __getitem__(self, item):
        return self._categories[item]

    @property
    def categories(self):
        return self._categories

    @staticmethod
    def _validate_indicator_dict(indicator):
        if type(indicator) is not dict:
            raise TypeError("No dictionary found")
        if 'service' not in indicator:
            raise ValueError("No 'service' found in the dictionary")
        if 'id' not in indicator:
            raise ValueError("No 'id' found in the dictionary")
        if 'description' not in indicator:
            raise ValueError("No 'description' found in the dictionary")
        if 'categories' not in indicator:
            raise ValueError("No 'categories' found in the dictionary")

        if type(indicator['service']) not in (str, unicode):
            raise ValueError("'service' must be a string")
        if type(indicator['id']) not in (str, unicode):
            raise ValueError("'id' must be a string")
        if type(indicator['description']) not in (str, unicode):
            raise ValueError("'description' must be a string")
        if type(indicator['categories']) is not list:
            raise ValueError("'categories' must be a list")

        if not indicator['service']:
            raise ValueError("'service' cannot be empty")
        if not indicator['id']:
            raise ValueError("'id' cannot be empty")

    @staticmethod
    def instance_from_dict(indicator, context):
        Indicator._validate_indicator_dict(indicator)
        instance = Indicator(
            indicator['service'], indicator['id'], indicator['description'])
        for category_dict in indicator['categories']:
            category = Category.instance_from_dict(category_dict, context)
            category.indicator = instance
            instance.add_category(category)
        return instance


class Category(object):
    def __init__(self, id, description, type, frequency, calculator,
                 indicator=None):
        self.indicator = indicator
        self.id = id
        self.description = description
        self.type = type
        self.frequency = frequency
        self.calculator = calculator

    @property
    def value(self):
        return self.calculator.calculate()

    @staticmethod
    def _validate_category_dict(category):
        if type(category) is not dict:
            raise TypeError("No dictionary found")
        if 'id' not in category:
            raise ValueError("No 'id' found in the dictionary")
        if 'description' not in category:
            raise ValueError("No 'description' found in the dictionary")
        if 'calculator' not in category:
            raise ValueError("No 'calculator' found in the dictionary")

        if type(category['id']) not in (str, unicode):
            raise ValueError("'id' must be a string")
        if type(category['description']) not in (str, unicode):
            raise ValueError("'description' must be a string")
        if type(category['calculator']) not in (str, unicode):
            raise ValueError("'calculator' must be a string")

        if not category['id']:
            raise ValueError("'id' cannot be empty")
        if not category['calculator']:
            raise ValueError("'calculator' cannot be empty")

    @staticmethod
    def instance_from_dict(category, context):
        Category._validate_category_dict(category)
        calculator = Calculator.instance_from_string(
            category['calculator'], context)
        type = category['type'] if 'type' in category else None
        frequency = category['frequency'] if 'frequency' in category else None
        instance = Category(
            id=category['id'],
            description=category['description'],
            type=type,
            frequency=frequency,
            calculator=calculator
        )
        calculator.category = instance
        return instance


class CalculatorException(Exception):
    pass


class Calculator(object):
    def __init__(self, context, category=None):
        self.category = category
        self.context = context

    def calculate(self):
        raise NotImplementedError

    @staticmethod
    def instance_from_string(string, context):
        string_module = '.'.join(string.split('.')[:-1])
        string_class = string.split('.')[-1]
        try:
            module = importlib.import_module(string_module)
            calculator_class = getattr(module, string_class)
        except (ImportError, ValueError, AttributeError) as e:
            raise ValueError(
                "Class '{0}' could not be instantiated ({1})".format(
                    string, e.message))
        return calculator_class(context)
