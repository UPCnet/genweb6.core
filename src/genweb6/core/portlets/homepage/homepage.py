# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implementer

from genweb6.core import GenwebMessageFactory as GWMF
from genweb6.core.interfaces import IHomePage
from genweb6.core.utils import pref_lang


class IHomepagePortlet(IPortletDataProvider):
    """A portlet which can render a login form.
    """


@implementer(IHomepagePortlet)
class Assignment(base.Assignment):

    title = GWMF(u'homepage_portlet', default=u'Homepage')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('homepage.pt')

    def getHomepage(self):
        page = {}
        pc = api.portal.get_tool('portal_catalog')
        result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                  portal_type='Document',
                                  Language=pref_lang())
        page['body'] = ''
        if result:
            try:
                page['body'] = result[0].output
            except:
                pass

        return page


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
