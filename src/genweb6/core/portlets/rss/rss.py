# -*- coding: utf-8 -*-
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from bs4 import BeautifulSoup
from logging import getLogger
from plone import api
from plone.app.portlets import PloneMessageFactory as _PMF
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.interface import implementer

from genweb6.core import _

import feedparser
import time

# Accept these bozo_exceptions encountered by feedparser when parsing
# the feed:
ACCEPTED_FEEDPARSER_EXCEPTIONS = (feedparser.CharacterEncodingOverride, )

# store the feeds here (which means in RAM)
FEED_DATA = {}  # url: ({date, title, url, itemlist})

logger = getLogger(__name__)


class RSSFeed(object):
    """an RSS feed"""

    # TODO: discuss whether we want an increasing update time here, probably not though
    FAILURE_DELAY = 10  # time in minutes after which we retry to load it after a failure

    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout

        self._items = []
        self._title = ""
        self._siteurl = ""
        self._loaded = False    # is the feed loaded
        self._failed = False    # does it fail at the last update?
        self._last_update_time_in_minutes = 0   # when was the feed last updated?
        self._last_update_time = None            # time as DateTime or Nonw

    @property
    def last_update_time_in_minutes(self):
        """return the time the last update was done in minutes"""
        return self._last_update_time_in_minutes

    @property
    def last_update_time(self):
        """return the time the last update was done in minutes"""
        return self._last_update_time

    @property
    def update_failed(self):
        return self._failed

    @property
    def ok(self):
        return (not self._failed and self._loaded)

    @property
    def loaded(self):
        """return whether this feed is loaded or not"""
        return self._loaded

    @property
    def needs_update(self):
        """check if this feed needs updating"""
        now = time.time() / 60
        return (self.last_update_time_in_minutes + self.timeout) < now

    def update(self):
        """update this feed"""
        now = time.time() / 60  # time in minutes

        try:
            # check for failure and retry
            if self.update_failed:
                if (self.last_update_time_in_minutes + self.FAILURE_DELAY) < now:
                    return self._retrieveFeed()
                else:
                    return False
            # check for regular update
            if self.needs_update:
                return self._retrieveFeed()
        except:
            self._failed = True
            logger.exception('failed to update RSS feed %s', self.url)

        return self.ok

    def _buildItemDict(self, item):
        link = item.links[0]['href']
        description = self.html_escape(item.get('description', '').encode('utf-8'))
        itemdict = {
            'title': item.title,
            'url': link,
            'summary': self.abrevia(description, 250),
            'image': item.get('href', '') or self.getFirstImageDescription(description),
            'categories': [tag['term'] for tag in item.tags],
        }
        if hasattr(item, "updated"):
            try:
                itemdict['updated'] = DateTime(item.updated)
            except DateTimeError:
                # It's okay to drop it because in the
                # template, this is checked with
                # ``exists:``
                pass

        return itemdict

    def _retrieveFeed(self):
        """do the actual work and try to retrieve the feed"""
        url = self.url
        if url != '':
            self._last_update_time_in_minutes = time.time() / 60
            self._last_update_time = DateTime()
            d = feedparser.parse(url)
            if getattr(d, 'bozo', 0) == 1 and not isinstance(d.get('bozo_exception'), ACCEPTED_FEEDPARSER_EXCEPTIONS):
                self._loaded = True     # we tried at least but have a failed load
                self._failed = True
                return False
            try:
                self._title = d.feed.title
            except AttributeError:
                self._title = ""
            self._items = []
            try:
                self._siteurl = d.feed.link
            except AttributeError:
                self._siteurl = ""
            for item in d['items']:
                try:
                    itemdict = self._buildItemDict(item)
                except AttributeError:
                    continue

                self._items.append(itemdict)
            self._loaded = True
            self._failed = False
            return True
        self._loaded = True
        self._failed = True     # no url set means failed
        return False    # no url set, although that actually should not really happen

    def html_escape(self, summary):
        summary = summary.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'").replace('&gt;', '>').replace('&lt;', '<')
        return summary.replace('&middot;', '·').replace('&rsquo;', "'").replace("&ldquo;", '"').replace("&nbsp;", ' ')

    def cleanConflictiveTags(self, summary):
        while "<iframe>" in summary:
            startTag = summary.find('<iframe>')
            endTag = summary.find('</iframe>', startTag) + 9
            summary = summary[0:startTag] + summary[endTag:]

        while "<script>" in summary:
            startTag = summary.find('<script>')
            endTag = summary.find('</script>', startTag) + 9
            summary = summary[0:startTag] + summary[endTag:]

        while "<img" in summary:
            startTag = summary.find('<img')
            endTag = summary.find('>', startTag) + 1
            summary = summary[0:startTag] + summary[endTag:]

        return summary

    def abrevia(self, summary, sumlenght):
        """ Retalla contingut de cadenes
        """
        bb = ''
        summary = self.cleanConflictiveTags(summary)
        if sumlenght < len(summary):
            bb = summary[:sumlenght]
            if '<a' in bb:
                startLink = summary.find('<a')
                sumlenght += 4 + summary.find('>', startLink) - startLink
                bb = summary[:sumlenght]

            lastspace = bb.rfind(' ')
            cutter = lastspace
            precut = bb[0:cutter]

            if precut.count('<b>') > precut.count('</b>'):
                cutter = summary.find('</b>', lastspace) + 4
            elif precut.count('<strong>') > precut.count('</strong>'):
                cutter = summary.find('</strong>', lastspace) + 9

            if precut.count('<a') > precut.count('</a>'):
                cutter = summary.find('</a>', lastspace) + 4

            bb = summary[0:cutter]

            if bb.count('<p') > precut.count('</p'):
                bb += ' ...</p>'
            else:
                bb = bb + ' ...'
        else:
            bb = summary

        try:
            return BeautifulSoup(bb.decode('utf-8', 'ignore')).prettify()
        except:
            return BeautifulSoup(bb).prettify()

    def getFirstImageDescription(self, summary):
        startTag = summary.find('<img')
        if startTag >= 0:
            startLink = summary.find('src', startTag) + 5
            endLink = summary.find('"', startLink)
            return summary[startLink:endLink]
        else:
            return None

    @property
    def items(self):
        return self._items

    # convenience methods for displaying
    #

    @property
    def feed_link(self):
        """return rss url of feed for portlet"""
        return self.url.replace("http://", "feed://")

    @property
    def title(self):
        """return title of feed for portlet"""
        return self._title

    @property
    def siteurl(self):
        """return the link to the site the RSS feed points to"""
        return self._siteurl


class IRSSPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_PMF(u'Title'),
        description=_PMF(u'Title of the portlet.  If omitted, the title of the feed will be used.'),
        required=False,
        default=u''
    )

    count = schema.Int(
        title=_PMF(u'Number of items to display'),
        description=_PMF(u'How many items to list.'),
        required=True,
        default=5
    )

    url = schema.TextLine(
        title=_PMF(u'URL of RSS feed'),
        description=_PMF(u'Link of the RSS feed to display.'),
        required=True,
        default=u''
    )

    timeout = schema.Int(
        title=_PMF(u'Feed reload timeout'),
        description=_PMF(u'Time in minutes after which the feed should be reloaded.'),
        required=True,
        default=100
    )

    display_date = schema.Bool(
        title=_(u'Display dates'),
        required=False,
        default=True
    )

    display_description = schema.Bool(
        title=_(u'Display descriptions'),
        required=False,
        default=True
    )

    display_image = schema.Bool(
        title=_(u'Display images'),
        required=False,
        default=True
    )

    display_categories = schema.Bool(
        title=_(u'Display categories'),
        required=False,
        default=False
    )

    more_url = schema.TextLine(
        title=_(u'More link'),
        description=_(u'Url that links to more content.'),
        required=False,
        default=u''
    )

    more_text = schema.TextLine(
        title=_(u'More text'),
        description=_(u'Text to show more content.'),
        required=False,
        default=u''
    )


@implementer(IRSSPortlet)
class Assignment(base.Assignment):

    portlet_title = u''

    @property
    def title(self):
        """return the title with RSS feed title or from URL"""
        feed = FEED_DATA.get(self.data.url, None)
        if feed is None:
            return u'RSS: ' + self.url[:20]
        else:
            return u'RSS: ' + feed.title[:20]

    def __init__(self, portlet_title=u'', count=5, url=u"", timeout=100,
                 display_date=True, display_description=True, display_image=True,
                 display_categories=False, more_text=u'', more_url=''):
        self.portlet_title = portlet_title
        self.count = count
        self.url = url
        self.timeout = timeout
        self.display_date = display_date
        self.display_description = display_description
        self.display_image = display_image
        self.display_categories = display_categories
        self.more_text = more_text
        self.more_url = more_url


class Renderer(base.DeferredRenderer):

    render_full = ZopeTwoPageTemplateFile('rss.pt')

    @property
    def initializing(self):
        """should return True if deferred template should be displayed"""
        feed = self._getFeed()
        if not feed.loaded:
            return True
        if feed.needs_update:
            return True
        return False

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True

    def deferred_update(self):
        """refresh data for serving via KSS"""
        feed = self._getFeed()
        feed.update()

    def update(self):
        """update data before rendering. We can not wait for KSS since users
        may not be using KSS."""
        self.deferred_update()

    def _getFeed(self):
        """return a feed object but do not update it"""
        feed = FEED_DATA.get(self.data.url, None)
        if feed is None:
            # create it
            feed = FEED_DATA[self.data.url] = RSSFeed(self.data.url, self.data.timeout)
        return feed

    @property
    def url(self):
        """return url of feed for portlet"""
        return self._getFeed().url

    @property
    def siteurl(self):
        """return url of site for portlet"""
        return self._getFeed().siteurl

    @property
    def feedlink(self):
        """return rss url of feed for portlet"""
        return self.data.url.replace("http://", "feed://")

    @property
    def title(self):
        """return title of feed for portlet"""
        return getattr(self.data, 'portlet_title', '') or self._getFeed().title

    @property
    def items(self):
        return self._getFeed().items[:self.data.count]

    @property
    def enabled(self):
        return self._getFeed().ok

    @property
    def displayDate(self):
        return self.data.display_date

    @property
    def displayDescription(self):
        return self.data.display_description


class AddForm(base.AddForm):
    schema = IRSSPortlet
    label = _PMF(u"Add RSS Portlet")
    description = _PMF(u"This portlet displays an RSS feed.")

    def create(self, data):
        return Assignment(portlet_title=data.get('portlet_title', u''),
                          count=data.get('count', 5),
                          url=data.get('url', ''),
                          timeout=data.get('timeout', 100),
                          display_date=data.get('display_date', True),
                          display_description=data.get('display_description', True),
                          display_image=data.get('display_image', True),
                          display_categories=data.get('display_categories', False),
                          more_text=data.get('more_text', u''),
                          more_url=data.get('more_url', ''))


class EditForm(base.EditForm):
    schema = IRSSPortlet
    label = _PMF(u"Edit RSS Portlet")
    description = _PMF(u"This portlet displays an RSS feed.")
