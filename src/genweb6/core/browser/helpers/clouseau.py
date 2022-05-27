# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from zope.component.hooks import getSite

import importlib
import inspect

MODULES_TO_INSPECT = ['genweb6.core.browser.helpers.helpers_ldap',
                      'genweb6.core.browser.helpers.helpers',
                      'genweb6.core.browser.helpers.helpers_application',
                      'genweb6.core.browser.helpers.helpers_touchers']


class clouseau(BrowserView):

    def get_helpers(self):
        absolute_url = getSite().absolute_url()
        portal_url = getSite().restrictedTraverse('/').absolute_url()

        result = {'helpers_ldap': [],
                  'helpers': [],
                  'helpers_application': [],
                  'helpers_touchers': []}

        for module in MODULES_TO_INSPECT:
            themodule = importlib.import_module(module)
            members = inspect.getmembers(themodule, inspect.isclass)

            for name, klass in members:
                if 'genweb6.' in str(klass):
                    if module == 'genweb6.core.browser.helpers.helpers_ldap':
                        result['helpers_ldap'].append(dict(url='{}/{}'.format(absolute_url, name), description=klass.__doc__))
                    elif module == 'genweb6.core.browser.helpers.helpers':
                        result['helpers'].append(dict(url='{}/{}'.format(absolute_url, name), description=klass.__doc__))
                    elif module == 'genweb6.core.browser.helpers.helpers_application':
                        result['helpers_application'].append(dict(url='{}/{}'.format(portal_url, name), description=klass.__doc__))
                    elif module == 'genweb6.core.browser.helpers.helpers_touchers':
                        result['helpers_touchers'].append(dict(url='{}/{}'.format(absolute_url, name), description=klass.__doc__))

        return result
