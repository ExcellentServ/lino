# -*- coding: UTF-8 -*-
# Copyright 2011-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""Importing this from within one of your :xfile:`models.py` modules will
add the "Take" action.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


from lino.api import dd, rt

from ..workflows import (TaskStates, EventStates, GuestStates)


class TakeEvent(dd.Action):
    """
    This action means that you declare to become the fully responsible
    user for this event.  Accordingly, this action is available only
    when you are not already fully responsible. You are fully
    responsible when (1) :attr:`Event.user` is set to *you*
    **and** (2) :attr:`Event.assigned_to` is *not empty*.

    Basically anybody can take any event, even if it is not assigned
    to them.

    .. |flag_green| image:: ../../lino/media/extjs/images/mjames/flag_green.png
  
    Represented by a green flag (|flag_green|) button.


    """
    label = _("Take")
    show_in_workflow = True

    #~ icon_file = 'cancel.png'
    icon_name = 'flag_green'
    help_text = _("Take responsibility for this event.")

    def get_action_permission(self, ar, obj, state):
        if obj.user == ar.get_user():
            if obj.assigned_to is None:
                return False
        # elif obj.assigned_to != ar.get_user():
        #     return False
        return super(TakeEvent,
                     self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]

        def ok(ar):
            obj.user = ar.get_user()
            obj.assigned_to = None
            #~ kw = super(TakeEvent,self).run(obj,ar,**kw)
            obj.save()
            ar.set_response(refresh=True)

        ar.confirm(ok, self.help_text, _("Are you sure?"))



@dd.receiver(dd.pre_analyze)
def take_workflows(sender=None, **kw):

    site = sender

    site.modules.cal.Event.take = TakeEvent()
