# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.portlet.collection.collection import Renderer as CollectionRenderer


class gwCollection(CollectionRenderer):
    """ The standard collection portlet override 'old style'
        as it doesn't allow to do it jbot way...
    """
    _template = ViewPageTemplateFile('collection.pt')
    render = _template
