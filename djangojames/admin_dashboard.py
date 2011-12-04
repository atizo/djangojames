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

from admin_tools.dashboard import modules, modules, Dashboard, AppIndexDashboard
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard.
    """
    
    template = 'djangojames/dashboard.html'

    class Media:
        css = ('djangojames/css/statistics.css',)
        js = ('djangojames/js/statistics.js',)
            
    def __init__(self, **kwargs):
        Dashboard.__init__(self, **kwargs)

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            title= _(u'Applikationen'),
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            title= _(u'Letzte Aktionen'),
            limit=5,
        ))

        try:
            main_page = reverse('index')
        except:
            main_page = '/'

        cildren = [{'title': _(u'Hauptseite'),
                    'url': main_page},
                    {'title': _(u'Passwort wechseln'),
                     'url': reverse('admin:password_change')},
                ]
        
        if 'rosetta' in settings.INSTALLED_APPS:
            cildren.append({'title': _(u'Übersetzen'),
                             'url': reverse('rosetta-home')})
             
        cildren.append({'title': _(u'Django Dokumentation'),
                    'url': 'https://docs.djangoproject.com/'})

        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            title='Quick links',
            draggable=True,
            deletable=True,
            collapsible=True,
            children=cildren
        ))
        
        stats_modules = get_statistics_modules()
        if len(stats_modules) == 1:
            sm = StatisticsModule()
            sm.module = stats_modules[0]
            self.children.append(sm)
        else:
            children = []
            
            for statmod in stats_modules:
                sm = StatisticsModule()
                sm.module = statmod   
                children.append(sm)

            self.children.append(modules.Group(
                title=_(u'Statistiken'),
                display="tabs",
                children=children
            ))

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        context['james_chart_js_url'] = getattr(
                settings,
                'JAMES_CHART_JS_URL',
                None
        )
        
        context['james_chart_export_js_url'] = getattr(
                settings,
                'JAMES_CHART_EXPORT_JS_URL',
                None
        )
    
def get_statistics_modules():
    mod_clss = getattr(
        settings,
        'JAMES_ADMIN_STATISTICS_MODULES',
        None
    )
    mods = []
    if mod_clss:
        for mod_cls in mod_clss:
            mod, inst = mod_cls.rsplit('.', 1)
            mod = import_module(mod)
            mods.append(getattr(mod, inst))

    return mods

class StatisticsModule(modules.LinkList):
    title = _(u'Statistiken')
    template  = 'djangojames/statistics_module.html'

    def init_with_context(self, context):
        stats = self.module()
        if stats.name:
            self.title = stats.name
        context['stats'] = stats
        self.children.append([])