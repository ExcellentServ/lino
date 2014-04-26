# -*- coding: UTF-8 -*-
# Copyright 2012-2014 Luc Saffre
# This file is part of the Lino project.
# Lino is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with Lino; if not, see <http://www.gnu.org/licenses/>.
"""
The `demo` fixture for `households`
===================================

Creates some households by marrying a few Persons.

"""

from lino.core.dbutils import resolve_model


from lino.utils import Cycler
from lino import dd


def objects():

    # Role = resolve_model('households.Role')
    # Member = resolve_model('households.Member')
    # Household = resolve_model('households.Household')
    Person = resolve_model('contacts.Person')
    Type = resolve_model('households.Type')

    MEN = Cycler(Person.objects.filter(gender=dd.Genders.male)
                 .order_by('-id'))
    WOMEN = Cycler(Person.objects.filter(gender=dd.Genders.female)
                   .order_by('-id'))
    TYPES = Cycler(Type.objects.all())

    ses = dd.login()
    for i in range(5):
        pv = dict(
            head=MEN.pop(), partner=WOMEN.pop(),
            type=TYPES.pop())
        ses.run(
            Person.create_household,
            action_param_values=pv)
        # yield ses.response['data_record']
        # he = MEN.pop()
        # she = WOMEN.pop()
        
        # fam = Household(name=he.last_name + "-" + she.last_name, type_id=3)
        # yield fam
        # yield Member(household=fam, person=he, role=Role.objects.get(pk=1))
        # yield Member(household=fam, person=she, role=Role.objects.get(pk=2))

    return []
