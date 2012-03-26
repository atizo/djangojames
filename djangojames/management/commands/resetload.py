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
import os
import sys
from djangojames.db.utils import reset_schema
from optparse import make_option

FIXTUERS_EXT = '.json'

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-i', '--ignore_reset', action='store_true', dest='ignore_reset',
            help='Do not extecute the reset command (equivalent to syncdb)'),        
        make_option('-y', '--rebuild_haystack', action='store_true', dest='rebuild_haystack',
            help='call haystack rebuild_index command'),                                                                                                       
    )
    help = "Drops and recreates database (from jsons)."
    
    def _find_fixtures(self, start_dir):
        """ find all JSON files (except those in Unit Test Folder or initial_data) """
        fixtures = []
        def _find(arg, dirname, names):
            if (dirname.endswith('fixtures')) and (dirname.find('unit_test')==-1):
                for name in names:
                    if (name.endswith(FIXTUERS_EXT)) and (name.find('initial_data')==-1):
                        fixtures.append(name.replace(FIXTUERS_EXT, ''))
        os.path.walk(start_dir, _find, None)
        return fixtures
   
    def handle_noargs(self, **options):
        from django.conf import settings
        from django.db import models
        from django.core.management.sql import  emit_post_sync_signal
        from django.db.utils import DEFAULT_DB_ALIAS
        from django.core.management import call_command
        
        ignore_reset = options.get('ignore_reset', False)
        rebuild_haystack = options.get('rebuild_haystack', False)
        db = options.get('database', DEFAULT_DB_ALIAS)       
        database_config = settings.DATABASES[db]
        
        if not ignore_reset:
            reset_schema(database_config)

        # init db schema
        call_command('syncdb', interactive=False)
        
        # Emit the post sync signal. This allows individual
        # applications to respond as if the database had been
        # sync'd from scratch.
        emit_post_sync_signal(models.get_models(), 0, 0, db)
        # get all fixtures
        fixtures = self._find_fixtures(settings.PROJECT_ROOT)
        
        sys.stdout.write("Load fixtures: %s\n" % " ".join(fixtures))
        # Reinstall the initial_data fixture.
        call_command('loaddata', *fixtures)
        
        if rebuild_haystack:
            call_command('rebuild_index', interactive=False)

