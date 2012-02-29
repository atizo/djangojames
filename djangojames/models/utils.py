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
# Created on Feb 29, 2012
# @author: github.com/maersu

from django.db.models import Model
from django.forms.models import model_to_dict

def natural_copy(from_object, to_model_instance, exclude=None, ignore_blank=False):
    """Copy data from 'from_object' to 'to_model_instance' (by matching attribute names)
    
    Keyword arguments:
    from_object -- can be either  a django model instance or a dictionary
    to_model_instance -- a model instance
    exclude -- fields to ignore (think about id field)
    ignore_blank -- ignore blank fields (e.g False, None, '', 0)
    """
    if from_object is None or to_model_instance is None:     
        return      
    
    if exclude is None:
        exclude = []

    if type(from_object) == dict:
        for k, v in from_object.items():
            if k not in exclude and (ignore_blank == False or v):
                setattr(to_model_instance,k,v) 
    elif issubclass(from_object.__class__, Model):     
        return natural_copy(model_to_dict(from_object, exclude=exclude), to_model_instance)
    else:
        raise TypeError('Not Supported Type %s ' % type(from_object))
    
    
    