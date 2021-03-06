# -*- coding: UTF-8 -*-
# Copyright 2008-2015 Luc Saffre
# License: BSD (see file COPYING for details)

"""The database models and tables for :mod:`lino.modlib.countries`.

.. autosummary::

"""
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.conf import settings

from lino import dd, mixins
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

config = dd.plugins.countries

from .choicelists import PlaceTypes, CountryDrivers


FREQUENT_COUNTRIES = ['BE', 'NL', 'DE', 'FR', 'LU']
"""A list of frequent countries used by some demo fixtures."""


class Country(mixins.BabelNamed):
    """A "country" or "nation".
    """

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    isocode = models.CharField(
        max_length=4, primary_key=True,
        verbose_name=_("ISO code"),
        help_text=_("""\
        The two-letter code for this country as defined by ISO 3166-1.
        For countries that no longer exist it may be a 4-letter code."""))
    #~ name = models.CharField(max_length=200)
    #~ name = d.BabelCharField(max_length=200,verbose_name=_("Designation"))

    short_code = models.CharField(
        max_length=4, blank=True,
        verbose_name=_("Short code"),
        help_text=_("""A short abbreviation for regional usage. Obsolete."""))

    iso3 = models.CharField(
        max_length=3, blank=True,
        verbose_name=_("ISO-3 code"),
        help_text=_("The three-letter code for this country "
                    "as defined by ISO 3166-1."))

    def allowed_city_types(self):
        cd = getattr(CountryDrivers, self.isocode, None)
        if cd is not None:
            return cd.region_types + cd.city_types
        return PlaceTypes.items()


class Countries(dd.Table):

    """The table of all countries."""

    help_text = _("""
    A country is a geographic entity considered a "nation".
    """)
    #~ label = _("Countries")
    model = 'countries.Country'
    required = dd.Required(user_groups='office')
    order_by = ["name", "isocode"]
    column_names = "name isocode *"
    detail_layout = """
    isocode name short_code
    countries.PlacesByCountry
    """


class Place(mixins.BabelNamed):
    """Any kind of named geographic region (except those who have an entry
    in :class:`Country`.

    """
    class Meta:
        verbose_name = _("Place")
        verbose_name_plural = _("Places")
        if not settings.SITE.allow_duplicate_cities:
            unique_together = (
                'country', 'parent', 'name', 'type', 'zip_code')

    country = models.ForeignKey('countries.Country')
    zip_code = models.CharField(max_length=8, blank=True)
    type = PlaceTypes.field(blank=True)
    parent = models.ForeignKey(
        'self',
        blank=True, null=True,
        verbose_name=_("Part of"),
        help_text=_("The superordinate geographic place \
        of which this place is a part."))

    #~ def __unicode__(self):
        #~ return self.name

    def get_parents(self, *grandparents):
        if self.parent_id:
            return self.parent.get_parents(self, *grandparents)
        return [self] + list(grandparents)

    @dd.chooser()
    def type_choices(cls, country):
        if country is not None:
            allowed = country.allowed_city_types()
            return [(i, t) for i, t in PlaceTypes.choices if i in allowed]
        return PlaceTypes.choices

    # def __unicode__(self):
    def get_choices_text(self, request, actor, field):
        """
        Extends the default behaviour (which would simply diplay this
        city in the current language) by also adding the name in other
        languages and the type between parentheses.
        """
        names = [self.name]
        for lng in settings.SITE.BABEL_LANGS:
            #~ n = getattr(self,'name_'+lng)
            n = getattr(self, 'name' + lng.suffix)
            if n and not n in names:
                names.append(n)
                #~ s += ' / ' + n
        if len(names) == 1:
            s = names[0]
        else:
            s = ' / '.join(names)
            # s = "%s (%s)" % (names[0], ', '.join(names[1:]))
        if True:  # TODO: attribute per type?
            s += " (%s)" % unicode(self.type)
        return s
        #~ return unicode(self)

    @classmethod
    def get_cities(cls, country):
        if country is None:
            cd = None
            flt = models.Q()
        else:
            cd = getattr(CountryDrivers, country.isocode, None)
            flt = models.Q(country=country)

        #~ types = [PlaceTypes.blank_item] 20120829
        types = [None]
        if cd:
            types += cd.city_types
            #~ flt = flt & models.Q(type__in=cd.city_types)
        else:
            types += [v for v in PlaceTypes.items() if v.value >= '50']
            #~ flt = flt & models.Q(type__gte=PlaceTypes.get_by_value('50'))
        flt = flt & models.Q(type__in=types)
        #~ flt = flt | models.Q(type=PlaceTypes.blank_item)
        return cls.objects.filter(flt).order_by('name')

        #~ if country is not None:
            #~ cd = getattr(CountryDrivers,country.isocode,None)
            #~ if cd:
                #~ return Place.objects.filter(
                    #~ country=country,
                    #~ type__in=cd.city_types).order_by('name')
            #~ return country.place_set.order_by('name')
        #~ return cls.city.field.rel.to.objects.order_by('name')


class Places(dd.Table):
    help_text = _("""
    The table of known geographical places.
    A geographical place can be a city, a town, a suburb,
    a province, a lake... any named geographic entity,
    except for countries because these have their own table.
    """)

    model = 'countries.Place'
    required = dd.Required(user_level='admin', user_groups='office')
    order_by = "country name".split()
    column_names = "country name type zip_code parent *"
    detail_layout = """
    name country
    type parent zip_code id
    PlacesByPlace
    """


class PlacesByPlace(Places):
    label = _("Subdivisions")
    master_key = 'parent'
    column_names = "name type zip_code *"
    # required = dd.Required(user_groups='office')


class PlacesByCountry(Places):
    master_key = 'country'
    column_names = "name type zip_code *"
    required = dd.Required()
    details_of_master_template = _("%(details)s in %(master)s")


