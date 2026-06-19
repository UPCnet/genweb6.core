# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from zExceptions import NotFound

from genweb6.core.analytics import ga4
from genweb6.core.browser.syndication.views import TrackedFeedView
from Products.CMFPlone.browser.syndication.views import FeedView


class DummyRequest(dict):
    pass


class DummyContext(object):

    def Title(self):
        return 'Test Feed'

    def absolute_url_path(self):
        return '/ca/noticies'


class TestGA4Payload(unittest.TestCase):

    def test_build_client_id_is_stable(self):
        request = DummyRequest({
            'REMOTE_ADDR': '203.0.113.1',
            'HTTP_USER_AGENT': 'Feedly/1.0',
        })
        first = ga4.build_client_id(request)
        second = ga4.build_client_id(request)
        self.assertEqual(first, second)
        self.assertEqual(32, len(first))

    def test_build_client_id_differs_by_user_agent(self):
        base = {'REMOTE_ADDR': '203.0.113.1'}
        request_a = DummyRequest(dict(base, HTTP_USER_AGENT='Feedly/1.0'))
        request_b = DummyRequest(dict(base, HTTP_USER_AGENT='Thunderbird/102.0'))
        self.assertNotEqual(
            ga4.build_client_id(request_a),
            ga4.build_client_id(request_b),
        )

    def test_build_payload_fields(self):
        request = DummyRequest({
            'REMOTE_ADDR': '203.0.113.1',
            'HTTP_USER_AGENT': 'Feedly/1.0',
            'ACTUAL_URL': 'https://example.edu/ca/noticies/rss.xml',
        })
        context = DummyContext()
        payload = ga4.build_payload(context, request, 'rss.xml')

        self.assertIn('client_id', payload)
        self.assertEqual(1, len(payload['events']))
        event = payload['events'][0]
        self.assertEqual('rss_view', event['name'])
        self.assertEqual(
            'https://example.edu/ca/noticies/rss.xml',
            event['params']['page_location'],
        )
        self.assertEqual('Test Feed', event['params']['feed_title'])
        self.assertEqual('rss_xml', event['params']['feed_format'])
        self.assertEqual('/ca/noticies', event['params']['content_path'])

    def test_build_payload_rdf_format(self):
        request = DummyRequest({
            'REMOTE_ADDR': '203.0.113.1',
            'HTTP_USER_AGENT': 'Feedly/1.0',
            'ACTUAL_URL': 'https://example.edu/ca/noticies/RSS',
        })
        payload = ga4.build_payload(DummyContext(), request, 'RSS')
        self.assertEqual('rdf_xml', payload['events'][0]['params']['feed_format'])


class TestTrackRssView(unittest.TestCase):

    @patch('genweb6.core.analytics.ga4.threading.Thread')
    @patch('genweb6.core.analytics.ga4.get_analytics_config')
    def test_track_skipped_when_disabled(self, mock_config, mock_thread):
        mock_config.return_value = None
        request = DummyRequest({'REMOTE_ADDR': '1.1.1.1', 'HTTP_USER_AGENT': 'test'})
        ga4.track_rss_view(DummyContext(), request, 'rss.xml')
        mock_thread.assert_not_called()

    @patch('genweb6.core.analytics.ga4.threading.Thread')
    @patch('genweb6.core.analytics.ga4.get_analytics_config')
    def test_track_starts_background_thread(self, mock_config, mock_thread):
        mock_config.return_value = ('G-TEST123', 'secret-value')
        request = DummyRequest({
            'REMOTE_ADDR': '1.1.1.1',
            'HTTP_USER_AGENT': 'test',
            'ACTUAL_URL': 'https://example.edu/rss.xml',
        })
        ga4.track_rss_view(DummyContext(), request, 'rss.xml')
        mock_thread.assert_called_once()
        kwargs = mock_thread.call_args[1]
        self.assertTrue(kwargs['daemon'])


class TestSendEvent(unittest.TestCase):

    @patch('genweb6.core.analytics.ga4.requests.post')
    def test_send_event_posts_to_ga4(self, mock_post):
        payload = {'client_id': 'abc', 'events': [{'name': 'rss_view'}]}
        ga4._send_event('G-TEST123', 'secret-value', payload)
        mock_post.assert_called_once()
        url = mock_post.call_args[0][0]
        self.assertIn('measurement_id=G-TEST123', url)
        self.assertIn('api_secret=secret-value', url)
        self.assertEqual(payload, mock_post.call_args[1]['json'])

    @patch('genweb6.core.analytics.ga4.logger')
    @patch('genweb6.core.analytics.ga4.requests.post', side_effect=Exception('network'))
    def test_send_event_logs_warning_on_failure(self, mock_post, mock_logger):
        ga4._send_event('G-TEST123', 'secret-value', {})
        mock_logger.warning.assert_called_once()


class TestGetMeasurementId(unittest.TestCase):

    @patch('genweb6.core.analytics.ga4.queryUtility')
    def test_uses_explicit_measurement_id(self, mock_query):
        settings = MagicMock()
        settings.measurement_id = 'G-EXPLICIT'
        self.assertEqual('G-EXPLICIT', ga4.get_measurement_id(settings))
        mock_query.assert_not_called()

    @patch('genweb6.core.analytics.ga4.queryUtility')
    def test_falls_back_to_webstats_js(self, mock_query):
        settings = MagicMock()
        settings.measurement_id = ''
        site_settings = MagicMock()
        site_settings.webstats_js = "gtag('config', 'G-FROMJS');"
        registry = MagicMock()
        registry.forInterface.return_value = site_settings
        mock_query.return_value = registry
        self.assertEqual('G-FROMJS', ga4.get_measurement_id(settings))


class TestTrackedFeedView(unittest.TestCase):

    @patch('genweb6.core.browser.syndication.views.track_rss_view')
    @patch.object(FeedView, '__call__', return_value='<rss/>')
    def test_tracking_on_successful_feed(self, mock_super, mock_track):
        view = TrackedFeedView(MagicMock(), DummyRequest())
        view.__name__ = 'rss.xml'
        result = view()
        self.assertEqual('<rss/>', result)
        mock_track.assert_called_once_with(view.context, view.request, 'rss.xml')

    @patch('genweb6.core.browser.syndication.views.track_rss_view')
    @patch.object(FeedView, '__call__', return_value=None)
    def test_no_tracking_when_feed_not_served(self, mock_super, mock_track):
        view = TrackedFeedView(MagicMock(), DummyRequest())
        view.__name__ = 'RSS'
        self.assertIsNone(view())
        mock_track.assert_not_called()

    @patch('genweb6.core.browser.syndication.views.track_rss_view')
    @patch.object(FeedView, '__call__', side_effect=NotFound())
    def test_no_tracking_on_not_found(self, mock_super, mock_track):
        view = TrackedFeedView(MagicMock(), DummyRequest())
        view.__name__ = 'rss.xml'
        with self.assertRaises(NotFound):
            view()
        mock_track.assert_not_called()


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestGA4Payload)


if __name__ == '__main__':
    unittest.main()
