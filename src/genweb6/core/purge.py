# -*- coding: utf-8 -*-
from plone.cachepurging.interfaces import ICachePurgingSettings
from plone.cachepurging.interfaces import IPurgePathRewriter
from plone.cachepurging.interfaces import IPurger
from plone.cachepurging.utils import getURLsToPurge
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.globalrequest import getRequest

import logging

logger = logging.getLogger(__name__)


def purge_varnish_paths(self, paths):
    """ Purga todos los paths Ej: '/@@gw-hero' en el varnish"""

    purger = getUtility(IPurger)
    registry = getUtility(IRegistry)
    purgingSettings = registry.forInterface(ICachePurgingSettings)
    proxies = purgingSettings.cachingProxies
    if proxies:

        def purge(url):
            status, xcache, xerror = purger.purgeSync(url)
            log = url
            if xcache:
                log += " (X-Cache header: " + xcache + ")"
            if xerror:
                log += " -- " + xerror
            if not str(status).startswith("2"):
                log += " -- WARNING status " + str(status)

        relativePaths = [x.decode("utf8") if isinstance(x, bytes) else x for x in paths]
        try:
            rewriter = IPurgePathRewriter(self.request, None)
        except:
            request = getattr(self, 'REQUEST', None)
            rewriter = IPurgePathRewriter(request, None)

        for relativePath in relativePaths:
            rewrittenPaths = rewriter(relativePath) or []
            for rewrittenPath in rewrittenPaths:
                for newURL in getURLsToPurge(rewrittenPath, proxies):
                    purge(newURL)
