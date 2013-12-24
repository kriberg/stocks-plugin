# Copyright (c) 2010-2013 Kristian Berg
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2013-11-09"
__author__ = "vittoros"

import logging

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from ecm.lib import bigintpatch, softfk
from ecm.apps.common import eft
from ecm.plugins.assets.models import Asset
from ecm.apps.eve.models import Type, CelestialObject
from ecm.apps.corp.models import Hangar, Corporation

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Group(models.Model):
    name = models.CharField(max_length=255)
    stationID = models.BigIntegerField()
    hangarID = models.PositiveIntegerField(null=True, blank=True) # hangar division

    def __unicode__(self):
        return u'%s (%s: %s)' % (self.name, self.stationID, self.hangarID)

    def location(self):
        if self.hangarID:
            return '%s, %s' % (self.station(), self.hangar())
        else:
            return self.station()

    def missing_stock(self):
        items = Item.objects.filter(group=self)
        fittings = Fitting.objects.filter(group=self)
        stocks = {}
        for item in items:
            if not item.fully_stocked:
                stocks[item.eve_type.typeName] = u'(%d/%d)' % (item.stock_level,
                        item.desired_level)
        for fitting in fittings:
            if not fitting.fully_stocked:
                stocks[fitting.name] = u'(%d/%d)' % (len(fitting.stock_level),
                        fitting.desired_level)
        return stocks

    def fits(self):
        return Fitting.objects.filter(group=self)

    def items(self):
        return Item.objects.filter(group=self)

    def station(self):
        try:
            return CelestialObject.objects.get(itemID=self.stationID).itemName
        except CelestialObject.DoesNotExist:
            return self.stationID

    def hangar(self):
        try:
            return Hangar.objects.get(hangarID=self.hangarID) \
                    .get_name(Corporation.objects.mine())
        except Hangar.DoesNotExist:
            return self.hangarID

#------------------------------------------------------------------------------
class Item(models.Model):
    group = models.ForeignKey(Group)
    eve_type = softfk.SoftForeignKey(to='eve.Type')
    desired_level = models.BigIntegerField(default=0)

    def __unicode__(self):
        return u'%s (%s)' % (self.eve_type.typeName, self.group.name)

    def stock_level(self):
        items = Asset.objects.filter(eve_type=self.eve_type,
                stationID=self.group.stationID)
        if self.group.hangarID:
            items = items.filter(hangarID=self.group.hangarID)
        aggregated = items.aggregate(models.Sum('quantity'))
        if aggregated['quantity__sum']:
            return aggregated['quantity__sum']
        else:
            return 0

    def fully_stocked(self):
        return self.stock_level() >= self.desired_level


#------------------------------------------------------------------------------
class Fitting(models.Model):
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=255)
    ship_type = softfk.SoftForeignKey(to='eve.Type')
    desired_level = models.IntegerField(default=0)
    eft_export = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    matching_fuzz = models.IntegerField(default=0, help_text='How many \
            modules that can be off when matching.')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.group.name)

    def find_ships(self):
        ships = Asset.objects.filter(eve_type=self.ship_type,
                stationID=self.group.stationID,
                singleton=True)
        if self.group.hangarID:
            ships = ships.filter(hangarID=self.group.hangarID)

        items = self.fitting()
        matching_ships = []
        misfitted_ships = []
        modulecount = 0
        for item, quantity in items:
            modulecount += quantity
        LOG.debug('Found {0} {1}.'.format(ships.count(), self.ship_type))
        for ship in ships:
            contents = Asset.objects.filter(container1=ship.itemID)
            overlap = 0
            missing_items = []
            for item, quantity in items:
                num_fitted = contents.filter(eve_type=item).count()
                if num_fitted >= quantity:
                    overlap += quantity
                else:
                    missing_items.append((item, quantity-num_fitted))
            if overlap >= (modulecount - self.matching_fuzz):
                matching_ships.append(ship.pk)
            else:
                misfitted_ships.append((ship, missing_items,
                    Hangar.objects.get(hangarID=ship.hangarID).get_name( \
                            Corporation.objects.mine())))
            LOG.debug('{0} {1} matched {2}/{3}-{4} modules.'.format(
                ship.eve_type, ship.pk, overlap, modulecount, self.matching_fuzz))
        LOG.debug('Found {0} matching ships'.format(len(matching_ships)))
        matching = Asset.objects.filter(pk__in=matching_ships)
        return matching, misfitted_ships

    def stock_level(self):
        matching, not_matching = self.find_ships()
        return matching.count()

    def fully_stocked(self):
        return self.stock_level() >= self.desired_level

    def stock_description(self):
        matching, not_matching = self.find_ships()
        return '%d matches, %d misfitted, %d required' % (matching.count(),
                len(not_matching), self.desired_level)

    def fitting(self):
        ship, items = self.parse_fitting(self.eft_export)
        return items

    def parse_fitting(self, export):
        fitting = eft.parse_export(export)
        ship_type = None
        items = []
        for item, quantity in fitting.items():
            eve_type = Type.objects.get(typeName=item)
            if eve_type.categoryID == 6: # Ship category
                ship_type = eve_type
                fitting.pop(item)
            else:
                items.append((eve_type, quantity))
        return ship_type, items

    def accumulate_missing_items(self):
        matching, misfits = self.find_ships()
        total_missing_modules = {}

        for ship, missing_items, hangar in misfits:
            print missing_items
            for item, quantity in missing_items:
                if not item.pk in total_missing_modules:
                    total_missing_modules[item] = {'missing': 0,
                            'stocked': 0}
                total_missing_modules[item]['missing'] += quantity
        for item_key in total_missing_modules.keys():
            items = Asset.objects.filter(stationID=self.group.stationID,
                    eve_type=item_key, singleton=False)
            aggregated = items.aggregate(models.Sum('quantity'))
            if aggregated['quantity__sum']:
                total_missing_modules[item]['stocked'] = aggregated['quantity__sum']
        return total_missing_modules
