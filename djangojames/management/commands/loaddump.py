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
import os
import time

LOCAL_PATH = '/tmp/'

class Command(NoArgsCommand):
    fake_pw = 'test'
    domain_extension = 'fake'    
    help = 'Drops local database, loads database dump and set fake emails/usernames <name>"'+domain_extension+'"<domain> and fake passwords "'+fake_pw+'"'

    option_list = NoArgsCommand.option_list + (
        make_option('--keep_mails', action='store_true',
            help='Keep original mail addresses (ATTENTION!!!!)'),              
    )

    def handle_noargs(self, **options):
        from django.conf import settings
        from django.db.utils import DEFAULT_DB_ALIAS
        self.keep_mails = options.get('keep_mails', False)
        db = options.get('database', DEFAULT_DB_ALIAS)    
        database_config = settings.DATABASES[db]
        from djangojames.db.utils import reset_schema, get_dumpdb_name, restore_db
        from django.contrib.auth.models import User
        
        start_time = time.time()
        reset_schema(database_config)
        
        local_path =  os.path.join(LOCAL_PATH, get_dumpdb_name())
        print 'Using dumpfile at %s' % local_path
        
        restore_db(database_config, local_path)
        
        print 'Finished in %d seconds' % (time.time() - start_time)
        start_time = time.time()
        
        if self.keep_mails:
            warning = '@ ATTENTION: THE EMAIL ADDRESSES WILL NOT BE CHANGED! DO NOT SEND ANY MAIL FROM THE PLATFORM !!! @'
            print ''
            print '@'*len(warning)
            print warning
            print '@'*len(warning)
            print ''
        else:
            from django.core.management import call_command
            print 'Set fake emails <name>@%s-<domain> and fake passwords "%s"' % (self.domain_extension, self.fake_pw)
            
            call_command('fooemails', domain_extension=self.domain_extension)

            user = User()
            user.set_password(self.fake_pw)
            count = User.objects.all().update(password=user.password)
    
            print 'Reset %d passwords' % count
            print 'Finished in %d seconds' % (time.time() - start_time)
