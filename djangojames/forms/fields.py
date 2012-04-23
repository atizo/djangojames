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

from django.forms.util import flatatt
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django import forms

from widgets import Html5DateTimeInput

class InputLabelWidget(Select):
        
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        
        final_attrs = self.build_attrs(attrs, name=name)
        label = final_attrs.get('label','')
        if label:
            del final_attrs['label']
        
        output = [u'<select%s>' % flatatt(final_attrs)]
        if label:            
            output.append(self.render_option([], '', '- %s -' % label))
        
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append(u'</select>')

        return mark_safe(u'\n'.join(output))

class LabelCharField(forms.CharField):
    widget = InputLabelWidget
    
    def __init__(self, *args, **kwargs):
        super(LabelCharField, self).__init__(*args, **kwargs)
        self.label = kwargs.get('label', '')
    
    def widget_attrs(self, widget):
        if self.label:
            return {'label': u'%s' % self.label}
        return {}    
    
class LabelIntegerField(forms.IntegerField):
    widget = InputLabelWidget
    
    def __init__(self, *args, **kwargs):
        super(LabelIntegerField, self).__init__(*args, **kwargs)
        self.label = kwargs.get('label', '')
    
    def widget_attrs(self, widget):
        if self.label:
            return {'label': u'%s' % self.label}
        return {}
