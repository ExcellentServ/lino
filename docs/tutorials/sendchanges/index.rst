.. _lino.tutorial.sendchanges:

=============================================
Notifying others about database modifications
=============================================

This is a usage example for :mod:`lino.utils.sendchanges`.

General stuff:

>>> from lino.runtime import *
>>> from lino import rt
>>> from django.test.client import Client
>>> import json
>>> client = Client()


In your :xfile:`settings.py` file your override :meth:`do_site_startup
<lino.core.site.Site.do_site_startup>` in a similar way as shown
below.

.. literalinclude:: settings.py

Note that on a real site you will *not* override :meth:`send_email
<lino.core.site.Site.send_email>` as we do here. We do it because we
don't want to actually send emails each time we run our test suite.
Similarily, the :attr:`default_user
<lino.core.site.Site.default_user>` attribute is only here so we don't
need to care about authentication in this tutorial.

Loading demo data
=================

As usual we must load our demo data fixture using Django's standard
loaddata command:

>>> from django.core.management import call_command
>>> call_command('initdb_demo', interactive=False)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
Creating tables ...
Installed 236 object(s) from 10 fixture(s)



Verifying our configuration
===========================

The following tests check whether the setup is as expected:

>>> from lino.utils.sendchanges import find_emitter

Instances of `Partner` and  `Person` get their own emitter:

>>> find_emitter(contacts.Partner.objects.all()[0])
Emitter('contacts.Partner')
>>> find_emitter(contacts.Person.objects.all()[0])
Emitter('contacts.Person')

A `Company` instance gets the emitter for a `Partner`:

>>> find_emitter(contacts.Company.objects.all()[0])
Emitter('contacts.Partner')

A `Country` instance has no emitter:

>>> find_emitter(countries.Country.objects.all()[0])


Templates
=========

Here are the templates used for this tutorial (your own templates
might be more elaborated):

:file:`create_body.eml`

.. literalinclude:: config/created_body.eml

:file:`update_body.eml`

.. literalinclude:: config/updated_body.eml






Simulating a change
===================

Simulate an update from code without a web client.

>>> from lino.core.signals import pre_ui_delete, on_ui_created
>>> from lino.core.utils import ChangeWatcher
>>> request = dd.PseudoRequest("robin")
>>> obj = contacts.Person.objects.all()[0]
>>> cw = ChangeWatcher(obj)
>>> obj.first_name = "XXX"
>>> cw.send_update(request)
To: john@example.com, joe@example.com
Subject: Updated: Mr XXX Altenberg
User Robin Rood has saved these updates:
first_name : Hans --> XXX

But it's more realistic to simulate using web requests.

Create a Person:

>>> url = '/api/contacts/Persons'
>>> data = dict(an='submit_insert', first_name='Joe', last_name='Doe')
>>> res = client.post(url, data=data)
To: john@example.com, joe@example.com
Subject: Created: Joe Doe
User Robin Rood has created this record.
>>> res.status_code
200
>>> r = json.loads(res.content)
>>> print(r['message'])
Person "Joe Doe" has been created.
>>> r['success']
True

Create an organization:

>>> url = '/api/contacts/Companies'
>>> data = dict(an='submit_insert', name='Joe Doe\'s pub')
>>> res = client.post(url, data=data)
To: john@example.com, joe@example.com
Subject: Created partner Joe Doe's pub
User Robin Rood has created this record.
>>> res.status_code
200
>>> r = json.loads(res.content)
>>> print(r['message'])
Organization "Joe Doe's pub" has been created.
>>> r['success']
True

