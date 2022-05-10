# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from zope.component.hooks import getSite

import importlib
import inspect

MODULES_TO_INSPECT = ['genweb6.core.browser.setup',
                      'genweb6.core.browser.helpers',
                      'genweb6.core.browser.helpers_touchers']


class clouseau(BrowserView):

    def get_helpers(self):
        absolute_url = getSite().absolute_url()
        result = {'setup': [],
                  'helpers': [],
                  'helpers_touchers': []}

        for module in MODULES_TO_INSPECT:
            themodule = importlib.import_module(module)
            members = inspect.getmembers(themodule, inspect.isclass)

            for name, klass in members:
                if 'genweb6.' in str(klass):
                    if module == 'genweb6.core.browser.setup':
                        result['setup'].append(dict(url='{}/{}'.format(absolute_url, name), description=klass.__doc__))
                    elif module == 'genweb6.core.browser.helpers':
                        result['helpers'].append(dict(url='{}/{}'.format(absolute_url, name), description=klass.__doc__))
                    elif module == 'genweb6.core.browser.helpers_touchers':
                        result['helpers_touchers'].append(dict(url='{}/{}'.format(absolute_url, name), description=klass.__doc__))

        return result
