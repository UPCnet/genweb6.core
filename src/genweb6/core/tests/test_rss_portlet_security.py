# -*- coding: utf-8 -*-
"""Portlet RSS de Genweb: no debe cargar urls peligrosas ni feeds sin limite."""
from genweb6.core.portlets.rss import rss
from unittest import mock
from zope.interface import Invalid

import unittest

FEED = b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
<title>Feed</title><link>https://example.org/</link>
<item><title>Bueno</title><link>https://example.org/a</link>
<description>texto</description></item>
<item><title>Malo</title><link>javascript:alert(1)</link>
<description>texto</description></item>
</channel></rss>"""

DOWNLOAD = 'genweb6.core.portlets.rss.rss._download_feed_and_response'


class FakeResponse(object):
    status_code = 200
    headers = {'Content-Type': 'application/rss+xml'}


class TestRSSPortletSecurity(unittest.TestCase):

    def _feed(self, url):
        return rss.RSSFeed(url, 100)

    def test_schema_validator_rejects_dangerous_urls(self):
        for url in ('file:///etc/passwd', 'javascript:alert(1)',
                    'http://localhost/feed', 'http://127.0.0.1/feed',
                    'ftp://example.org/feed', ' https://example.org/feed',
                    'https://example.org:8080/feed'):
            with self.assertRaises(Invalid, msg=url):
                rss._rss_feed_url_validator(url)

    def test_schema_validator_accepts_public_https(self):
        self.assertTrue(rss._rss_feed_url_validator('https://example.org/feed'))

    def test_dangerous_url_is_never_downloaded(self):
        feed = self._feed('file:///etc/passwd')
        with mock.patch(DOWNLOAD) as download:
            self.assertFalse(feed.update())
        download.assert_not_called()
        self.assertTrue(feed.update_failed)

    def test_download_error_marks_feed_failed(self):
        feed = self._feed('https://example.org/feed')
        with mock.patch(DOWNLOAD, side_effect=ValueError('Downloaded too much content.')):
            self.assertFalse(feed._retrieveFeed())
        self.assertTrue(feed.update_failed)
        self.assertEqual(feed.items, [])

    def test_valid_feed_and_javascript_links_are_neutralised(self):
        feed = self._feed('https://example.org/feed')
        with mock.patch(DOWNLOAD, return_value=(FEED, FakeResponse())) as download:
            self.assertTrue(feed._retrieveFeed())
        download.assert_called_once_with('https://example.org/feed')
        urls = [item['url'] for item in feed.items]
        self.assertEqual(urls, ['https://example.org/a', '#'])

    def test_feedparser_does_not_receive_the_url(self):
        feed = self._feed('https://example.org/feed')
        with mock.patch(DOWNLOAD, return_value=(FEED, FakeResponse())):
            with mock.patch.object(rss.feedparser, 'parse',
                                   wraps=rss.feedparser.parse) as parse:
                feed._retrieveFeed()
        self.assertNotIsInstance(parse.call_args[0][0], str)
