# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from BTrees.OOBTree import OOBTree
from Products.CMFCore.MemberDataTool import MemberAdapter as BaseMemberAdapter
from Products.CMFCore.MemberDataTool import _marker
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.permissions import ManageUsers
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _CMFPlone
from Products.CMFPlone.browser.syndication.adapters import BaseItem
from Products.CMFPlone.browser.syndication.adapters import FolderFeed
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces import ISocialMediaSchema
from Products.CMFPlone.interfaces.syndication import IFeedItem
from Products.CMFPlone.patterns.tinymce import TinyMCESettingsGenerator
from Products.CMFPlone.utils import getSiteLogo
from Products.CMFPlone.utils import get_portal
from Products.CMFPlone.utils import normalizeString
from Products.LDAPUserFolder.LDAPUser import LDAPUser
from Products.LDAPUserFolder.LDAPUser import NonexistingUser
from Products.LDAPUserFolder.utils import GROUP_MEMBER_MAP
from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet
from Products.PlonePAS.utils import safe_unicode
from Products.PluggableAuthService.events import PropertiesUpdated
from Products.PluggableAuthService.interfaces.authservice import IPluggableAuthService

from borg.localrole.interfaces import IFactoryTempFolder
from hashlib import sha1
from io import StringIO
from operator import itemgetter
from plone import api
from plone.app.content.interfaces import INameFromTitle
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.contenttypes.browser.link_redirect_view import NON_RESOLVABLE_URL_SCHEMES
from plone.app.textfield.value import IRichTextValue
from plone.app.users.browser.interfaces import IUserIdGenerator
from plone.app.users.browser.register import RENAME_AFTER_CREATION_ATTEMPTS
from plone.app.users.utils import uuid_userid_generator
from plone.app.uuid.utils import uuidToObject
from plone.app.widgets.utils import get_relateditems_options
from plone.app.z3cform.utils import call_callables
from plone.base.interfaces import IPloneSiteRoot
from plone.base.interfaces.controlpanel import IMailSchema
from plone.base.utils import pretty_title_or_id
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from urllib.parse import quote_plus
from urllib.parse import urlparse
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.event import notify
from zope.schema._field import Choice
from zope.schema.interfaces import ConstraintNotSatisfied

from genweb6.core import _
from genweb6.core.adapters.portrait import IPortraitUploadAdapter
from genweb6.core.utils import portal_url
from genweb6.core.utils import pref_lang

import json
import logging
import requests
import six

try:
    from collective.relationhelpers import api as relapi

    HAS_RELAPI = True
except ImportError:
    HAS_RELAPI = False

try:
    from Products.CMFPlone import relationhelper

    HAS_PLONE6 = True
except ImportError:
    HAS_PLONE6 = False

logger = logging.getLogger('event.LDAPUserFolder')
genweb_log = logging.getLogger('genweb6.core')


# Dejo la funcion que teniamos ya que ha cambiado mucho
# BORRAR cuando veamos que funciona todo
# def generate_user_id(self, data):
#     """Generate a user id from data.

#     The data is the data passed in the form.  Note that when email
#     is used as login, the data will not have a username.

#     There are plans to add some more options and add a hook here
#     so it is possible to use a different scheme here, for example
#     creating a uuid or creating bob-jones-1 based on the fullname.

#     This will update the 'username' key of the data that is passed.
#     """
#     if data.get('username'):
#         default = data.get('username').lower()
#     elif data.get('email'):
#         default = data.get('email').lower()
#     else:
#         default = ''
#     data['username'] = default
#     return default


def generate_user_id(self, data):
    """Generate a user id from data.

    We try a few options for coming up with a good user id:

    1. We query a utility, so integrators can register a hook to
       generate a user id using their own logic.

    2. If use_uuid_as_userid is set in the registry, we
       generate a uuid.

    3. If a username is given and we do not use email as login,
       then we simply return that username as the user id.

    4. We create a user id based on the full name, if that is
       passed.  This may result in an id like bob-jones-2.

    When the email address is used as login name, we originally
    used the email address as user id as well.  This has a few
    possible downsides, which are the main reasons for the new,
    pluggable approach:

    - It does not work for some valid email addresses.

    - Exposing the email address in this way may not be wanted.

    - When the user later changes his email address, the user id
      will still be his old address.  It works, but may be
      confusing.

    Another possibility would be to simply generate a uuid, but that
    is ugly.  We could certainly try that though: the big plus here
    would be that you then cannot create a new user with the same user
    id as a previously existing user if this ever gets removed.  If
    you would get the same id, this new user would get the same global
    and local roles, if those have not been cleaned up.

    When a user id is chosen, the 'user_id' key of the data gets
    set and the user id is returned.
    """
    generator = queryUtility(IUserIdGenerator)
    if generator:
        userid = generator(data)
        if userid:
            data['user_id'] = userid
            return userid

    settings = self._get_security_settings()
    if settings.use_uuid_as_userid:
        userid = uuid_userid_generator()
        data['user_id'] = userid
        return userid

    # We may have a username already.
    userid = data.get('username').lower()
    if userid:
        # If we are not using email as login, then this user name is fine.
        if not settings.use_email_as_login:
            data['user_id'] = userid
            return userid

    # First get a default value that we can return if we cannot
    # find anything better.
    pas = getToolByName(self.context, 'acl_users')
    email = pas.applyTransform(data.get('email').lower())
    default = data.get('username').lower() or email or ''
    data['user_id'] = default
    fullname = data.get('fullname')
    if not fullname:
        return default
    userid = normalizeString(fullname)
    # First check that this is a valid member id, regardless of
    # whether a member with this id already exists or not.  We
    # access an underscore attribute of the registration tool, so
    # we take a precaution in case this is ever removed as an
    # implementation detail.
    registration = getToolByName(self.context, 'portal_registration')
    if hasattr(registration, '_ALLOWED_MEMBER_ID_PATTERN'):
        if not registration._ALLOWED_MEMBER_ID_PATTERN.match(userid):
            # If 'bob-jones' is not good then 'bob-jones-1' will not
            # be good either.
            return default
    if registration.isMemberIdAllowed(userid):
        data['user_id'] = userid
        return userid
    # Try bob-jones-1, bob-jones-2, etc.
    idx = 1
    while idx <= RENAME_AFTER_CREATION_ATTEMPTS:
        new_id = "%s-%d" % (userid, idx)
        if registration.isMemberIdAllowed(new_id):
            data['user_id'] = new_id
            return new_id
        idx += 1

    # We cannot come up with a nice id, so we simply return the default.
    return default


def setMemberProperties(self, mapping, force_local=0, force_empty=False):
    """PAS-specific method to set the properties of a
    member. Ignores 'force_local', which is not reliably present.
    """
    sheets = None

    # We could pay attention to force_local here...
    if not IPluggableAuthService.providedBy(self._tool.acl_users):
        # Defer to base impl in absence of PAS, a PAS user, or
        # property sheets
        return BaseMemberAdapter.setMemberProperties(self, mapping)
    else:
        # It's a PAS! Whee!
        user = self.getUser()
        sheets = getattr(user, 'getOrderedPropertySheets', lambda: None)()

        # We won't always have PlonePAS users, due to acquisition,
        # nor are guaranteed property sheets
        if not sheets:
            # Defer to base impl if we have a PAS but no property
            # sheets.
            return BaseMemberAdapter.setMemberProperties(self, mapping)

    # If we got this far, we have a PAS and some property sheets.
    # XXX track values set to defer to default impl
    # property routing?
    modified = False
    for k, v in mapping.items():
        if v is None and not force_empty:
            continue
        for sheet in sheets:
            if not sheet.hasProperty(k):
                continue
            if IMutablePropertySheet.providedBy(sheet):
                sheet.setProperty(user, k, v)
                modified = True
            else:
                break
    if modified:
        self.notifyModified()

        # Genweb: Updated by patch
        notify(PropertiesUpdated(user, mapping))

    # Trigger PropertiesUpdated event when member properties are updated,
    # excluding user login events
    if not set(mapping.keys()) & set(('login_time', 'last_login_time')):
        notify(PropertiesUpdated(self, mapping))


# Add subjects and creators to searchableText Dexterity objects
def SearchableText(obj):
    text = u''
    richtext = IRichText(obj, None)
    if richtext:
        textvalue = richtext.text
        if IRichTextValue.providedBy(textvalue):
            transforms = api.portal.get_tool(name='portal_transforms')
            # Before you think about switching raw/output
            # or mimeType/outputMimeType, first read
            # https://github.com/plone/Products.CMFPlone/issues/2066
            raw = safe_unicode(textvalue.raw)
            if six.PY2:
                raw = raw.encode('utf-8', 'replace')
            text = transforms.convertTo(
                'text/plain',
                raw,
                mimetype=textvalue.mimeType,
            ).getData().strip()

    subject = u' '.join(
        [safe_unicode(s) for s in obj.Subject()]
    )

    creators = u' '.join(
        [safe_unicode(c) for c in obj.creators]
    )

    return u' '.join((
        safe_unicode(obj.id),
        safe_unicode(obj.title) or u'',
        safe_unicode(obj.description) or u'',
        safe_unicode(text),
        safe_unicode(subject),
        safe_unicode(creators),
    ))


def getThreads(self, start=0, size=None, root=0, depth=None):
    """Get threaded comments
    """

    def recurse(comment_id, d=0):
        # Yield the current comment before we look for its children
        yield {'id': comment_id, 'comment': self[comment_id], 'depth': d}

        # Recurse if there are children and we are not out of our depth
        if depth is None or d + 1 < depth:
            children = self._children.get(comment_id, None)
            if children is not None:
                for child_id in children:
                    for value in recurse(child_id, d + 1):
                        yield value

    # Find top level threads
    comments = self._children.get(root, None)
    if comments is not None:
        count = 0
        for comment_id in reversed(comments.keys(min=start)):

            # Abort if we have found all the threads we want
            count += 1
            if size and count > size:
                return

            # Let the closure recurse
            for value in recurse(comment_id):
                yield value


def getUserByAttr(self, name, value, pwd=None, cache=0):
    """ Get a user based on a name/value pair representing an
        LDAP attribute provided to the user.  If cache is True,
        try to cache the result using 'value' as the key
    """
    if not value:
        return None

    cache_type = pwd and 'authenticated' or 'anonymous'
    negative_cache_key = '%s:%s:%s' % (
        name, value, sha1((pwd or '').encode()).hexdigest())
    if cache:
        if self._cache('negative').get(negative_cache_key) is not None:
            return None

        cached_user = self._cache(cache_type).get(value, pwd)

        if cached_user:
            msg = 'getUserByAttr: "%s" cached in %s cache' % (
                value, cache_type)
            logger.debug(msg)
            return cached_user

    user_roles, user_dn, user_attrs, ldap_groups = self._lookupuserbyattr(
        name=name, value=value, pwd=pwd)

    if user_dn is None:
        logger.debug('getUserByAttr: "%s=%s" not found' % (name, value))
        self._cache('negative').set(negative_cache_key, NonexistingUser())
        return None

    if user_attrs is None:
        msg = 'getUserByAttr: "%s=%s" has no properties, bailing' % (
            name, value)
        logger.debug(msg)
        self._cache('negative').set(negative_cache_key, NonexistingUser())
        return None

    if user_roles is None or user_roles == self._roles:
        msg = 'getUserByAttr: "%s=%s" only has roles %s' % (
            name, value, str(user_roles))
        logger.debug(msg)

    login_name = user_attrs.get(self._login_attr, '')
    uid = user_attrs.get(self._uid_attr, '')

    if self._login_attr != 'dn' and len(login_name) > 0:
        try:
            if name == self._login_attr:
                logins = [x for x in login_name
                          if value.strip().lower() == x.lower()]
                login_name = logins[0]
            else:
                login_name = login_name[0]
        except:
            msg = ('****getUserByAttr: logins %s and login_name %s' %
                   (logins, login_name))
            logger.error(msg)
            pass
    elif len(login_name) == 0:
        msg = 'getUserByAttr: "%s" has no "%s" (Login) value!' % (
            user_dn, self._login_attr)
        logger.debug(msg)
        self._cache('negative').set(negative_cache_key, NonexistingUser())
        return None

    if self._uid_attr != 'dn' and len(uid) > 0:
        uid = uid[0]
    elif len(uid) == 0:
        msg = 'getUserByAttr: "%s" has no "%s" (UID Attribute) value!' % (
            user_dn, self._uid_attr)
        logger.debug(msg)
        self._cache('negative').set(negative_cache_key, NonexistingUser())
        return None

    # BEGIN PATCH
    login_name = login_name.lower()
    uid = uid.lower()
    # END PATCH

    user_obj = LDAPUser(uid, login_name, pwd or 'undef', user_roles or [],
                        [], user_dn, user_attrs, self.getMappedUserAttrs(),
                        self.getMultivaluedUserAttrs(),
                        self.getBinaryUserAttrs(),
                        ldap_groups=ldap_groups)

    if cache:
        self._cache(cache_type).set(value, user_obj)

    return user_obj


def enumerateUsers(self, id=None, login=None, exact_match=0, sort_by=None,
                   max_results=None, **kw):
    """ Fulfill the UserEnumerationPlugin requirements """
    view_name = self.getId() + '_enumerateUsers'
    criteria = {'id': id, 'login': login, 'exact_match': exact_match,
                'sort_by': sort_by, 'max_results': max_results}
    criteria.update(kw)

    cached_info = self.ZCacheable_get(view_name=view_name,
                                      keywords=criteria,
                                      default=None)

    if cached_info is not None:
        logger.debug('returning cached results from enumerateUsers')
        return cached_info

    result = []
    acl = self._getLDAPUserFolder()
    login_attr = acl.getProperty('_login_attr')
    uid_attr = acl.getProperty('_uid_attr')
    rdn_attr = acl.getProperty('_rdnattr')
    plugin_id = self.getId()
    edit_url = '%s/%s/manage_userrecords' % (plugin_id, acl.getId())

    if acl is None:
        return ()

    if exact_match and (id or login):
        if id:
            ldap_user = acl.getUserById(id)
            if ldap_user is not None and ldap_user.getId() != id:
                ldap_user = None
        elif login:
            ldap_user = acl.getUser(login)
            if ldap_user is not None and ldap_user.getUserName() != login:
                ldap_user = None

        if ldap_user is not None:
            qs = 'user_dn=%s' % quote_plus(ldap_user.getUserDN())
            result.append({'id': ldap_user.getId(),
                           'login': ldap_user.getProperty(login_attr),
                           'pluginid': plugin_id,
                           'editurl': '%s?%s' % (edit_url, qs)})
    else:
        l_results = []
        seen = []
        ldap_criteria = {}

        if id:
            if uid_attr == 'dn':
                # Workaround: Due to the way findUser reacts when a DN
                # is searched for I need to hack around it... This
                # limits the usefulness of searching by ID if the user
                # folder uses the full DN aas user ID.
                ldap_criteria[rdn_attr] = id
            else:
                ldap_criteria[uid_attr] = id

        if login:
            ldap_criteria[login_attr] = login

        for key, val in kw.items():
            if key not in (login_attr, uid_attr):
                ldap_criteria[key] = val

        # If no criteria are given create a criteria set that will
        # return all users
        if not login and not id:
            ldap_criteria[login_attr] = ''

        l_results = acl.searchUsers(exact_match=exact_match,
                                    **ldap_criteria)

        for l_res in l_results:
            try:
                # If the LDAPUserFolder returns an error, bail
                if (l_res.get('sn', '') == 'Error' and l_res.get('cn', '') == 'n/a'):
                    return ()

                if l_res['dn'] not in seen:
                    # BEGIN PATCH
                    l_res['id'] = l_res[uid_attr].lower()
                    l_res['login'] = l_res[login_attr].lower()
                    # END PATCH
                    l_res['pluginid'] = plugin_id
                    quoted_dn = quote_plus(l_res['dn'])
                    l_res['editurl'] = '%s?user_dn=%s' % (edit_url, quoted_dn)
                    result.append(l_res)
                    seen.append(l_res['dn'])
            except:
                msg = ('****Result ldap error: l_res %s' % (l_res))
                logger.error(msg)
                pass

        if sort_by is not None:
            result.sort(key=lambda item: item.get(sort_by, '').lower())

        if isinstance(max_results, int) and len(result) > max_results:
            result = result[:max_results-1]

    result = tuple(result)
    self.ZCacheable_set(result, view_name=view_name, keywords=criteria)

    return result


def chooseName(self, name, obj):
    container = aq_inner(self.context)
    if not name:
        nameFromTitle = INameFromTitle(obj, None)
        if nameFromTitle is not None:
            name = nameFromTitle.title
        if not name:
            name = getattr(aq_base(obj), 'id', None)
        if not name:
            name = getattr(aq_base(obj), 'portal_type', None)
        if not name:
            name = obj.__class__.__name__

    if not isinstance(name, six.text_type):
        name = six.text_type(name, 'utf-8')

    request = getattr(obj.__of__(container), 'REQUEST', None)
    if request is not None:
        name = IUserPreferredURLNormalizer(request).normalize(name)
    else:
        name = getUtility(IURLNormalizer).normalize(name)

    if name[:1] == '_':
        name = name[1:]

    return self._findUniqueName(name, obj)


def html_results(self, query):
    """html results, used for in the edit screen of a collection,
       used in the live update results"""

    options = dict(original_context=self.context)
    results = self(query, sort_on=self.request.get('sort_on', None),
                   sort_order=self.request.get('sort_order', None),
                   limit=self.request.get('limit', 1000))

    lang_res = []
    for res in results:
        if hasattr(res, 'language'):
            if res.language == pref_lang():
                lang_res.append(res)
        else:
            if res.Language() == pref_lang():
                lang_res.append(res)

    results = IContentListing(lang_res)
    return getMultiAdapter(
        (results, self.request),
        name='display_query_results'
    )(**options)


def sitemapObjects(self):
    """Returns the data to create the sitemap."""
    catalog = api.portal.get_tool(name='portal_catalog')
    query = {}
    utils = api.portal.get_tool(name='plone_utils')
    query['portal_type'] = utils.getUserFriendlyTypes()
    ptool = api.portal.get_tool(name='portal_properties')
    siteProperties = getattr(ptool, 'site_properties')
    typesUseViewActionInListings = frozenset(
        siteProperties.getProperty('typesUseViewActionInListings', [])
    )

    is_plone_site_root = IPloneSiteRoot.providedBy(self.context)
    if not is_plone_site_root:
        query['path'] = '/'.join(self.context.getPhysicalPath())

    query['is_default_page'] = True
    default_page_modified = OOBTree()
    for item in catalog.searchResults(query):
        key = item.getURL().rsplit('/', 1)[0]
        value = (item.modified.micros(), item.modified.ISO8601())
        default_page_modified[key] = value

    # The plone site root is not catalogued.
    if is_plone_site_root:
        loc = self.context.absolute_url()
        date = self.context.modified()
        # Comparison must be on GMT value
        modified = (date.micros(), date.ISO8601())
        default_modified = default_page_modified.get(loc, None)
        if default_modified is not None:
            modified = max(modified, default_modified)
        lastmod = modified[1]
        yield {
            'loc': loc,
            'lastmod': lastmod,
            # 'changefreq': 'always', # hourly/daily/weekly/monthly/yearly/never
            # 'prioriy': 0.5, # 0.0 to 1.0
        }

    query['is_default_page'] = False
    for item in catalog.searchResults(query):
        loc = item.getURL()
        date = item.modified
        # Comparison must be on GMT value
        modified = (date.micros(), date.ISO8601())
        default_modified = default_page_modified.get(loc, None)
        if default_modified is not None:
            modified = max(modified, default_modified)
        lastmod = modified[1]
        if item.portal_type in typesUseViewActionInListings:
            loc += "/view"
        yield {
            'loc': loc,
            'lastmod': lastmod,
            # 'changefreq': 'always', # hourly/daily/weekly/monthly/yearly/never
            # 'prioriy': 0.5, # 0.0 to 1.0
        }


# Extensible member portrait management
def changeMemberPortrait(self, portrait, id=None):
    """update the portait of a member.

    We URL-quote the member id if needed.

    Note that this method might be called by an anonymous user who
    is getting registered.  This method will then be called from
    plone.app.users and this is fine.  When called from restricted
    python code or with a curl command by a hacker, the
    declareProtected line will kick in and prevent use of this
    method.
    """
    authenticated_id = self.getAuthenticatedMember().getId()
    if not id:
        id = authenticated_id
    safe_id = self._getSafeMemberId(id)

    if authenticated_id and id != authenticated_id:
        # Only Managers can change portraits of others.
        if not _checkPermission(ManageUsers, self):
            raise Unauthorized

    # The plugable actions for how to handle the portrait.
    adapter = getMultiAdapter((self, self.REQUEST), IPortraitUploadAdapter)
    adapter(portrait, safe_id)


def deletePersonalPortrait(self, id=None):
    """deletes the Portait of a member.
    """
    authenticated_id = self.getAuthenticatedMember().getId()
    if not id:
        id = authenticated_id
    safe_id = self._getSafeMemberId(id)
    if id != authenticated_id and not _checkPermission(
            ManageUsers, self):
        raise Unauthorized

    # The plugable actions for how to handle the portrait.
    portrait_url = portal_url() + '/defaultUser.png'
    imgData = requests.get(portrait_url).content
    image = StringIO(imgData)
    image.filename = 'defaultUser'
    adapter = getMultiAdapter((self, self.REQUEST), IPortraitUploadAdapter)
    adapter(image, safe_id)
    # membertool = getToolByName(self, 'portal_memberdata')
    # return membertool._deletePortrait(safe_id)


@memoize
def _get_tags(self):
    site = getSite()
    registry = getUtility(IRegistry)
    settings = registry.forInterface(
        ISocialMediaSchema, prefix="plone", check=False
    )

    if not settings.share_social_data:
        return []

    # Comentar lineas para que sean visible siempre los tags
    # portal_membership = api.portal.get_tool(name="portal_membership")  # Se modifico para hacerlo con la api
    # is_anonymous = bool(portal_membership.isAnonymousUser())
    # if not is_anonymous:
    #     return []

    page_title = getattr(self.context, 'seo_title', None)  # Añadido
    if not page_title:
        page_title = self.page_title

    tags = [
        dict(itemprop="name", content=page_title),
        dict(name="twitter:card", content="summary"),
        dict(property="og:site_name", content=self.site_title_setting),
        dict(property="og:title", content=page_title),
        dict(property="twitter:title", content=page_title),  # Añadido
        dict(property="og:type", content="website"),
    ]

    if settings.twitter_username:
        tags.append(
            dict(
                name="twitter:site",
                content="@" + settings.twitter_username.lstrip("@"),
            )
        )

    if settings.facebook_app_id:
        tags.append(dict(property="fb:app_id", content=settings.facebook_app_id))

    if settings.facebook_username:
        tags.append(
            dict(
                property="og:article:publisher",
                content="https://www.facebook.com/" + settings.facebook_username,
            )
        )

    # reuse syndication since that packages the data
    # the way we'd prefer likely
    feed = FolderFeed(site)
    item = queryMultiAdapter((self.context, feed), IFeedItem, default=None)
    if item is None:
        item = BaseItem(self.context, feed)

    description = getattr(self.context, 'seo_description', None)  # Añadido
    if not description:
        description = item.description

    tags.extend(
        [
            dict(itemprop="description", content=description),
            dict(itemprop="url", content=item.link),
            dict(property="og:description", content=description),
            dict(property="twitter:description", content=description),  # Añadido
            dict(property="og:url", content=item.link),
            dict(property="twitter:url", content=item.link),  # Añadido
        ]
    )

    found_image = False
    if item.has_enclosure and item.file_length > 0:
        if item.file_type.startswith("image"):
            found_image = True
            tags.extend(
                [
                    dict(property="og:image", content=item.file_url),
                    dict(property="twitter:image", content=item.file_url),  # Añadido
                    dict(itemprop="image", content=item.file_url),
                    dict(property="og:image:type", content=item.file_type),
                ]
            )
        elif item.file_type.startswith("video") or item.file_type == "application/x-shockwave-flash":
            tags.extend(
                [
                    dict(property="og:video", content=item.file_url),
                    dict(property="og:video:type", content=item.file_type),
                ]
            )
        elif item.file_type.startswith("audio"):
            tags.extend(
                [
                    dict(property="og:audio", content=item.file_url),
                    dict(property="og:audio:type", content=item.file_type),
                ]
            )

    if not found_image:
        url = getSiteLogo()
        tags.extend(
            [
                dict(property="og:image", content=url),
                dict(property="twitter:image", content=url),  # Añadido
                dict(itemprop="image", content=url),
                dict(property="og:image:type", content="image/png"),
            ]
        )
    return tags


gw_group = dict(
    member=[
        ('Member', _CMFPlone('My Preferences')),
    ],
    site=[
        ('plone-general', _CMFPlone('General')),
        ('plone-content', _CMFPlone('Content')),
        ('plone-users', _CMFPlone('Users')),
        ('plone-security', _CMFPlone('Security')),
        ('plone-advanced', _CMFPlone('Advanced')),
        ('Plone', _CMFPlone('Plone Configuration')),
        ('Products', _CMFPlone('Add-on Configuration')),
        ('genweb-configuration', _('Genweb Configuration')),  # Añadido
        ('genweb-advanced', _('Genweb Advanced')),  # Añadido
        ('genweb-connection', _('Connections')),  # Añadido
    ]
)


def mailhost_warning(self):
    # Añadir el control para ver si puede acceder al controlpanel de Correo
    # Los permisos corresponden a plone.app.controlpanel.Mail
    username = api.user.get_current().id
    user_permissions = api.user.get_roles(username=username, obj=self)
    if 'Manager' not in user_permissions and 'Site Administrator' not in user_permissions:
        return False

    registry = getUtility(IRegistry)
    mail_settings = registry.forInterface(IMailSchema, prefix="plone", check=False)
    mailhost = mail_settings.smtp_host
    email = mail_settings.email_from_address
    if mailhost and email:
        return False
    return True


title_displaysubmenuitem = _(u'label_choose_template', default=u'Display')


title_factoriessubmenuitem = _(u'label_add_new_item', default=u'Add new\u2026')


def getGroups(self, dn='*', attr=None, pwd=''):
    """ returns a list of possible groups from the ldap tree
        (Used e.g. in showgroups.dtml) or, if a DN is passed
        in, all groups for that particular DN.
    """
    group_list = []
    no_show = ('Anonymous', 'Authenticated', 'Shared')

    if self._local_groups:
        if dn != '*':
            all_groups_list = self._groups_store.get(dn) or []
        else:
            all_groups_dict = {}
            zope_roles = list(self.valid_roles())
            zope_roles.extend(list(self._additional_groups))

            for role_name in zope_roles:
                if role_name not in no_show:
                    all_groups_dict[role_name] = 1

            all_groups_list = all_groups_dict.keys()

        for group in all_groups_list:
            if attr is None:
                group_list.append((group, group))
            else:
                group_list.append(group)

        group_list.sort()

    else:
        gscope = self._delegate.getScopes()[self.groups_scope]

        if dn != '*':
            f_template = '(&(objectClass=%s)(%s=%s))'
            group_filter = '(|'

            for g_name, m_name in GROUP_MEMBER_MAP.items():
                fltr = self._delegate.filter_format(f_template,
                                                    (g_name, m_name, dn))
                group_filter += fltr

            group_filter += ')'

        else:
            group_filter = '(|'

            for g_name in GROUP_MEMBER_MAP.keys():
                fltr = self._delegate.filter_format('(objectClass=%s)',
                                                    (g_name,))
                group_filter += fltr

            group_filter += ')'

        res = self._delegate.search(base=self.groups_base, scope=gscope,
                                    filter=group_filter, attrs=['cn'],
                                    bind_dn='', bind_pwd='')

        exc = res['exception']
        if exc and exc != 'Too many results for this query':
            if attr is None:
                group_list = (('', exc),)
            else:
                group_list = (exc,)
        elif res['size'] > 0:
            res_dicts = res['results']
            for i in range(res['size']):
                dn = res_dicts[i].get('dn')
                try:
                    cn = res_dicts[i]['cn'][0]
                except KeyError:    # NDS oddity
                    cn = self._delegate.explode_dn(dn, 1)[0]

                if attr is None:
                    group_list.append((cn, dn))
                elif attr == 'cn':
                    group_list.append(cn)
                elif attr == 'dn':
                    group_list.append(dn)

    return group_list


def getProperty(self, id, default=_marker):
    """PAS-specific method to fetch a user's properties. Looks
    through the ordered property sheets.
    """
    sheets = None
    if not IPluggableAuthService.providedBy(self._tool.acl_users):
        return BaseMemberAdapter.getProperty(self, id)
    else:
        # It's a PAS! Whee!
        user = self.getUser()
        sheets = getattr(user, 'getOrderedPropertySheets', lambda: None)()

        # we won't always have PlonePAS users, due to acquisition,
        # nor are guaranteed property sheets
        if not sheets:
            try:
                return BaseMemberAdapter.getProperty(self, id, default)
            except ValueError:
                # Zope users don't have PropertySheets,
                # return an empty string for them if the property
                # doesn't exists.
                return ''

    # If we made this far, we found a PAS and some property sheets.
    for sheet in sheets:
        if sheet.hasProperty(id):
            # Return the first one that has the property.
            value = sheet.getProperty(id)
            if six.PY2 and isinstance(value, six.text_type):
                # XXX Temporarily work around the fact that
                # property sheets blindly store and return
                # unicode. This is sub-optimal and should be
                # dealed with at the property sheets level by
                # using Zope's converters.
                return value.encode('utf-8')
            if value != '':
                return value
            else:
                continue

    # Couldn't find the property in the property sheets. Try to
    # delegate back to the base implementation.
    return BaseMemberAdapter.getProperty(self, id, default)


def import_relations(self, data):
    ignore = [
        "translationOf",  # old LinguaPlone
        "isReferencing",  # linkintegrity
        "internal_references",  # obsolete
        "link",  # tab
        "link1",  # extranetfrontpage
        "link2",  # extranetfrontpage
        "link3",  # extranetfrontpage
        "link4",  # extranetfrontpage
        "box3_link",  # shopfrontpage
        "box1_link",  # shopfrontpage
        "box2_link",  # shopfrontpage
        "source",  # remotedisplay
        "internally_links_to",  # DoormatReference
    ]
    all_fixed_relations = []
    for rel in data:
        if "relationship" in rel and rel["relationship"] in ignore:  # Añadido a la condición la comprobación de que exista el atributo relationship
            continue
        rel["from_attribute"] = self.get_from_attribute(rel)
        all_fixed_relations.append(rel)
    all_fixed_relations = sorted(
        all_fixed_relations, key=itemgetter("from_uuid", "from_attribute")
    )
    if HAS_RELAPI:
        relapi.purge_relations()
        relapi.cleanup_intids()
        relapi.restore_relations(all_relations=all_fixed_relations)
    elif HAS_PLONE6:
        relationhelper.purge_relations()
        relationhelper.cleanup_intids()
        relationhelper.restore_relations(all_relations=all_fixed_relations)


# Añadimos el parametro long_format=1 para mostrar un formato de fecha largo en la vista de author
def author_content(self):
    results = []

    plone_view = self.context.restrictedTraverse(
        '@@plone'
    )

    brains = self.portal_catalog.searchResults(
        Creator=self.username,
        sort_on='created',
        sort_order='reverse'
    )

    for brain in brains[:10]:
        results.append({
            'title': pretty_title_or_id(
                self, brain
            ),
            'date': plone_view.toLocalizedTime(
                brain.Date, long_format=1
            ),
            'url': brain.getURL()
        })

    return results


# Traducimos el título del portlet para que se ordenen alfabéticamente
def addable_portlets(self):
    baseUrl = self.baseUrl()
    addviewbase = baseUrl.replace(self.context_url(), "")

    def sort_key(v):
        return v.get("title")

    def check_permission(p):
        addview = p.addview
        if not addview:
            return False

        addview = "{}/+/{}".format(
            addviewbase,
            addview,
        )
        if addview.startswith("/"):
            addview = addview[1:]
        try:
            self.context.restrictedTraverse(str(addview))
        except (AttributeError, KeyError, Unauthorized, NotFound):
            return False
        return True

    portlets = [
        {
            "title": self.context.translate(p.title, domain="plone"),  # Aplicamos la traducción
            "description": p.description,
            "addview": f"{addviewbase}/+/{p.addview}",
        }
        for p in self.manager.getAddablePortletTypes()
        if check_permission(p)
    ]

    portlets.sort(key=sort_key)
    return portlets


# Modificamos el path del parámetro prependToUrl para no generar ../resolveuid
def tinymce(self):
    """
    data-pat-tinymce : JSON.stringify({
        relatedItems: {
            vocabularyUrl: config.portal_url +
            '/@@getVocabulary?name=plone.app.vocabularies.Catalog'
        },
        tiny: config,
        prependToUrl: 'resolveuid/',
        linkAttribute: 'UID',
        prependToScalePart: '/@@images/image/'
        })
    """

    generator = TinyMCESettingsGenerator(self.context, self.request)
    settings = generator.settings
    folder = aq_inner(self.context)

    # Test if we are currently creating an Archetype object
    if IFactoryTempFolder.providedBy(aq_parent(folder)):
        folder = aq_parent(aq_parent(aq_parent(folder)))
    if not IFolderish.providedBy(folder):
        folder = aq_parent(folder)

    if IPloneSiteRoot.providedBy(folder):
        initial = None
    else:
        initial = IUUID(folder, None)

    portal = get_portal()
    portal_url = portal.absolute_url()
    current_path = folder.absolute_url()[len(portal_url) :]

    image_types = settings.image_objects or []

    server_url = self.request.get("SERVER_URL", "")
    site_path = portal_url[len(server_url) :]

    related_items_config = get_relateditems_options(
        context=self.context,
        value=None,
        separator=";",
        vocabulary_name="plone.app.vocabularies.Catalog",
        vocabulary_view="@@getVocabulary",
        field_name=None,
    )
    related_items_config = call_callables(related_items_config, self.context)

    configuration = {
        "base_url": self.context.absolute_url(),
        "imageTypes": image_types,
        # Keep imageScales at least until https://github.com/plone/mockup/pull/1156
        # is merged and plone.staticresources is updated.
        "imageScales": self.image_scales,
        "pictureVariants": self.picture_variants,
        "imageCaptioningEnabled": self.image_captioning,
        "linkAttribute": "UID",
        # This is for loading the languages on tinymce
        "loadingBaseUrl": "{}/++plone++static/components/tinymce-builded/"
        "js/tinymce".format(portal_url),
        "relatedItems": related_items_config,
        "prependToScalePart": "/@@images/image/",
        "prependToUrl": "resolveuid/",  # Moficamos el path para no genererar ../
        "inline": settings.inline,
        "tiny": generator.get_tiny_config(),
        "upload": {
            "baseUrl": portal_url,
            "currentPath": current_path,
            "initialFolder": initial,
            "maxFiles": 1,
            "relativePath": "@@fileUpload",
            "showTitle": False,
            "uploadMultiple": False,
        },
    }
    return {"data-pat-tinymce": json.dumps(configuration)}

from zope.schema import getFieldsInOrder
from collective.easyform.api import get_actions
from collective.easyform.api import get_schema
from collective.easyform.interfaces import ISaveData
from collective.easyform.serializer import convertAfterDeserialize

def deserializeSavedData(self, data):
    if "savedDataStorage" in data:
        storage = data["savedDataStorage"]
        actions = getFieldsInOrder(get_actions(self.context))
        schema = get_schema(self.context)
        AllFieldsinOrder = schema.namesAndDescriptions()
        included_columns_in_savedata = []
        for column, field in AllFieldsinOrder:
            if "label" not in field.__str__().lower():
                included_columns_in_savedata.append(column)
        for name, action in actions:
            if ISaveData.providedBy(action) and name in storage:
                savedData = storage[name]
                for key, value in savedData.items():
                    for name in included_columns_in_savedata:  # schema.names():
                        try:
                            value[name] = convertAfterDeserialize(
                                schema[name], value[name]
                            )
                        except:
                            value[name] = name
                    action.setDataRow(int(key), value)

from collective.easyform.api import is_file_data
from xml.etree import ElementTree as ET
from zope.contenttype import guess_content_type
from csv import writer as csvwriter
from DateTime import DateTime
from six import BytesIO

def get_attachments(self, fields, request):
    """Return all attachments uploaded in form."""
    attachments = []
    # if requested, generate CSV attachment of form values
    sendCSV = getattr(self, "sendCSV", None)
    sendWithHeader = getattr(self, "sendWithHeader", None)
    sendXLSX = getattr(self, "sendXLSX", None)
    if sendCSV or sendXLSX:
        csvdata = ()
    sendXML = getattr(self, "sendXML", None)
    if sendXML:
        xmlRoot = ET.Element("form")
    field_names = self.get_field_names_in_order()
    for fname in field_names:
        try:
            field = fields[fname]
        except:
            continue
        if sendCSV or sendXLSX:
            if not is_file_data(field):
                val = self.serialize(field)
                if six.PY2:
                    val = val.encode("utf-8")
                csvdata += (val,)
        if sendXML:
            if not is_file_data(field):
                ET.SubElement(xmlRoot, "field", name=fname).text = self.serialize(
                    field
                )  # noqa
        if is_file_data(field):
            data = field.data
            filename = field.filename
            mimetype, enc = guess_content_type(filename, data, None)
            attachments.append((filename, mimetype, enc, data))
    if sendCSV:
        output = StringIO()
        writer = csvwriter(output)
        if sendWithHeader:
            writer.writerow(self.get_header_row())
        writer.writerow(csvdata)
        csv = output.getvalue()
        if six.PY3:
            csv = csv.encode("utf-8")
        now = DateTime().ISO().replace(" ", "-").replace(":", "")
        filename = "formdata_{0}.csv".format(now)
        # Set MIME type of attachment to 'application' so that it will be encoded with base64
        attachments.append((filename, "application/csv", "utf-8", csv))
    if sendXLSX:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        if sendWithHeader:
            ws.append(self.get_header_row())
        ws.append(csvdata)
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            output = tmp.read()
        now = DateTime().ISO().replace(" ", "-").replace(":", "")
        filename = "formdata_{0}.xlsx".format(now)
        attachments.append(
            (
                filename,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "utf-8",
                output
            )
        )
    if sendXML:
        # use ET.write to get a proper XML Header line
        output = BytesIO()
        doc = ET.ElementTree(xmlRoot)
        doc.write(output, encoding="utf-8", xml_declaration=True)
        xmlstr = output.getvalue()
        now = DateTime().ISO().replace(" ", "-").replace(":", "")
        filename = "formdata_{0}.xml".format(now)
        # Set MIME type of attachment to 'application' so that it will be encoded with base64
        attachments.append((filename, "application/xml", "utf-8", xmlstr))
    return attachments

from plone.app.event.base import spell_date

@property
def header_string(self):
    start, end = self._start_end
    start_dict = spell_date(start, self.context) if start else None
    end_dict = spell_date(end, self.context) if end else None

    mode = self.mode
    main_msgid = None
    sub_msgid = None
    if mode == "all":
        main_msgid = _("all_events", default="All events")

    elif mode == "past":
        main_msgid = _("past_events", default="Past events")

    elif mode == "future":
        main_msgid = _("future_events", default="Future events")

    elif mode == "now":
        main_msgid = _("todays_upcoming_events", default="Todays upcoming events")

    elif mode == "today":
        main_msgid = _("todays_events", default="Todays events")

    elif mode == "7days":
        main_msgid = _("7days_events", default="Events in next 7 days.")
        sub_msgid = _(
            "events_from_until",
            default="${from} until ${until}.",
            mapping={
                "from": "%s, %s. %s %s"
                % (
                    start_dict["wkday_name"],
                    start.day,
                    start_dict["month_name"],
                    start.year,
                ),
                "until": "%s, %s. %s %s"
                % (
                    end_dict["wkday_name"],
                    end.day,
                    end_dict["month_name"],
                    end.year,
                ),
            },
        )

    elif mode == "day":
        main_msgid = _(
            "events_on_day",
            default="Events on ${day}",
            mapping={
                "day": "%s, %s. %s %s"
                % (
                    start_dict["wkday_name"],
                    start.day,
                    start_dict["month_name"],
                    start.year,
                ),
            },
        )

    elif mode == "week":
        main_msgid = _(
            "events_in_week",
            default="Events in week ${weeknumber}",
            mapping={"weeknumber": start.isocalendar()[1]},
        )
        sub_msgid = _(
            "events_from_until",
            default="${from} until ${until}.",
            mapping={
                "from": "%s, %s. %s %s"
                % (
                    start_dict["wkday_name"],
                    start.day,
                    start_dict["month_name"],
                    start.year,
                ),
                "until": "%s, %s. %s %s"
                % (
                    end_dict["wkday_name"],
                    end.day,
                    end_dict["month_name"],
                    end.year,
                ),
            },
        )

    elif mode == "month":
        main_msgid = _(
            "events_in_month",
            default="Events in ${month} ${year}",
            mapping={
                "month": start_dict["month_name"],
                "year": start.year,
            },
        )

    trans = self.context.translate
    return {
        "main": trans(main_msgid) if main_msgid else "",
        "sub": trans(sub_msgid) if sub_msgid else "",
    }

def resultsFolder(self, **kwargs):
    """Return a content listing based result set with contents of the
    folder.

    :param **kwargs: Any keyword argument, which can be used for catalog
                        queries.
    :type  **kwargs: keyword argument

    :returns: plone.app.contentlisting based result set.
    :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
            sequence.
    """
    # Extra filter
    kwargs.update(self.request.get("contentFilter", {}))
    if "object_provides" not in kwargs:  # object_provides is more specific
        kwargs.setdefault("portal_type", self.friendly_types)
    kwargs.setdefault("exclude_from_nav", False)  # Añadido
    kwargs.setdefault("batch", True)
    kwargs.setdefault("b_size", self.b_size)
    kwargs.setdefault("b_start", self.b_start)
    kwargs.setdefault("orphan", 1)

    listing = aq_inner(self.context).restrictedTraverse("@@folderListing", None)
    if listing is None:
        return []
    results = listing(**kwargs)
    return results

def _validate(self, value):
    # Pass all validations during initialization
    if self._init_field:
        return
    super(Choice, self)._validate(value)
    vocabulary = self._resolve_vocabulary(value)

    if value not in vocabulary:
        try:
            vocabulary.query['path']['query'] = '/'.join(api.portal.get().getPhysicalPath())
        except:
            raise ConstraintNotSatisfied(
                value, self.__name__
            ).with_field_and_value(self, value)

    if value not in vocabulary:
        raise ConstraintNotSatisfied(
            value, self.__name__
        ).with_field_and_value(self, value)


def display_link(self):
    """Format the url for display"""

    url = self.url()
    if "resolveuid" in url:
        uid = url.split("/")[-1]
        obj = uuidToObject(uid)
        if obj:
            title = obj.Title()
            # Generar correctamente el enlace para tener en cuenta los mountpoints
            # meta ="/".join(obj.getPhysicalPath()[2:])
            meta = "/".join(obj.getPhysicalPath()[len(api.portal.get().getPhysicalPath()):])
            if not meta.startswith("/"):
                meta = "/" + meta
            return {
                "title": title,
                "meta": meta,
            }

    parsed = urlparse(url)
    if parsed.scheme == "mailto":
        return {
            "title": parsed.path,
            "meta": "",
        }

    return {
        "title": url,
        "meta": "",
    }

def absolute_target_url(self):
    """Compute the absolute target URL."""
    url = self.url()

    if self._url_uses_scheme(NON_RESOLVABLE_URL_SCHEMES):
        # For non http/https url schemes, there is no path to resolve.
        return url

    if url.startswith("."):
        # we just need to adapt ../relative/links, /absolute/ones work
        # anyway -> this requires relative links to start with ./ or
        # ../
        context_state = self.context.restrictedTraverse("@@plone_context_state")
        url = "/".join([context_state.canonical_object_url(), url])
    else:
        if "resolveuid" in url:
            uid = url.split("/")[-1]
            obj = uuidToObject(uid)
            if obj:
                # Generar correctamente el enlace para tener en cuenta los mountpoints
                # url = "/".join(obj.getPhysicalPath()[2:])
                # if not url.startswith("/"):
                #     url = "/" + url
                url = obj.absolute_url()

        if not url.startswith(("http://", "https://")):
            url = self.request["SERVER_URL"] + url

    return url


from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from collective.easyform.actions import DummyFormView
from collective.easyform.api import OrderedDict
from collective.easyform.api import dollar_replacer
from collective.easyform.api import filter_fields
from collective.easyform.api import filter_widgets
from collective.easyform.api import lnbr
from plone.app.textfield.value import RichTextValue


def get_mail_body(self, unsorted_data, request, context):
    """Returns the mail-body with footer."""
    schema = get_schema(context)

    form = DummyFormView(context, request)
    form.schema = schema
    form.prefix = "form"
    form._update()
    widgets = filter_widgets(self, form.w)

    # Añadido para corregir los campos de tipo richtext
    for k, v in unsorted_data.items():
        if isinstance(v, RichTextValue):
            unsorted_data.update({k: v.raw})

    data = filter_fields(self, schema, unsorted_data)

    bodyfield = self.body_pt

    # pass both the bare_fields (fgFields only) and full fields.
    # bare_fields for compatability with older templates,
    # full fields to enable access to htmlValue
    if isinstance(self.body_pre, six.string_types):
        body_pre = self.body_pre
    else:
        body_pre = self.body_pre.output

    if isinstance(self.body_post, six.string_types):
        body_post = self.body_post
    else:
        body_post = self.body_post.output

    if isinstance(self.body_footer, six.string_types):
        body_footer = self.body_footer
    else:
        body_footer = self.body_footer.output

    extra = {
        "data": data,
        "fields": OrderedDict([(i, j.title) for i, j in getFieldsInOrder(schema)]),
        "widgets": widgets,
        "mailer": self,
        "body_pre": body_pre and lnbr(dollar_replacer(body_pre, data)),
        "body_post": body_post and lnbr(dollar_replacer(body_post, data)),
        "body_footer": body_footer and lnbr(dollar_replacer(body_footer, data)),
    }
    template = ZopePageTemplate(self.__name__)
    template.write(bodyfield)
    template = template.__of__(context)
    return template.pt_render(extra_context=extra)


def render_ALV(self):
    return self.index()


from plone.app.multilingual.browser.viewlets import _cache_until_catalog_change
from plone.app.multilingual.interfaces import ITranslationManager
from plone.memoize import ram


@ram.cache(_cache_until_catalog_change)
def get_alternate_languages(self):
    """Cache relative urls only. If we have multilingual sites
    and multi domain site caching absolute urls will result in
    very inefficient caching. Build absolute url in template.
    """
    tm = ITranslationManager(self.context)
    catalog = getToolByName(self.context, "portal_catalog")
    results = catalog(TranslationGroup=tm.query_canonical())
    registry_tool = getToolByName(self, "portal_registry")
    default_language = registry_tool['plone.default_language']

    alternates = []
    default_url = self.context.absolute_url()

    for item in results:
        url = item.getURL()
        if item.Language == default_language:
            default_url = url
        alternates.append(
            {
                "lang": item.Language,
                "url": url,
            }
        )

    alternates.append(
        {
            "lang": "x-default",
            "url": default_url,
        }
    )

    return alternates

from plone.app.layout.navigation.root import getNavigationRoot

def get_base_path(self, context):
    path = getNavigationRoot(context)
    if path.endswith('/ca') or path.endswith('/es') or path.endswith('/en'):
        return '/'.join(getNavigationRoot(context).split('/')[:-1])
    else:
        return path


from datetime import datetime
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.event.base import _prepare_range
from plone.app.event.base import construct_calendar
from plone.app.event.base import expand_events
from plone.app.event.base import get_events
from plone.app.event.base import localized_today
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import start_end_query
from plone.event.interfaces import IEventAccessor
from plone.app.querystring import queryparser

@property
def cal_data(self):
    """Calendar iterator over weeks and days of the month to display."""
    context = aq_inner(self.context)
    today = localized_today(context)
    year, month = self.year_month_display()
    monthdates = [dat for dat in self.cal.itermonthdates(year, month)]

    start = monthdates[0]
    end = monthdates[-1]

    data = self.data
    query = {}
    if data.state:
        query["review_state"] = data.state

    events = []
    query.update(self.request.get("contentFilter", {}))
    if ISyndicatableCollection and ISyndicatableCollection.providedBy(
        self.search_base
    ):
        # Whatever sorting is defined, we're overriding it.
        query = queryparser.parseFormquery(
            self.search_base,
            self.search_base.query,
            sort_on="start",
            sort_order=None,
        )

        # restrict start/end with those from query, if given.
        try:
            if "start" in query and query["start"] > start:
                start = query["start"]
        except:
            if "start" in query:
                fixStart = datetime.strptime(query["start"]['query'].Date(), '%Y/%m/%d').date()
                start = fixStart if fixStart > start else start

        try:
            if "end" in query and query["end"] < end:
                end = query["end"]
        except:
            if "end" in query:
                fixEnd = datetime.strptime(query["end"]['query'].Date(), '%Y/%m/%d').date()
                end = fixStart if fixEnd < end else end

        start, end = _prepare_range(self.search_base, start, end)
        query.update(start_end_query(start, end))
        events = self.search_base.results(
            batch=False, brains=True, custom_query=query
        )
        events = expand_events(
            events,
            ret_mode=RET_MODE_OBJECTS,
            start=start,
            end=end,
            sort="start",
            sort_reverse=False,
        )
    else:
        if self.search_base_path:
            query["path"] = {"query": self.search_base_path}
        events = get_events(
            context,
            start=start,
            end=end,
            ret_mode=RET_MODE_OBJECTS,
            expand=True,
            **query,
        )

    cal_dict = construct_calendar(events, start=start, end=end)

    # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
    caldata = [[]]
    for dat in monthdates:
        if len(caldata[-1]) == 7:
            caldata.append([])
        date_events = None
        isodat = dat.isoformat()
        if isodat in cal_dict:
            date_events = cal_dict[isodat]

        events_string_list = []
        if date_events:
            for occ in date_events:
                accessor = IEventAccessor(occ)
                location = accessor.location
                whole_day = accessor.whole_day
                time = accessor.start.time().strftime("%H:%M")
                # TODO: make 24/12 hr format configurable
                events_string_list.append(
                    "{}{}{}{}".format(
                        accessor.title,
                        f" {time}" if not whole_day else "",
                        ", " if not whole_day and location else "",
                        f" {location}" if location else "",
                    )
                )

        caldata[-1].append(
            {
                "date": dat,
                "day": dat.day,
                "prev_month": dat.month < month,
                "next_month": dat.month > month,
                "today": dat.year == today.year
                and dat.month == today.month
                and dat.day == today.day,
                "date_string": f"{dat.year}-{dat.month}-{dat.day}",
                "events_string": " | ".join(events_string_list),
                "events": date_events,
            }
        )
    return caldata


