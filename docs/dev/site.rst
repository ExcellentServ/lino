===================================
Introducing the :class:`Site` class
===================================

.. This document is part of the Lino test suite. You can test only
   this document using::

    $ python setup.py test -s tests.DocsTests.test_site

.. currentmodule:: lino.core.site

The :class:`Site` is the base class for representing a "Lino
application" (and we suppose that you have read :doc:`application`).
This concept brings an additional level of encapsulation to Django.  A
:class:`Site` *class* is a kind of a "project template".

A `Site` has attributes like :attr:`Site.verbose_name` (the "short"
user-visible name) and the :attr:`Site.version` which are used by the
method :meth:`Site.welcome_text`.  It also defines a
:meth:`Site.startup` method and signals which fire exactly once when
the application starts up.

And then it is designed to be subclassed by the application developer
(e.g. :class:`lino.projects.min1.settings.Site`), then imported into a
local :xfile:`settings.py`, where a local system administrator may
subclass it another time.

A Lino application starts to "live" when such a :class:`Site` class
gets **instantiated**.  This instance of your application is then
stored in the :setting:`SITE` variable of a local
:xfile:`settings.py`.

Unlike most other Django settings, :setting:`SITE` contains a *Python
object* which has methods that can be called by application code at
runtime.


Instantiating a :class:`Site`
=============================

You'll have noticed that the first parameter passed to the
instantiator of a :class:`Site` class is always `globals()
<https://docs.python.org/2/library/functions.html#globals>`__.  This
is the global namespace of your settings module.  And the instantiator
will write into this.

In other words, Lino is going to automatically set certain Django
settings. Including for example :setting:`INSTALLED_APPS` and
:setting:`DATABASES`.  To be precise, here are these settings:

>>> from lino.projects.min1.settings import Site
>>> pseudoglobals = {}
>>> SITE = Site(pseudoglobals)
>>> pseudoglobals.keys()
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
['EMAIL_SUBJECT_PREFIX', 'LOGGING', 'LANGUAGE_CODE',
'MIDDLEWARE_CLASSES', 'LANGUAGES', 'DEBUG', 'USE_L10N',
'ROOT_URLCONF', 'FIXTURE_DIRS', 'INSTALLED_APPS', 'SERVER_EMAIL',
'TEMPLATE_CONTEXT_PROCESSORS', 'SERIALIZATION_MODULES', 'MEDIA_ROOT',
'LOGGING_CONFIG', 'TEMPLATE_LOADERS', 'DATABASES', 'ADMINS',
'DEFAULT_FROM_EMAIL', 'LOCALE_PATHS', 'ALLOWED_HOSTS', 'EMAIL_HOST',
'MEDIA_URL']

A more detailed description of the Django settings managed by Lino is
in :doc:`/ref/settings`.

Note that Lino writes only while the Site class gets instantiated.  So
if for some reason you want to modify one of these settings, do it
*after* instantiating your ``SITE = Site(globals())`` line.




Specifying the :setting:`INSTALLED_APPS`
=========================================

A :class:`Site` is usually meant to work for a given set of Django
apps (i.e. what's in the :setting:`INSTALLED_APPS` setting).  It is a
"collection of apps" which make up a whole.  To define this
collection, the application developper usually overrides the
:meth:`Site.get_installed_apps` method.



Additional local apps
=====================

An optional second positional argument can be specified by local
system administrators in order to specify additional *local apps*
These will go into the :setting:`INSTALLED_APPS` setting (but
:class:`Site` will automatically add some).

>>> from lino.projects.min1.settings import Site
>>> pseudoglobals = {}
>>> Site(pseudoglobals, "lino.modlib.notes")  #doctest: +ELLIPSIS
<lino.projects.min1.settings.Site object at ...>
>>> print('\n'.join(pseudoglobals['INSTALLED_APPS']))
django.contrib.sessions
lino.modlib.about
lino.modlib.extjs
lino.modlib.bootstrap3
lino.modlib.notes
lino
lino.modlib.contenttypes
lino.modlib.system
lino.modlib.users
lino.modlib.countries
lino.modlib.contacts
lino.modlib.cal
lino.modlib.export_excel
lino.modlib.office


As an application developer you won't specifiy this argument,
then you should specify your installed apps by overriding
:meth:`get_installed_apps <lino.core.site.Site.get_installed_apps>`.

Besides this you can override any class argument using a keyword
argment of same name:

- :attr:`lino.core.site.Site.title`
- :attr:`lino.core.site.Site.verbose_name`

You've maybe heard that it is not allowed to modify Django's settings
once it has started.  But there's nothing illegal with this here
because this happens before Django has seen your :xfile:`settings.py`.

Lino does more than this. It will for example read the `__file__
<http://docs.python.org/2/reference/datamodel.html#index-49>`__
attribute of this, to know where your :file:`settings.py` is in the
file system.



Technical details
=================


The following examples use the :class:`TestSite` class just to show
certain things which apply also to "real" Sites.

These are the Django settings which Lino will override:

>>> from django.utils import translation
>>> from lino.core.site import TestSite as Site
>>> from pprint import pprint
>>> pprint(Site().django_settings)
... #doctest: +ELLIPSIS +REPORT_UDIFF +NORMALIZE_WHITESPACE
{'DATABASES': {'default': {'ENGINE': 'django.db.backends.sqlite3',
                           'NAME': '.../default.db'}},
 'FIXTURE_DIRS': (),
 'INSTALLED_APPS': ('lino.modlib.about',
                    'lino.modlib.extjs',
                    'lino.modlib.bootstrap3',
                    'lino'),
 'LANGUAGES': [],
 'LOCALE_PATHS': (),
 'LOGGING': {'disable_existing_loggers': True,
             'filename': None,
             'level': 'INFO',
             'logger_names': 'atelier lino'},
 'LOGGING_CONFIG': 'lino.utils.log.configure',
 'MEDIA_ROOT': 'lino/core/media',
 'MEDIA_URL': '/media/',
 'MIDDLEWARE_CLASSES': ('django.middleware.common.CommonMiddleware',
                        'lino.core.auth.NoUserMiddleware',
                        'lino.utils.ajax.AjaxExceptionResponse'),
 'ROOT_URLCONF': 'lino.core.urls',
 'SECRET_KEY': '20227',
 'SERIALIZATION_MODULES': {'py': 'lino.utils.dpy'},
 'TEMPLATE_CONTEXT_PROCESSORS': ('django.core.context_processors.debug',
                                 'django.core.context_processors.i18n',
                                 'django.core.context_processors.media',
                                 'django.core.context_processors.static'),
 'TEMPLATE_LOADERS': ('lino.core.web.Loader',
                      'django.template.loaders.filesystem.Loader',
                      'django.template.loaders.app_directories.Loader'),
 '__file__': '...'}


Application code usually specifies :attr:`Site.languages` as a single
string with a space-separated list of language codes.  The
:class:`Site` will analyze this string during instantiation and
convert it into a tuple of :data:`LanguageInfo` objects.

>>> SITE = Site(languages="en fr de")
>>> pprint(SITE.languages)
(LanguageInfo(django_code='en', name='en', index=0, suffix=''),
 LanguageInfo(django_code='fr', name='fr', index=1, suffix='_fr'),
 LanguageInfo(django_code='de', name='de', index=2, suffix='_de'))

>>> SITE = Site(languages="de-ch de-be")
>>> pprint(SITE.languages)
(LanguageInfo(django_code='de-ch', name='de_CH', index=0, suffix=''),
 LanguageInfo(django_code='de-be', name='de_BE', index=1, suffix='_de_BE'))

If we have more than one locale of a same language *on a same Site*
(e.g. 'en-us' and 'en-gb') then it is not allowed to specify just
'en'.  But otherwise it is allowed to just say "en", which will mean
"the English variant used on this Site".

>>> site = Site(languages="en-us fr de-be de")
>>> pprint(site.languages)
(LanguageInfo(django_code='en-us', name='en_US', index=0, suffix=''),
 LanguageInfo(django_code='fr', name='fr', index=1, suffix='_fr'),
 LanguageInfo(django_code='de-be', name='de_BE', index=2, suffix='_de_BE'),
 LanguageInfo(django_code='de', name='de', index=3, suffix='_de'))

>>> pprint(site.language_dict)
{'de': LanguageInfo(django_code='de', name='de', index=3, suffix='_de'),
 'de_BE': LanguageInfo(django_code='de-be', name='de_BE', index=2, suffix='_de_BE'),
 'en': LanguageInfo(django_code='en-us', name='en_US', index=0, suffix=''),
 'en_US': LanguageInfo(django_code='en-us', name='en_US', index=0, suffix=''),
 'fr': LanguageInfo(django_code='fr', name='fr', index=1, suffix='_fr')}

>>> pprint(site.django_settings['LANGUAGES'])  #doctest: +ELLIPSIS
[('de', 'German'), ('fr', 'French')]


