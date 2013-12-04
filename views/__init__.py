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

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext as Ctx

from ecm.views.decorators import check_user_access
from ecm.plugins.stocks.models import Group, Fitting

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@check_user_access()
def home(request):
    groups = Group.objects.all()
    return render_to_response('ecm/stocks/groups.html', {
        'groups': groups,
        }, Ctx(request))

@check_user_access()
def fitting(request, fitting_id):
    fit = get_object_or_404(Fitting, pk=fitting_id)
    matching, misfits = fit.find_ships()
    LOG.debug(misfits)
    return render_to_response('ecm/stocks/fitting.html', {
        'fit': fit,
        'matching': matching,
        'misfits': misfits,
        }, Ctx(request))
