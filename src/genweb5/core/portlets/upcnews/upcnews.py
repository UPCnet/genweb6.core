# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implementer

from genweb5.core import utils

import feedparser


class IUPCNewsPortlet(IPortletDataProvider):
    """A portlet which can render a list of news from UPC.
    """


@implementer(IUPCNewsPortlet)
class Assignment (base.Assignment):

    @property
    def title(self):
        return _(u"UPCNews")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('upcnews.pt')

    def mes(self, mes):
        return self.utils.mes(mes)

    def dia_semana(self, dia):
        return self.utils.dia_semana(dia)

    def getUrlRSSPremsa(self):
        url = ''
        idioma = utils.pref_lang()

        if idioma == 'en':
            url = 'https://upc.edu/en/press-room/upc-today/RSS'

        elif idioma == 'ca':
            url = 'https://upc.edu/ca/sala-de-premsa/actualitat-upc/RSS'

        elif idioma == 'es':
            url = 'https://upc.edu/es/sala-de-prensa/actualidad-upc/RSS'
        else:
            url = 'https://upc.edu/ca/sala-de-premsa/actualitat-upc/RSS'

        return url

    def getURLPremsa(self):
        url = ''
        idioma = utils.pref_lang()
        if idioma == 'en':
            url = 'https://upc.edu/en/press-room'

        elif idioma == 'ca':
            url = 'https://upc.edu/ca/sala-de-premsa'

        elif idioma == 'es':
            url = 'https://upc.edu/es/sala-de-prensa'

        else:
            url = 'https://upc.edu/ca/sala-de-premsa'

        return url

    def getRSS(self):

        url = self.getUrlRSSPremsa()
        items = []

        d = feedparser.parse(url)
        for item in d['items']:
            try:
                itemdict = {
                    'title': item.title,
                    'url': item.link,
                    'summary': item.get('description', ''),
                }
            except AttributeError:
                continue
            items.append(itemdict)
        return items[:6]


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
