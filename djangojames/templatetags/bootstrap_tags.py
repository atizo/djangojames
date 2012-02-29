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

register = template.Library()

@register.filter
def as_bootstrap(form):
    """
        Render a form bootstrap2 compatible
        
        Usage:
            {% load bootstrap_tags %}
            
            <form method="POST" action="." class="form-horizontal">
                {% csrf_token %}
                {{ my_form|as_bootstrap }}
                <div class="form-actions">
                    <button type="submit" class="btn primary">Save</button>
                </div>
            </form>
    """
    template = get_template("bootstrap/form.html")
    c = Context({"form": form})
    return template.render(c)
