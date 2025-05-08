# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.PortalTransforms.transforms.safe_html import CSS_COMMENT
from Products.PortalTransforms.transforms.safe_html import decode_htmlentities

from plone.app.event.base import RET_MODE_BRAINS
from plone.app.event.base import _get_compare_attr
from plone.app.event.base import _obj_or_acc
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IRecurrenceSupport
from Products.PlonePAS.utils import safe_unicode
from plone import api
from collective.easyform import config


def gw_expend_events(events, ret_mode, start=None, end=None, sort=None, sort_reverse=None):
    """Expand to the recurrence occurrences of a given set of events.

    :param events: IEvent based objects or IEventAccessor object wrapper.

    :param ret_mode: Return type of search results. These options are
                     available:

                         * 2 (objects): Return results as IEvent and/or
                                        IOccurrence objects.
                         * 3 (accessors): Return results as IEventAccessor
                                          wrapper objects.
                     Option "1" (brains) is not supported.

    :type ret_mode: integer [2|3]

    :param start: Date, from which on events should be expanded.
    :type start: Python datetime.

    :param end: Date, until which events should be expanded.
    :type end: Python datetime

    :param sort: Object or IEventAccessor Attribute to sort on.
    :type sort: string

    :param sort_reverse: Change the order of the sorting.
    :type sort_reverse: boolean
    """
    assert ret_mode is not RET_MODE_BRAINS

    exp_result = []
    for it in events:
        obj = it.getObject() if getattr(it, "getObject", False) else it
        if IEventRecurrence.providedBy(obj) and obj.recurrence:
            occ_list = list(IRecurrenceSupport(obj).occurrences(start, end))
            # add original event (to make expand_events not remove one item of the original list)
            try:
                if (start or end) and (obj.start >= (end or start)):
                    if obj not in occ_list:
                        occ_list.append(obj)
            except:
                if DateTime(str(start or end)) and (DateTime(str(obj.start)) >= (DateTime(str(end or start)))):
                    if obj not in occ_list:
                        occ_list.append(obj)

            occurrences = [_obj_or_acc(occ, ret_mode) for occ in occ_list]
        elif IEvent.providedBy(obj):
            occurrences = [_obj_or_acc(obj, ret_mode)]
        else:
            # No IEvent based object. Could come from a collection.
            continue
        exp_result += occurrences
    if sort:
        exp_result.sort(key=lambda x: _get_compare_attr(x, sort))
    if sort_reverse:
        exp_result.reverse()
    return exp_result


def gw_hasScript(s):
    """Dig out evil Java/VB script inside an HTML attribute.
    >>> hasScript(
    ...     'data:text/html;'
    ...     'base64,PHNjcmlwdD5hbGVydCgidGVzdCIpOzwvc2NyaXB0Pg==')
    True
    >>> hasScript('script:evil(1);')
    True
    >>> hasScript('expression:evil(1);')
    True
    >>> hasScript('expression/**/:evil(1);')
    True
    >>> hasScript('http://foo.com/ExpressionOfInterest.doc')
    False
    """
    s = decode_htmlentities(s)
    s = s.replace('\x00', '')
    s = CSS_COMMENT.sub('', s)
    s = ''.join(s.split()).lower()
    # for t in ('script:', 'expression:', 'expression(', 'data:'):
    for t in ('script:', 'expression:', 'expression('):
        if t in s:
            return True
    return False





def gw_default_mail_body():
    """Default mail body for mailer action.
    Acquire 'mail_body_default.pt' or return hard coded default
    """
    
    import pkg_resources
    content = pkg_resources.resource_string(
        'genweb6.core', 
        'templates/mail_body_default.pt'
    )
    GW_MAIL_BODY_DEFAULT = safe_unicode(content)

    try:
        portal = api.portal.get()
    except api.exc.CannotGetPortalError:
        return GW_MAIL_BODY_DEFAULT

    mail_body_default = portal.restrictedTraverse(
        "easyform_mail_body_default.pt", default=None
    )
    if mail_body_default:
        return safe_unicode(mail_body_default.file.data)
    else:
        return GW_MAIL_BODY_DEFAULT