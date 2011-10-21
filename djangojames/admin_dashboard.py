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

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard

from admin_tools.dashboard import modules

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard.
    """ 
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

        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            title='Quick links',
            draggable=True,
            deletable=True,
            collapsible=True,
            children=[
                {
                    'title': _(u'Hauptseite'),
                    'url': reverse('index'),
                },
                {
                    'title': _(u'Passwort wechseln'),
                    'url': reverse('admin:password_change'),
                },
                {
                    'title': _(u'Übersetzen'),
                    'url': reverse('rosetta-home')
                },
                {
                    'title': _(u'Django Dokumentation'),
                    'url': 'https://docs.djangoproject.com/'
                },
            ]
        ))

        # append a feed module
        self.children.append(modules.Feed(
            title= _(u'Django Neuigkeiten'),
            feed_url='http://www.djangoproject.com/rss/weblog/',
            limit=5,
            
        ))

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass