# Copyright (c) 2010-2013 Kristian Berg
# 
# This file is part of stocks-plugin.
# 
# stocks-plugin is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# stocks-plugin is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# stocks-plugin. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2013-11-09"
__author__ = "vittoros"


from django.contrib import admin
from django.db.models import Q
from django import forms
from ext_plugins.stocks.models import Item, Fitting, Group
from ecm.apps.eve.models import Type, CelestialObject
from ecm.apps.corp.models import CorpHangar

class GroupForm(forms.ModelForm):
    stationID = forms.ModelChoiceField(queryset=CelestialObject.objects \
            .filter(Q(group=15) | Q(type=21645)).order_by('itemName'))
    hangarID = forms.ModelChoiceField(queryset=CorpHangar.objects.all(),
            required=False)

    def clean_stationID(self):
        station = self.cleaned_data.get('stationID', None)
        if station:
            return station.itemID

    def clean_hangarID(self):
        hangar = self.cleaned_data.get('hangarID', None)
        if hangar:
            return hangar.hangar_id


    class Meta:
        model = Group


class GroupAdmin(admin.ModelAdmin):
    form = GroupForm


class ItemAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'eve_type':
            kwargs['queryset'] = Type.objects.order_by('typeName')
        return super(ItemAdmin, self).formfield_for_foreignkey(db_field,
                request, **kwargs)


class FittingForm(forms.ModelForm):
    class Meta:
        model = Fitting


class FittingAdmin(admin.ModelAdmin):
    readonly_fields = ('ship_type',)
    form = FittingForm

    def save_model(self, request, obj, form, change):
        eft_data = form.cleaned_data.get('eft_export', None)
        ship_type, items = obj.parse_fitting(eft_data)
        obj.ship_type = ship_type
        admin.ModelAdmin.save_model(self, request, obj, form, change)
        obj.save()


admin.site.register(Group, GroupAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Fitting, FittingAdmin)
