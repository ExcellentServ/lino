# Copyright 2008-2015 Luc Saffre
# License: BSD (see file COPYING for details)

"""Extends `django.contrib.contenttypes`.  This module must be
installed if your models contain GenericForeignKey fields or inherit
from the :class:`Controllable
<lino.modlib.contenttypes.mixins.Controllable>` mixin.

.. autosummary::
   :toctree:

    models
    mixins

"""

from lino import ad


class Plugin(ad.Plugin):
    "See :doc:`/dev/plugins`."

    def setup_reports_menu(config, site, profile, m):
        hook = site.plugins.system
        m = m.add_menu(hook.app_label, hook.verbose_name)
        m.add_action(site.modules.contenttypes.StaleControllables)

    def setup_config_menu(config, site, profile, m):
        hook = site.plugins.system
        m = m.add_menu(hook.app_label, hook.verbose_name)
        m.add_action(site.modules.contenttypes.HelpTexts)

    def setup_explorer_menu(config, site, profile, m):
        hook = site.plugins.system
        m = m.add_menu(hook.app_label, hook.verbose_name)
        m.add_action(site.modules.contenttypes.ContentTypes)



