# -*- coding: UTF-8 -*-
# Copyright 2013-2015 Luc Saffre
# License: BSD (see file COPYING for details)

"""Adds feedback-based workflow to :mod:`lino.modlib.cal`. You
"activate" this by simply importing it from within a
:xfile:`models.py` used by your application.

Used e.g. by :ref:`welfare`.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from lino.api import dd

from lino.modlib.cal.workflows import EventStates, GuestStates

add = EventStates.add_item
add('40', _("Published"), 'published', edit_guests=True)


if True:
    add = GuestStates.add_item
    add('20', _("Accepted"), 'accepted')
    add('30', _("Rejected"), 'rejected')
    add('40', _("Present"), 'present', afterwards=True)
    add('50', _("Absent"), 'absent', afterwards=True)
    add('60', _("Excused"), 'excused', afterwards=True)


class InvitationFeedback(dd.ChangeStateAction, dd.NotifyingAction):

    def get_action_permission(self, ar, obj, state):
        if obj.partner_id is None:
            return False
        if obj.event.state != EventStates.published:
            return False
        return super(InvitationFeedback,
                     self).get_action_permission(ar, obj, state)

    def get_notify_subject(self, ar, obj):
        return self.notify_subject % dict(
            guest=obj.partner,
            day=dd.fds(obj.event.start_date),
            time=str(obj.event.start_time))


class RejectInvitation(InvitationFeedback):
    label = _("Reject")
    help_text = _("Reject this invitation.")
    required = dict(states='invited accepted')  # ,owner=False)
    notify_subject = _(
        "%(guest)s cannot accept invitation %(day)s at %(time)s")


class AcceptInvitation(InvitationFeedback):
    label = _("Accept")
    help_text = _("Accept this invitation.")
    required = dict(states='invited rejected')  # ,owner=False)
    notify_subject = _("%(guest)s confirmed invitation %(day)s at %(time)s")


@dd.receiver(dd.pre_analyze)
def my_guest_workflows(sender=None, **kw):
    """
    A Guest can be marked absent or present only for events that took place
    """
    def event_took_place(action, user, obj, state):
        return obj.event_id and (obj.event.state == EventStates.took_place)

    GuestStates.rejected.add_transition(AcceptInvitation)
    GuestStates.rejected.add_transition(RejectInvitation)
    GuestStates.present.add_transition(
        states='invited accepted',  # owner=True,
        allow=event_took_place)
    GuestStates.absent.add_transition(states='invited accepted',  # owner=True,
                                      allow=event_took_place)


class ResetEvent(dd.ChangeStateAction):
    label = _("Reset")
    icon_name = 'cancel'
    required = dict(states='published took_place')


class CloseMeeting(dd.ChangeStateAction):
    label = _("Close meeting")
    help_text = _("The event took place.")
    icon_name = 'emoticon_smile'
    required = dict(states='published draft')


@dd.receiver(dd.pre_analyze)
def my_event_workflows(sender=None, **kw):

    EventStates.published.add_transition(  # _("Confirm"),
        states='suggested draft',
        icon_name='accept',
        help_text=_("Mark this as published. "
                    "All participants have been informed."))
    EventStates.took_place.add_transition(CloseMeeting, name='close_meeting')
    EventStates.cancelled.add_transition(
        pgettext("calendar event action", "Cancel"),
        states='published draft',
        icon_name='cross')
    EventStates.draft.add_transition(ResetEvent)


