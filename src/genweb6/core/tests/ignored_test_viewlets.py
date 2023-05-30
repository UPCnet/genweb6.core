# # -*- coding: utf-8 -*-
# from genweb6.core.testing import GENWEB_INTEGRATION_TESTING
# from genweb.theme.browser.viewlets import gwCSSViewlet
# from genweb.js.browser.viewlets import gwJSViewlet

# import json
# import pkg_resources
# import unittest2 as unittest


# class TestExample(unittest.TestCase):

#     layer = GENWEB_INTEGRATION_TESTING

#     def setUp(self):
#         self.app = self.layer['app']
#         self.portal = self.layer['portal']
#         self.request = self.layer['request']

#         genwebthemeegg = pkg_resources.get_distribution('genweb.theme')
#         genwebjsegg = pkg_resources.get_distribution('genweb.js')
#         resource_file_css = open('{}/genweb/theme/config.json'.format(genwebthemeegg.location))
#         resource_file_js = open('{}/genweb/js/config.json'.format(genwebjsegg.location))
#         self.resources_conf_css = json.loads(resource_file_css.read())
#         self.resources_conf_js = json.loads(resource_file_js.read())

#     def test_css_development_resource_viewlet(self):

#         viewlet = gwCSSViewlet(self.portal, self.request, None, None)
#         viewlet.update()
#         resources = viewlet.get_development_resources()

#         for resource in resources:
#             self.assertTrue('++' in resource)

#     def test_css_production_resource_viewlet(self):
#         viewlet = gwCSSViewlet(self.portal, self.request, None, None)
#         viewlet.update()
#         resources = viewlet.get_production_resources()

#         for resource in resources:
#             self.assertTrue('++' in resource)

#         self.assertTrue(len(resources) == len(self.resources_conf_css['order']))

#     def test_js_development_resource_viewlet(self):

#         viewlet = gwJSViewlet(self.portal, self.request, None, None)
#         viewlet.update()
#         resources = viewlet.get_development_resources()

#         for resource in resources:
#             self.assertTrue('++' in resource)

#     def test_js_production_resource_viewlet(self):
#         viewlet = gwJSViewlet(self.portal, self.request, None, None)
#         viewlet.update()
#         resources = viewlet.get_production_resources()

#         for resource in resources:
#             self.assertTrue('++' in resource)

#         self.assertTrue(len(resources) == len(self.resources_conf_js['order']))
