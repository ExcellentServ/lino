# Copyright 2011-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""Defines the choicelists for :mod:`lino.modlib.users`, i.e.
:class:`UserLevels`, 
:class:`UserGroups` and
:class:`UserProfiles`.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from django.conf import settings


from lino.core.choicelists import ChoiceList, Choice


class UserLevel(Choice):
    short_name = None


class UserLevels(ChoiceList):
    """
    The level of a user is one way of differenciating users when 
    defining access permissions and workflows. 
    
    .. django2rst:: rt.show(users.UserLevels,
                            column_names='value name text')


    """

    verbose_name = _("User Level")
    verbose_name_plural = _("User Levels")
    required = settings.SITE.get_default_required(user_level='admin')
    short_name = models.CharField(
        _("Short name"), max_length=2,
        help_text=_("Used when defining UserProfiles"))

    @classmethod
    def get_column_names(self, ar):
        return 'value name short_name text remark'

    @classmethod
    def field(cls, module_name=None, **kw):
        """
        Extends :meth:`lino.core.fields.ChoiceListField.field` .
        """
        kw.setdefault('blank', True)
        if module_name is not None:
            kw.update(verbose_name=string_concat(
                cls.verbose_name, ' (', module_name, ')'))
        return super(UserLevels, cls).field(**kw)


add = UserLevels.add_item
add('10', _("Guest"), 'guest', short_name='G')
add('30', _("User"), "user", short_name='U')
add('40', _("Manager"), "manager", short_name='M')
add('50', _("Administrator"), "admin", short_name='A')
UserLevels.SHORT_NAMES = dict(
    A='admin', U='user', _=None, M='manager', G='guest')


class UserProfile(Choice):

    hidden_languages = None
    """
    A subset of :setting:`languages`
    which should be hidden in this user profile.
    Default value is :attr:`hidden_languages <UserProfiles.hidden_languages>`.
    This is used on multilingual sites with more than 4 or 5 languages.
    See the source code of :meth:`lino_welfare.settings.Site.setup_user_profiles`
    for a usage example.
    """

    def __init__(self, cls, value, text,
                 name=None, memberships=None, authenticated=True,
                 readonly=False,
                 #~ expert=False,
                 **kw):

        super(UserProfile, self).__init__(value, text, name)
        #~ keys = ['level'] + [g+'_level' for g in choicelist.groups_list]
        #~ keys = ['level'] + [g+'_level' for g in choicelist.membership_keys]
        self.readonly = readonly
        #~ self.expert = expert
        self.authenticated = authenticated
        self.memberships = memberships
        self.kw = kw

    def attach(self, cls):
        super(UserProfile, self).attach(cls)
        self.kw.setdefault('hidden_languages', cls.hidden_languages)
        if self.memberships is None:
            for k in cls.membership_keys:
                #~ kw[k] = UserLevels.blank_item
                #~ kw.setdefault(k,UserLevels.blank_item) 20120829
                self.kw.setdefault(k, None)
        else:
        #~ if memberships is not None:
            if len(self.memberships.split()) != len(cls.membership_keys):
                raise Exception(
                    "Invalid memberships specification %r : "
                    "must contain %d letters"
                    % (self.memberships, len(cls.membership_keys)))
            for i, k in enumerate(self.memberships.split()):
                self.kw[cls.membership_keys[i]
                        ] = UserLevels.get_by_name(UserLevels.SHORT_NAMES[k])

        #~ print 20120705, value, kw

        assert 'level' in self.kw

        for k, vf in cls.virtual_fields.items():
            if vf.has_default():
                self.kw.setdefault(k, vf.get_default())
            elif vf.return_type.blank:
                self.kw.setdefault(k, None)

        for k, v in self.kw.items():
            setattr(self, k, v)

        for k in cls.default_memberships:
            setattr(self, k, self.level)

        if self.hidden_languages is not None:
            self.hidden_languages = set(
                settings.SITE.resolve_languages(self.hidden_languages))

        del self.kw
        del self.memberships

    def __repr__(self):
        #~ s = self.__class__.__name__
        s = str(self.choicelist)
        if self.name:
            s += "." + self.name
        s += ":" + self.value + "("
        #~ s += "level=%s" % self.level.name
        s += "level=%s" % self.level
        for g in UserGroups.items():
            if g.value:  # no level for UserGroups.blank_item
                v = getattr(self, g.value + '_level', None)
                if v is not None:
                    s += ",%s=%s" % (g.value, v.name)
        s += ")"
        return s


class UserProfiles(ChoiceList):
    """The list of user profiles available on this site.
    
    Each user profile is a set of user levels (one for each functional
    group), leading to an individual combination of permissions.
    
    The demo database has defined the following user profiles:

    .. django2rst:: rt.show(users.UserProfiles,
                            column_names='value name text level')

    Note that we show here only the "general" or "system" userlevel.
    Open :menuselection:`Explorer --> System --> User Profiles`
    in your Lino to see all application-specific userlevels.

    """
    required = settings.SITE.get_default_required(user_level='admin')
    #~ item_class = UserProfile
    verbose_name = _("User Profile")
    verbose_name_plural = _("User Profiles")
    show_values = True
    max_length = 20
    membership_keys = ('level',)

    preferred_foreignkey_width = 20

    hidden_languages = settings.SITE.hidden_languages
    """Default value for the :attr:`hidden_languages
    <UserProfile.hidden_languages>` of newly attached choice item.

    """

    level = UserLevels.field(_("System"))

    @classmethod
    def reset(cls, groups=None, hidden_languages=None):
        """
        Deserves a docstring.
        """
        if hidden_languages is not None:
            cls.hidden_languages = hidden_languages
        expected_names = set(
            ['*'] + [g.value for g in UserGroups.items() if g.value])
        if groups is None:
            groups = ' '.join(expected_names)
        s = []
        for g in groups.split():
            if not g in expected_names:
                raise Exception("Unexpected name %r (UserGroups are: %s)" % (
                    g, [g.value for g in UserGroups.items() if g.value]))
            else:
                expected_names.remove(g)
                if g == '*':
                    s.append('level')
                else:
                    if not UserGroups.get_by_value(g):
                        raise Exception("Unknown group %r" % g)
                    s.append(g + '_level')
        #~ if len(expected_names) > 0:
            #~ raise Exception("Missing name(s) %s in %r" % (expected_names,groups))
        cls.default_memberships = expected_names
        cls.membership_keys = tuple(s)
        cls.clear()

    @classmethod
    def add_item(cls, value, text, memberships=None, name=None, **kw):
        return cls.add_item_instance(UserProfile(
            cls, value, text, name, memberships, **kw))

#~ UserProfiles choicelist is going to be filled in `lino.core.site.Site.setup_user_profiles`
#~ because the attributes of each item depend on UserGroups


class UserGroups(ChoiceList):
    """TODO: Rename this to "FunctionalGroups" or sth similar.
    
    Functional Groups are another way of differenciating users when
    defining access permissions and workflows.
    
    Applications can define their functional groups

    """

    required = settings.SITE.get_default_required(user_level='admin')
    verbose_name = _("User Group")
    verbose_name_plural = _("User Groups")
    show_values = True
    max_length = 20
    """
    """

# add = UserGroups.add_item
# add('system', _("System"))
# filled using add_user_group()


