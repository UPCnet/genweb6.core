# -*- coding: utf-8 -*-
from Products.CMFPlone.browser.syndication.views import FeedView

from genweb6.core.analytics.ga4 import track_rss_view


class TrackedFeedView(FeedView):
    """FeedView that reports RSS access to GA4 via Measurement Protocol."""

    def __call__(self):
        view_name = self.__name__
        result = super(TrackedFeedView, self).__call__()
        if result is not None:
            track_rss_view(self.context, self.request, view_name)
        return result
