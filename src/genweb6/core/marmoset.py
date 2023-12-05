# -*- coding: utf-8 -*-
from DateTime import DateTime

from plone.app.event.base import RET_MODE_BRAINS
from plone.app.event.base import _get_compare_attr
from plone.app.event.base import _obj_or_acc
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IRecurrenceSupport


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