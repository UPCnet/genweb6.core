# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets.recent import Renderer as RecentRenderer


class gwRecent(RecentRenderer):
    _template = ViewPageTemplateFile('recent.pt')

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())
