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

from django.utils.translation import ugettext_lazy as tr_lazy

NAME = 'stocks'
VERSION = '1.0'

DEPENDS_ON = {
    'ecm' : '2.0',
    'ecm.plugins.assets' : '2.0',
}

MENUS = [
    {'title': tr_lazy('Stocks'),    'url': '',      'items': [
    ]},
]

URL_PERMISSIONS = [
    r'^/stocks/.*$',
]

SETTINGS = {
}

