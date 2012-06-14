# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2012 ITerativ GmbH. All rights reserved.
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
# Created on Feb 28, 2012
# @author: github.com/maersu

from django.template import Context
from django.template.loader import get_template
from django import template
from django import forms
from django.forms.widgets import Input

register = template.Library()

def _handle_field(boundfield):
    if issubclass(boundfield.field.widget.__class__, Input):
        boundfield.field.widget.attrs['class'] = boundfield.field.widget.attrs.get('class', '') + ' input-text'
    boundfield.widgetclass = boundfield.field.widget.__class__.__name__.lower()

@register.filter
def as_foundation(form):
    """
        Render a form foundation2 compatible
        
        Usage:
            {% load foundation_tags %}
            
            <form method="POST" action=".">
                {% csrf_token %}
                {{ my_form|as_foundation }}
                <div class="form-actions">
                    <button type="submit" class="button">Save</button>
                </div>
            </form>
    """
    template = get_template("foundation/templatetags/form.html")

    for field in form:
        _handle_field(field)
                
    c = Context({"form": form})
    return template.render(c)

@register.filter
def as_foundation_field(field):
    """
        Render a form foundation compatible
        
        Usage:
            {% load foundation_tags %}
            
            <form method="POST" action=".">
                {% csrf_token %}
                <fieldset>
                {{ form.field1 |as_foundation_field }}
                {{ form.field2 |as_foundation_field }}
                {{ form.field3 |as_foundation_field }}
                <div class="form-actions">
                    <button type="submit" class="button">Save</button>
                </div>
                </fieldset>
            </form>
    """
    template = get_template("foundation/templatetags/field.html")
    _handle_field(field)
    c = Context({"field": field})
    return template.render(c)
