# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.app.portlets.portlets.rss import Renderer as RssRenderer


class gwRSS(RssRenderer):
    """ The standard rss portlet override 'old style'
        as it doesn't allow to do it jbot way...
    """
    render_full = ZopeTwoPageTemplateFile('rss.pt')
