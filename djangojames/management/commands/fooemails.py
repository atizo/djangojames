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

from django.core.management.base import NoArgsCommand
from optparse import make_option


class Command(NoArgsCommand):
    help = "prepend a snippet to every email"
    flag = __name__

    option_list = NoArgsCommand.option_list + (
        make_option('--domain_extension',
            help='a text snippet to prepend to the existing domains'),  
    )

    def handle_noargs(self, **options): 
        from djangojames.db.utils import foo_emails
        domain_extension = options.get('domain_extension', 'foo') 
        
        if not domain_extension:
            domain_extension = 'foo'
        
        email_cnt = foo_emails(domain_extension)
        print 'Foo %d emails' % email_cnt
