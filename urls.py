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

from django.conf.urls.defaults import patterns

urlpatterns = patterns('ext_plugins.stocks.views',
    (r'^$', 'home'),
    (r'^fitting/(?P<fitting_id>\d+)$', 'fitting'),
)


