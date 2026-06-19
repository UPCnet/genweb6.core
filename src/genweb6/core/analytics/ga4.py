# -*- coding: utf-8 -*-
"""GA4 Measurement Protocol client for RSS feed views."""

from plone.base.interfaces import ISiteSchema
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

import hashlib
import logging
import re
import threading

import requests

from genweb6.core.controlpanels.analytics import IGA4RSSAnalyticsSettings


logger = logging.getLogger(__name__)

GA4_MP_URL = 'https://www.google-analytics.com/mp/collect'
MEASUREMENT_ID_RE = re.compile(r'G-[A-Z0-9]+')
REQUEST_TIMEOUT = 3

FEED_FORMATS = {
    'rss.xml': 'rss_xml',
    'RSS': 'rdf_xml',
}


def build_client_id(request):
    ip = request.get('REMOTE_ADDR', '') or ''
    user_agent = request.get('HTTP_USER_AGENT', '') or ''
    raw = '{0}|{1}'.format(ip, user_agent).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()[:32]


def get_measurement_id(settings):
    measurement_id = (settings.measurement_id or '').strip()
    if measurement_id:
        return measurement_id

    registry = queryUtility(IRegistry)
    if registry is None:
        return None

    site_settings = registry.forInterface(ISiteSchema, prefix='plone', check=False)
    webstats_js = getattr(site_settings, 'webstats_js', '') or ''
    match = MEASUREMENT_ID_RE.search(webstats_js)
    return match.group(0) if match else None


def get_analytics_config():
    registry = queryUtility(IRegistry)
    if registry is None:
        return None

    settings = registry.forInterface(IGA4RSSAnalyticsSettings, check=False)
    if not settings.enabled:
        return None

    measurement_id = get_measurement_id(settings)
    api_secret = (settings.api_secret or '').strip()
    if not measurement_id or not api_secret:
        return None

    return measurement_id, api_secret


def get_feed_title(context):
    try:
        title = context.Title()
    except (AttributeError, TypeError):
        return ''
    return title or ''


def get_content_path(context):
    try:
        return context.absolute_url_path()
    except AttributeError:
        return ''


def build_payload(context, request, view_name):
    feed_format = FEED_FORMATS.get(view_name, view_name)
    page_location = request.get('ACTUAL_URL', '') or request.get('URL', '')

    return {
        'client_id': build_client_id(request),
        'events': [{
            'name': 'rss_view',
            'params': {
                'page_location': page_location,
                'feed_title': get_feed_title(context),
                'feed_format': feed_format,
                'content_path': get_content_path(context),
            },
        }],
    }


def _send_event(measurement_id, api_secret, payload):
    url = '{0}?measurement_id={1}&api_secret={2}'.format(
        GA4_MP_URL,
        measurement_id,
        api_secret,
    )
    try:
        requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    except Exception as error:
        logger.warning('GA4 RSS tracking failed: %s', error)


def track_rss_view(context, request, view_name):
    config = get_analytics_config()
    if config is None:
        return

    measurement_id, api_secret = config
    payload = build_payload(context, request, view_name)

    thread = threading.Thread(
        target=_send_event,
        args=(measurement_id, api_secret, payload),
        daemon=True,
    )
    thread.start()
