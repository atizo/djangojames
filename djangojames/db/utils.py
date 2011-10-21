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

import os
from subprocess import call
from random import choice
from django.db.utils import IntegrityError
from django.db.models.loading import get_app
from django.db.models import get_models, EmailField

TMP_DUMP_DB = '/tmp/dump.out'

def _get_engine(database_config):
    return database_config['ENGINE'].split('.')[-1]

def get_dumpdb_name(): 
    from django.conf import settings
    return 'dump_%s.out' % os.path.split(settings.PROJECT_ROOT)[-1]

def reset_schema(database_config):
    from django.db import connection
    from django.db import transaction
    from django.conf import settings
    
    db_engine = _get_engine(database_config)
    sql_list = None
    
    if db_engine in ['postgresql_psycopg2', 'postgresql']:
        sql_list = (
            'DROP  SCHEMA public CASCADE',
            'CREATE SCHEMA public AUTHORIZATION %s' % database_config['USER'],
            'GRANT ALL ON SCHEMA public TO postgres',
            'GRANT ALL ON SCHEMA public TO public',
            "COMMENT ON SCHEMA public IS 'standard public schema';",
        )

    elif db_engine == 'mysql':
        sql_list = (
            'DROP DATABASE %s' % database_config['NAME'],
            'CREATE DATABASE %s' % database_config['NAME'],
            'USE %s' % database_config['NAME']
        )
    elif db_engine == 'sqlite3':
        db_path = os.path.join(settings.PROJECT_ROOT, database_config['NAME'])
        if os.path.exists(db_path):
            print "Remove sqlite3 db file: %s" % db_path
            os.remove(db_path)
    else:
        raise NotImplementedError, "This database backend is not yet supported: %s" % db_engine
    
    cursor = connection.cursor()
    if sql_list and len(sql_list):
        for sql in sql_list:
            cursor.execute(sql)
    transaction.commit_unless_managed()
            
def restore_db(database_config, backup_file):
    
    if not (os.path.exists(backup_file) and os.path.isfile(backup_file)):
        raise Exception("Backup file '%s' doesn't exists" % backup_file)
    
    db_engine = _get_engine(database_config)
    database_config['FILE'] = backup_file
    if db_engine in ['postgresql_psycopg2', 'postgresql']:    
        database_config['tmp_dump'] = TMP_DUMP_DB
        cmd = 'pg_restore -U %(USER)s -d %(NAME)s %(tmp_dump)s > /dev/null 2>&1'  % database_config
    elif db_engine == 'mysql':    
        cmd = 'mysql --user=%(USER)s --password=%(PASSWORD)s %(NAME)s < %(FILE)s' % database_config
    else:
        raise NotImplementedError, "This database backend is not yet supported: %s" % db_engine    

    print cmd 
    call(cmd, shell=True)    

def dump_db(database_config, outputpath='/tmp/'):
    db_engine = _get_engine(database_config)
    database_config['OUTPUT_FILE'] = os.path.join(outputpath, get_dumpdb_name())
    #from fabric.api import local
    
    if db_engine in ['postgresql_psycopg2', 'postgresql']:     
        cmd = 'pg_dump -U postgres %(NAME)s > %(OUTPUT_FILE)s' % database_config
    elif db_engine == 'mysql':
        
        if database_config['HOST']:
            database_config['HOST'] = '--host %s' % database_config['HOST']
        cmd = '/usr/bin/mysqldump %(NAME)s %(HOST)s -u %(USER)s -p%(PASSWORD)s >  %(OUTPUT_FILE)s' % database_config
    else:
        raise NotImplementedError, "This database backend is not yet supported: %s" % db_engine    

    print cmd
    call(cmd, shell=True)
    
def get_random_text(length=10, allowed_chars='abcdefghijklmnopqrstuvwxyz'):
    return ''.join([choice(allowed_chars) for i in range(length)])
    
def foo_emails(domain_extension='foo'):
    
    def _get_foo_email(email):
        try:
            ll = email.split('@')
            return (ll[0]+'@'+domain_extension+'-'+ll[1]).lower()
        except:
            fragment = get_random_text()
            new_mail = (fragment+'@'+domain_extension+'-'+fragment+'.ch').lower()
            print 'WARNING: Invalid Email found: "' + email +'" (-> '+ new_mail
            return new_mail
    
    from django.conf import settings
    from django.db import transaction
    
    app_label = lambda app: app[app.rfind('.')+1:]
    
    email_cnt = 0
    # set fake emails for all EmailFields
    for app in settings.INSTALLED_APPS:
        app = get_app(app_label(app), True)
        if not app:
            continue
        
        model_list = get_models(app)
        for model in model_list:
            field_names = [f.attname for f, m in model._meta.get_fields_with_model() if f.__class__ is EmailField]
            if len(field_names):
                try:
                    for model_instance in model.objects.all():
                        for field_name in field_names:
                            orig_email = getattr(model_instance, field_name)
                            if orig_email:
                                repl_email = _get_foo_email(orig_email)
                                setattr(model_instance, field_name, repl_email)
                                email_cnt += 1
                        try:
                            model_instance.save()
                            transaction.commit_unless_managed()
                        except IntegrityError, ie:
                            print '\nError while processing: ', model_instance
                            print ie
                            transaction.rollback_unless_managed()
                except Exception, e:
                    print '\nError while processing: ', model
                    print e
                    transaction.rollback_unless_managed()
                        
    return email_cnt

    