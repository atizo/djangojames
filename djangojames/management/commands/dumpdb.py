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
from djangojames.db.utils import dump_db

class Command(NoArgsCommand):
    help = "Dumps the project db"
    flag = __name__

    option_list = NoArgsCommand.option_list + (
        make_option('--outputpath',
            help='a directory to write the dump to'),  
    )

    def handle_noargs(self, **options): 
        from django.db.utils import DEFAULT_DB_ALIAS
        from django.conf import settings
        
        db = options.get('database', DEFAULT_DB_ALIAS)
        outputpath = options.get('outputpath', settings.PROJECT_ROOT) 
        
        if outputpath is None:
            outputpath = settings.PROJECT_ROOT
        
        database_config = settings.DATABASES[db]       
        
        dump_db(database_config, outputpath)
