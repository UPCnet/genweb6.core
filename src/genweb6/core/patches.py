# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from BTrees.OOBTree import OOBTree
from Products.CMFCore.MemberDataTool import MemberAdapter as BaseMemberAdapter
from Products.CMFCore.permissions import ManageUsers
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.syndication.adapters import BaseItem
from Products.CMFPlone.browser.syndication.adapters import FolderFeed
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces import ISocialMediaSchema
from Products.CMFPlone.interfaces.syndication import IFeedItem
from Products.CMFPlone.utils import getSiteLogo
from Products.LDAPUserFolder.LDAPUser import LDAPUser
from Products.LDAPUserFolder.LDAPUser import NonexistingUser
from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet
from Products.PlonePAS.utils import safe_unicode
from Products.PluggableAuthService.events import PropertiesUpdated
from Products.PluggableAuthService.interfaces.authservice import IPluggableAuthService

from io import StringIO
from plone import api
from plone.app.content.interfaces import INameFromTitle
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.textfield.value import IRichTextValue
from plone.app.users.browser.interfaces import IUserIdGenerator
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from urllib.parse import quote_plus
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.event import notify

from genweb6.core.adapters.portrait import IPortraitUploadAdapter
from genweb6.core.utils import portal_url
from genweb6.core.utils import pref_lang

import logging
import requests
import six
from hashlib import sha1

logger = logging.getLogger('event.LDAPUserFolder')
genweb_log = logging.getLogger('genweb6.core')


def isStringType(data):
    return isinstance(data, str) or isinstance(data, unicode)

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
    item_count = 30
    if hasattr(self.context, 'item_count'):
        item_count = self.context.item_count

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

    # Our LDAP improvements hand the current user id in unicode, but BTree can't
    # handle unicode keys in inner objects... *sigh*
    if isinstance(safe_id, unicode):
        safe_id = str(safe_id)

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
    # portal_membership = api.portal.get_tool(name="portal_membership")  # Se modifico para para hacerlo con la api
    # is_anonymous = bool(portal_membership.isAnonymousUser())
    # if not is_anonymous:
    #     return []

    tags = [
        dict(itemprop="name", content=self.page_title),
        dict(name="twitter:card", content="summary"),
        dict(property="og:site_name", content=self.site_title_setting),
        dict(property="og:title", content=self.page_title),
        dict(property="twitter:title", content=self.page_title),  # Añadido
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

    tags.extend(
        [
            dict(itemprop="description", content=item.description),
            dict(itemprop="url", content=item.link),
            dict(property="og:description", content=item.description),
            dict(property="twitter:description", content=item.description),  # Añadido
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
                dict(property="twitter:image", content=url),  # Added
                dict(itemprop="image", content=url),
                dict(property="og:image:type", content="image/png"),
            ]
        )
    return tags
