# -*- coding: utf-8 -*-
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.uuid.utils import uuidToURL
from plone.outputfilters.browser.resolveuid import ResolveUIDView
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component.hooks import getSite


class GenwebResolveUIDView(ResolveUIDView):
    """Resolve resolveuid links; show Plone 404 page if content does not exist."""

    def _show_not_found_page(self):
        """Render Plone standard 404 page (NotFound exception view)."""
        portal = getSite()
        root = getNavigationRootObject(self.context, portal)
        exc = NotFound()
        view = getMultiAdapter((exc, self.request), name="index.html")
        view.__parent__ = root
        return view()

    def __call__(self):
        url = uuidToURL(self.uuid)

        if not url:
            return self._show_not_found_page()

        if self.subpath:
            url = "/".join([url] + self.subpath)

        if self.request.QUERY_STRING:
            url += "?" + self.request.QUERY_STRING

        self.request.response.redirect(url, status=301)
        return ""
