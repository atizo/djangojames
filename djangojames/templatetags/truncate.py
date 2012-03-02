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
# Created on Mar 2, 2012
# @author: github.com/maersu

from django.template import Library
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy
from django.template.defaultfilters import stringfilter
import re
register = Library()

def truncate_string(s, num):
    s = force_unicode(s)
    newlength = int(num)
        
    if len(s) > newlength:
        length = newlength - 3
        if s[length-1] == ' ' or s[length] == ' ':
            s = s[:length].strip()
        else:
            words = re.split(' *', s[:length])
            if len(words) > 1:
                del words[-1]
            s = u' '.join(words)
        s += ' ...'
            
    return s
truncate_chars = allow_lazy(truncate_string, unicode)

@register.filter
@stringfilter
def truncatestring(value, arg):
    """
    Truncates the string after a number of characters. It respects word boundaries and keeps newlines.
    
    Argument: Number of characters.
    """
    try:
        length = int(arg)
    except ValueError: # If the argument is not a valid integer.
        return value # Fail silently.
    return truncate_chars(value, length)
truncatestring.is_safe = True