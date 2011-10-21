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
from django.http import HttpResponse
import csv
from django.utils.encoding import smart_str
from django.utils.datastructures import SortedDict
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import datetime
from django.conf import settings

def humanized_content_dict_for_model_instance(instance):
    """Returns a dictionary for the given Django model instance with normalized data."""
    model = instance.__class__
    opts = model._meta
    data_map = SortedDict()
    suppress_object_id = False
    for f in opts.fields:
        k = f.name.replace('_', ' ').title()
        v = getattr(instance, f.name)
        if hasattr(instance, 'get_%s_display' % f.name):
            m = getattr(instance, 'get_%s_display' % f.name)                
            v = m()
        
        if type(f) == ForeignKey:
            try:
                to = f.related.parent_model            
                if to == User:
                    if v is not None:
                        name = v.get_full_name()
                        email = unicode(v.email)
                    else:
                        name = ''
                        email = ''
                    
                    data_map[k] = unicode(name)
                    data_map['%s Email' % k] = unicode(email)
                    continue
                
                elif to == ContentType and f.name == 'content_type':
                    if hasattr(instance, 'object_id'):
                        try:
                            data_map['Content Object'] = '%s: %s' % (v, v.get_object_for_this_type(id=getattr(instance, 'object_id')))
                        except:
                            data_map['Content Object'] = ''
                            pass
                        suppress_object_id = True
                        continue
                else:
                    if v is not None:
                        klass = ContentType.objects.get_for_model(v)
                        data_map[k] = '%s: %s' % (klass, v)
                        continue
                    
            except Exception, e:
                print e
                pass
                
        if v == None:
            v = ''
        elif type(v) == datetime.date:
            v = v.strftime(smart_str(settings.DATE_FORMAT))                   
        elif type(v) == datetime.datetime:
            v = v.strftime(smart_str(settings.DATETIME_FORMAT))
 
        data_map[k] = v

        if suppress_object_id and data_map.has_key('Object Id'):
            del data_map['Object Id']
    
    for f in opts.many_to_many:
        k = f.name.replace('_', ' ').title()
        vals = []
        for val in f.value_from_object(instance):
            klass = ContentType.objects.get_for_model(val)
            vals.append('%s: %s' % (klass, unicode(val)))
        data_map[k] = ','.join(vals)
    
    return data_map

def queryset_to_csv_response(filename, queryset):
    if len(queryset) > 0:
        response = HttpResponse(mimetype='text/csv')
        file_name = slugify(filename)
        response['Content-Disposition'] = 'attachment; filename=%s-export.csv' % file_name   
        writer = csv.writer(response)

        i = 0
        for inst in queryset:
            i += 1
            dict =  humanized_content_dict_for_model_instance(inst)
            if i == 1:
                writer.writerow([smart_str(k) for k in dict.keys()])
            writer.writerow([smart_str(c) for c in dict.values()])
            
        return response
    else:
        return None
