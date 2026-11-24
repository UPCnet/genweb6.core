# -*- coding: utf-8 -*-
"""Portlets RSS (Plone y genweb): descarga con 5 s, redirecciones validadas y,
si falla una actualización, se siguen mostrando los últimos elementos."""
from genweb6.core.portlets.rss import download
from genweb6.core.portlets.rss import rss
from unittest import mock
from zope.interface import Invalid

import requests
import unittest

FEED = b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
<title>Feed</title><link>https://example.org/</link>
<item><title>Avis</title><link>https://example.org/a</link>
<description>texto</description></item>
</channel></rss>"""

DOWNLOAD = 'genweb6.core.portlets.rss.rss.download_feed_and_response'
GET = 'genweb6.core.portlets.rss.download.requests.get'


class FakeResponse(object):

    def __init__(self, status=200, body=b'', headers=None):
        self.status_code = status
        self.headers = headers or {'Content-Type': 'application/rss+xml'}
        self._body = body
        self.closed = False

    @property
    def is_redirect(self):
        return self.status_code in (301, 302, 303, 307, 308) and \
            'Location' in self.headers

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))

    def iter_content(self, size):
        for i in range(0, len(self._body), size):
            yield self._body[i:i + size]

    def close(self):
        self.closed = True


class TestDownload(unittest.TestCase):

    def test_timeout_5_seconds_and_no_automatic_redirects(self):
        with mock.patch(GET, return_value=FakeResponse(body=FEED)) as get:
            contents, response = download.download_feed_and_response(
                'https://example.org/feed')
        self.assertEqual(contents, FEED)
        kwargs = get.call_args.kwargs
        self.assertEqual(kwargs['timeout'], 5)
        self.assertFalse(kwargs['allow_redirects'])

    def test_follows_validated_redirect_http_to_https(self):
        responses = [
            FakeResponse(302, headers={
                'Location': 'https://example.org/feed'}),
            FakeResponse(body=FEED),
        ]
        with mock.patch(GET, side_effect=responses) as get:
            contents, _ = download.download_feed_and_response(
                'http://example.org/feed')
        self.assertEqual(contents, FEED)
        self.assertEqual(get.call_args_list[1].args[0],
                         'https://example.org/feed')
        self.assertTrue(responses[0].closed)

    def test_relative_redirect(self):
        responses = [
            FakeResponse(301, headers={'Location': '/rss.xml'}),
            FakeResponse(body=FEED),
        ]
        with mock.patch(GET, side_effect=responses) as get:
            download.download_feed_and_response('https://example.org/feed')
        self.assertEqual(get.call_args_list[1].args[0],
                         'https://example.org/rss.xml')

    def test_redirect_to_forbidden_url_is_refused(self):
        for location in ('http://localhost/feed', 'file:///etc/passwd',
                         'http://127.0.0.1/feed'):
            response = FakeResponse(302, headers={'Location': location})
            with mock.patch(GET, return_value=response) as get:
                with self.assertRaises(Invalid, msg=location):
                    download.download_feed_and_response(
                        'https://example.org/feed')
            self.assertEqual(get.call_count, 1)

    def test_too_many_redirects(self):
        loop = FakeResponse(302, headers={'Location': 'https://example.org/x'})
        with mock.patch(GET, return_value=loop) as get:
            with self.assertRaises(ValueError):
                download.download_feed_and_response('https://example.org/x')
        self.assertEqual(get.call_count, download.MAX_REDIRECTS + 1)

    def test_size_limit(self):
        big = FakeResponse(body=b'x' * 200)
        with mock.patch(GET, return_value=big):
            with self.assertRaises(ValueError):
                download.download_feed_and_response(
                    'https://example.org/feed', limit=100)
        declared = FakeResponse(body=b'', headers={'Content-Length': '200'})
        with mock.patch(GET, return_value=declared):
            with self.assertRaises(ValueError):
                download.download_feed_and_response(
                    'https://example.org/feed', limit=100)

    def test_not_modified_and_http_errors(self):
        with mock.patch(GET, return_value=FakeResponse(304)):
            contents, response = download.download_feed_and_response(
                'https://example.org/feed', headers={'If-None-Match': 'x'})
        self.assertEqual((contents, response.status_code), (b'', 304))
        with mock.patch(GET, return_value=FakeResponse(500)):
            with self.assertRaises(requests.HTTPError):
                download.download_feed_and_response('https://example.org/feed')


class TestKeepLastItems(unittest.TestCase):

    def setUp(self):
        rss.FEED_DATA.clear()

    def _renderer(self, feed):
        renderer = rss.Renderer.__new__(rss.Renderer)
        renderer._getFeed = lambda: feed
        return renderer

    def test_failed_update_keeps_items_and_portlet_visible(self):
        feed = rss.RSSFeed('https://example.org/feed', 100)
        with mock.patch(DOWNLOAD, return_value=(FEED, FakeResponse())):
            self.assertTrue(feed._retrieveFeed())
        self.assertTrue(self._renderer(feed).enabled)

        with mock.patch(DOWNLOAD, side_effect=requests.ReadTimeout('lent')):
            self.assertFalse(feed._retrieveFeed())
        self.assertTrue(feed.update_failed)
        self.assertEqual([i['title'] for i in feed.items], ['Avis'])
        self.assertTrue(self._renderer(feed).enabled)

    def test_malformed_feed_keeps_items_and_logs(self):
        feed = rss.RSSFeed('https://example.org/feed', 100)
        with mock.patch(DOWNLOAD, return_value=(FEED, FakeResponse())):
            feed._retrieveFeed()
        with mock.patch(DOWNLOAD, return_value=(b'<rss><channel><item>',
                                                 FakeResponse())):
            with self.assertLogs(rss.logger, 'WARNING') as logs:
                self.assertFalse(feed._retrieveFeed())
        self.assertIn('malformed', logs.output[0])
        self.assertEqual(len(feed.items), 1)
        self.assertTrue(self._renderer(feed).enabled)

    def test_never_loaded_feed_stays_hidden(self):
        feed = rss.RSSFeed('https://example.org/feed', 100)
        with mock.patch(DOWNLOAD, side_effect=requests.ConnectTimeout('x')):
            feed._retrieveFeed()
        self.assertFalse(self._renderer(feed).enabled)

    def test_plone_renderer_patch(self):
        """La propiedad que sustituye Renderer.enabled del RSS de Plone."""
        class FakeFeed(object):
            ok = False
            items = [{'title': 'Avis'}]

        class FakeRenderer(object):
            enabled = download.renderer_enabled

            def _getFeed(self):
                return FakeFeed()

        self.assertTrue(FakeRenderer().enabled)
        FakeFeed.items = []
        self.assertFalse(FakeRenderer().enabled)
