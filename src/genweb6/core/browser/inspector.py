# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView

from zope.component.hooks import getSite

import importlib
import inspect

MODULES_TO_INSPECT = ['genweb6.core.browser.setup',
                      'genweb6.core.browser.helpers',
                      'genweb6.core.browser.helpers_touchers']


class clouseau(BrowserView):

    def get_helpers(self):
        portal = getSite()
        app = portal.restrictedTraverse('/')

        setup = []

        bulk = []
        products = []
        cache = []

        application = []
        plone = []

        for module in MODULES_TO_INSPECT:
            themodule = importlib.import_module(module)
            members = inspect.getmembers(themodule, inspect.isclass)
            # import ipdb; ipdb.set_trace()
            pass

            for name, klass in members:
                if name != 'BrowserView':
                    if module == 'genweb6.core.browser.setup':
                        setup.append(
                            dict(url='{}/{}'.format(portal.absolute_url(), name), description=klass.__doc__))
                    elif 'bulk' in name.lower():
                        pass
                    elif 'product' in name.lower():
                        pass
                    elif 'cache' in name.lower():
                        pass

            #     if grok.View in klass.__bases__:
            #         if getattr(klass, 'grokcore.component.directive.context').getName() == 'IApplication':
            #             application.append(dict(url='{}/{}'.format(app.absolute_url(), getattr(klass, 'grokcore.component.directive.name', name.lower())), description=klass.__doc__))
            #         else:
            #             plone_site.append(dict(url='{}/{}'.format(portal.absolute_url(), getattr(klass, 'grokcore.component.directive.name', name.lower())), description=klass.__doc__))

        return (plone, application)
