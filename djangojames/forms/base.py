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

from django import forms
from django.forms.util import ValidationError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from widgets import Html5DateInput, Html5TimeInput

class MetaBaseForm(object):
    def exists_all(self, fieldlist):
        return all([ f in self.cleaned_data and (
            self.cleaned_data[f] == True
            or (type(self.cleaned_data[f]) != bool and self.cleaned_data[f] != None)
        ) for f in fieldlist ])

    def exists_any_and_set(self, fieldlist, allow_zero=False):
        if allow_zero:
            if any([f in self.cleaned_data and (self.cleaned_data[f] or (allow_zero and self.cleaned_data[f] == 0)) for f in fieldlist]):
                return True        
        else:
            if any([f in self.cleaned_data and self.cleaned_data[f] for f in fieldlist]):
                return True

        return False

    def check_unique(self, modelklass, field, exclude_value='', error=_(u'Existiert bereits.'), ignore_case=False):
        
        if field in self.cleaned_data and self.cleaned_data[field]:

            if ignore_case:
                qfield = '%s__iexact' % field
            else:
                qfield = field
                
            kwargs={qfield: self.cleaned_data[field]}
            q = modelklass.objects.filter(**kwargs)
            
            if exclude_value:
                exkwargs={qfield: exclude_value}
                q = q.exclude(**exkwargs)

            if q.exists(): 
                self._errors[field] = ValidationError(error).messages
                del self.cleaned_data[field]

    def required_all(self, fieldlist, error=_(u'Dieses Feld ist zwingend erforderlich.')):
        for f in fieldlist:
            if f in self.cleaned_data and not self.cleaned_data[f]:
                self._errors[f] = ValidationError(error).messages
                del self.cleaned_data[f]

    def invalidate(self, fieldlist, error=_(u'Dieses Feld ist zwingend erforderlich.')):
        for f in fieldlist:
            if f in self.cleaned_data:
                self._errors[f] = ValidationError(error).messages
                del self.cleaned_data[f]

    def required_all_or_none(self, fieldlist, error=_(u'Dieses Feld ist zwingend erforderlich.')):
        not_found=[f for f in fieldlist if f in self.cleaned_data and not self.cleaned_data[f]]
        if len(not_found) > 0 and len(not_found) <> len(fieldlist):                                
            for nf in not_found:
                self._errors[nf] = ValidationError(error).messages
                del self.cleaned_data[nf]

    def required_at_least_one_text(self, fieldlist, error=_(u'Bitte mindestens einen Text eingeben')):
        if all([f in self.cleaned_data for f in fieldlist]):
            if all([len(strip_tags(self.cleaned_data.get(f, ''))) == 0 for f in fieldlist]):
                for f in fieldlist:
                    self._errors[f] = ValidationError(error).messages
                    del self.cleaned_data[f]

    def asterix_required(self):
        for index, field in enumerate(self):
            if field.field.required and field.field.label[-1] != '*':
                field.field.label = u'%s *' % field.field.label
                
                if field.field.widget.attrs.has_key('label'):
                    field.field.widget.attrs['label'] = field.field.label

    def remove_label_form_data(self):
        
        self.data = self.data.copy()
        
        for index, field in enumerate(self):
            if self.data.get(field.name, '') == u'%s' % field.label:
                del self.data[field.name]

    def disable_form(self):
        for field in self.fields.values():
            field.widget.attrs['disabled'] = "disabled"
                
class NiceForm(MetaBaseForm):
    render_template = 'djangojames/form.html'
    
    def as_nice(self):
        return self._render()

    def _render(self, context = None):
        if context == None: context = {}
        form = {'raw': self, 'fields': []}
        
        for index, field in enumerate(self):
            field.starts_group = self._starts_group(field.name)
            field.ends_group = self._ends_group(field.name)
            form['fields'].append({'raw': field, 'class': field.field.widget.__class__.__name__.lower()})
            if issubclass(type(field.field), forms.fields.DateField):
                field.field.widget = Html5DateInput()
            elif issubclass(type(field.field), forms.fields.TimeField):
                field.field.widget = Html5TimeInput()

        return mark_safe(render_to_string(self.render_template, dict(context, **{'form':form})))

    def __unicode__(self):        
        return self.as_nice()

    def _has_groups(self):
        if not hasattr(self, '__has_groups'):
            self.__has_groups = hasattr(self, 'Meta') and hasattr(self.Meta, 'groups')
        return self.__has_groups
        
    def _starts_group(self, fieldname):
        if self._has_groups():
            if not hasattr(self, '__group_start'):
                self.__group_start = [group[0] for group in self.Meta.groups if len(group) > 0]
            return fieldname in self.__group_start
        return False

    def _ends_group(self, fieldname):
        if self._has_groups():
            if not hasattr(self, '__group_end'):
                self.__group_end = [group[-1] for group in self.Meta.groups if len(group) > 0]
            return fieldname in self.__group_end
        return False

class BaseModelForm(NiceForm, forms.ModelForm):
    pass

class BaseForm(NiceForm, forms.Form):
    pass