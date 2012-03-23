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
# Created on Mar 13, 2012
# @author: github.com/maersu

from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from djangojames.models.utils import unique_text
  
class UniqeSluger(object):
    def __init__(self, source, target):
        self.target = target
        self.source = source
        
    def __call__(self, instance, **kwargs):
        source_field = getattr(instance, self.source)
        targte_value = unique_text(slugify(source_field),
                                   instance.__class__,
                                   self.target)
        setattr(instance,
                self.target,
                targte_value)


def unique_slug(target, source):
    """
    usage:
        @unique_slug('name', 'slug')
        class SlugModel(models.Model):
            name = models.CharField()
            slug = models.SlugField()
    """
    def _decorator(klass):
        pre_save.connect(UniqeSluger(target, source), sender=klass, weak=False)
        return klass
    return _decorator