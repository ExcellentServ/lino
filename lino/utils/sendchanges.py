# Copyright 2010-2015 Luc Saffre
# License: BSD (see file COPYING for details)
"""Send an email to a configurable list of addresses when a
configurable database item has been changed.

Importing this module will add a receiver to the
:attr:`on_ui_created <lino.core.signals.on_ui_created>`,
:attr:`on_ui_updated <lino.core.signals.on_ui_updated>` and
:attr:`pre_ui_delete <lino.core.signals.pre_ui_delete>`
signals.

Usage example (taken from :doc:`/tutorials/sendchanges/index`)::

    class Site(Site):
        title = "sendchanges example"

        def do_site_startup(self):
            super(Site, self).do_site_startup()
            from lino.utils.sendchanges import register, subscribe
            register('contacts.Person', 'first_name last_name birth_date',
                     'created_body.eml', 'updated_body.eml')
            e = register('contacts.Partner', 'name',
                         'created_body.eml', 'updated_body.eml')
            e.updated_subject = "Change in partner {master}"
            subscribe('john.doe@example.org')


Note that the order of subscription is important when the watched
models inherit from each other: for a given model instance, the first
matching subscription will be used.

"""

import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.utils.translation import ugettext as _

from lino import rt
from lino.core.signals import receiver
from lino.core.signals import on_ui_created, on_ui_updated, pre_ui_delete
from lino.core.fields import fields_list
from lino.core.dbutils import resolve_model
from lino.core.dbutils import full_model_name as fmn

SUBSCRIPTIONS = []
EMITTERS = []


class Emitter(object):
    """
    The object returned by :func:`register`.

    """
    created_tpl = None
    update_tpl = None
    delete_tpl = None
    created_subject = _("Created: {obj}")
    updated_subject = _("Updated: {obj}")
    deleted_subject = _("Deleted: {obj}")
    master_field = None

    def __init__(self, model, watched_fields,
                 created_tpl=None, update_tpl=None, delete_tpl=None,
                 master_field=None):
        """`model` is either a class object or a string with the global name
        of a model (e.g. ``'contacts.Person'``). `watched_fields` is a
        string with a space-separated list of field names to watch.
        `master_field` can optionally specify a field which points to
        the "master".

        """
        self.model = resolve_model(model, strict=True)
        self.watched_fields = fields_list(self.model, watched_fields)
        if master_field:
            self.master_field = master_field
        if created_tpl:
            self.created_tpl = rt.get_template(created_tpl)
        if update_tpl:
            self.update_tpl = rt.get_template(update_tpl)
        if delete_tpl:
            self.delete_tpl = rt.get_template(delete_tpl)

    def __repr__(self):
        return "Emitter('{0}')".format(fmn(self.model))

    def get_master(self, obj):
        if self.master_field is None:
            return None
        return getattr(obj, self.master_field)

    def emit_created(self, request, obj, **context):
        """Send "created" mails for the given model instance `obj`."""
        if self.created_tpl:
            context.update(obj=obj)
            context.update(master=self.get_master(obj))
            subject = self.created_subject.format(**context)
            self.sendmails(request, subject, self.created_tpl, **context)

    def emit_updated(self, request, cw, **context):
        """Send "updated" mails for the given ChangeWatcher `cw`."""
        if not self.update_tpl:
            return
        updates = list(cw.get_updates(watched_fields=self.watched_fields))
        if len(updates) == 0:
            logger.info("20150112 no updates for %s", cw)
            return
        context.update(obj=cw.watched)
        context.update(master=self.get_master(cw.watched))
        context.update(old=cw.original_state)
        context.update(updates=updates)
        subject = self.updated_subject.format(**context)
        self.sendmails(request, subject, self.update_tpl, **context)
        
    def emit_deleted(self, request, obj, **context):
        """Send "deleted" mails for the given model instance `obj`."""
        if self.delete_tpl:
            context.update(obj=obj)
            context.update(master=self.get_master(obj))
            subject = self.deleted_subject.format(**context)
            self.sendmails(request, subject, self.delete_tpl, **context)

    def sendmails(self, request, subject, template, **context):
        # logger.info("body template %s, template)
        context.update(request=request)
        body = template.render(**context)
        sender = request.user.email or settings.SERVER_EMAIL
        rt.send_email(subject, sender, body, SUBSCRIPTIONS)


def subscribe(addr):
    """Subscribe the given email address for getting notified about
    changes.

    """
    SUBSCRIPTIONS.append(addr)


def register(*args, **kwargs):
    """Register an :class:`Emitter` for the given model. `args` and
    `kwargs` are forwarded to :meth:`Emitter.__init__`.

    """
    sub = Emitter(*args, **kwargs)
    EMITTERS.append(sub)
    return sub


def find_emitter(obj):
    """Return the registered subscription for the given model instance."""
    # return SUBSCRIPTIONS.get(obj.__class__)
    for e in EMITTERS:
        if isinstance(obj, e.model):
            return e


@receiver(on_ui_created)
def on_created(sender=None, request=None, **kw):
    # sender is a model instance
    s = find_emitter(sender)
    if s is not None:
        s.emit_created(request, sender)


@receiver(on_ui_updated)
def on_updated(sender=None, request=None, **kw):
    # sender is a ChangeWatcher
    s = find_emitter(sender.watched)
    if s is not None:
        s.emit_updated(request, sender)


@receiver(pre_ui_delete)
def on_deleted(sender=None, request=None, **kw):
    # sender is a model instance
    s = find_emitter(sender)
    if s is not None:
        s.emit_deleted(request, sender)

