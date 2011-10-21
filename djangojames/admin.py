# -*- coding: utf-8 -*-
#
# Atizo - The Open Innovation Platform
# http://www.atizo.com/
#
# Copyright (c) 2008-2010 Atizo AG. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from django.template.defaultfilters import slugify
from django.contrib import admin
from djangojames.models.export import queryset_to_csv_response

def admin_export_as_csv(modeladmin, request, queryset):
    return queryset_to_csv_response(slugify(modeladmin.__class__.__name__), queryset)
admin_export_as_csv.short_description = "Auswahl als CSV Exportieren"
admin.site.add_action(admin_export_as_csv)
