# -*- coding: UTF-8 -*-
# Copyright 2009-2012 Luc Saffre
# License: BSD (see file COPYING for details)

u"""
Projects
--------

Adds tables Project and ProjectType

"""

from django.db import models
from django.utils.translation import ugettext as _

from lino.api import dd
from lino import mixins
from lino.modlib.users.mixins import ByUser, UserAuthored


class ProjectType(mixins.BabelNamed):

    class Meta:
        verbose_name = _("Project Type")
        verbose_name_plural = _("Project Types")


class ProjectTypes(dd.Table):
    model = ProjectType
    order_by = ["name"]

#
# PROJECT
#


class Project(UserAuthored, mixins.CachedPrintable):

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    name = models.CharField(max_length=200)
    type = models.ForeignKey(ProjectType, blank=True, null=True)
    started = models.DateField(blank=True, null=True)
    stopped = models.DateField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

#~ class ProjectDetail(layouts.FormLayout):
    #~ datalink = 'projects.Project'
    #~ main = """
    #~ name type
    #~ started stopped
    #~ text
    #~ """


class Projects(dd.Table):
    model = 'projects.Project'
    order_by = ["name"]
    #~ button_label = _("Projects")
    detail_layout = """
    name type user
    started stopped
    text
    """


class MyProjects(Projects, ByUser):
    pass


