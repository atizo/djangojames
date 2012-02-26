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
# Created on Feb 26, 2012
# @author: github.com/maersu

from django import template
import re

register = template.Library()

BOOLS = {'true': True, 'false': False}
class SetVarNode(template.Node):
    def __init__(self, aval, avar, try_cast=False):
        self.aval = aval
        self.avar = avar
        self.try_cast = try_cast
    def render(self, context): 
        if self.try_cast:
            if self.aval.isdigit():
                self.aval = int(self.aval)
            elif self.aval.lower() in BOOLS.keys():
                self.aval = BOOLS[self.aval.lower()]
                
            for c in context:
                if self.aval in c:
                    context[self.avar] = context.get(self.aval)
                    return ''
        context[self.avar] = self.aval
        return ''

@register.tag
def setvar(parser,token):
    """
        Example:

            {% if user in object.list.all %}
                {% setvar "Max" as user %}
            {% endif %}
    
            {{user}}
        
        or:
        
            {% if user in object.list.all %}
                {% setvar true as isuser %}
            {% endif %}
    
            {{isuser}}
        
    """

    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    val_string, var_name = m.groups()
    
    try_cast=False
    if not (val_string[0] == val_string[-1] and val_string[0] in ('"', "'")):
        try_cast = True
    else:
        val_string = val_string[1:-1]
         
    return SetVarNode(val_string, var_name, try_cast)

register.tag('setvar', setvar)