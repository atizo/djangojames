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
from django.conf.urls.defaults import patterns, url
import datetime
from django.http import HttpResponse
from django.utils import simplejson
import time
from django.utils.functional import wraps
from django.template.loader import render_to_string
from django.db.models.aggregates import Count
from django.utils.datastructures import SortedDict
from googleanalytics import Connection
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
import logging
from django.template.defaultfilters import slugify

logger = logging.getLogger(__name__)

class BaseStatistics(object):
    
    name = _(u'Statistiken')
    render_template = 'djangojames/statistics.html'
    default_options = {}

    def __init__( self, *args, **kwargs):
        self.prefix = slugify(self.__class__.__name__)
    
    def get_statsmethod(self):
        return [(m.replace('stats_', ''), getattr(self,m)) for m in dir(self) if m.startswith('stats_')]

    def __unicode__(self):
        return self.get_html()

    def get_urls(self):
        self._urls = None
        
        def _add_pattern(pattern):
            if self._urls:
                self._urls += pattern
            else:
                self._urls = pattern            
        
        for m in self.get_statsmethod():
            _add_pattern(patterns("", url("^%s/$" % m[0], m[1], name='%s' % m[0]),))

        if hasattr(self, 'summary'):
            _add_pattern(patterns("", url("^%s/$" % 'summary', self.summary, name='%s' % 'summary'),))
                    
        return self._urls

    @classmethod
    def datetime_to_stamp(cls, a_datetime):
        
        if isinstance(a_datetime, unicode):
            a_datetime = BaseStatistics.str_to_date(a_datetime)

        a_datetime = a_datetime + datetime.timedelta(days=1)
        if isinstance(a_datetime, datetime.datetime):
            return time.mktime(a_datetime.replace(hour=0, minute=0, second=0, microsecond=0).timetuple()) * 1000
        else:
            return time.mktime(a_datetime.timetuple()) * 1000
    
    @classmethod
    def str_to_date(cls, astring, last_second=False, default=None):
        """
        parses a date 'yy-mm-dd' (eg 2011-05-24)
        """
        if astring:        
            l = [int(t) for t in astring.split('-')]
            if len(l) == 3:
                if last_second:
                    return datetime.datetime(l[0], l[1], l[2], 23, 59, 59)
                else:
                    return datetime.datetime(l[0], l[1], l[2])
        
        return default    
        
    def get_html(self):
        context = {'stats_config': simplejson.dumps(self.get_statsconfig())}
        context['earliest_date'] = '-3years'
        context['latest_date'] = '+2years'
        context['choice_per_col'] = '3'
        context['prefix'] = self.prefix
        
        if hasattr(self, 'get_extra_config'):
            context.update(self.get_extra_config())

        return render_to_string(self.render_template, context)
    
    def get_statsconfig(self):
        config_lists = []
        for m in self.get_statsmethod():
            name = unicode(getattr(m[1], "name", m[0]))
            options = getattr(m[1], 'options', self.default_options)
            modes = getattr(m[1], 'modes', {})
            type = getattr(m[1], 'type', {'name': 'line', 'unity': 'linear'})
            selected = getattr(m[1], "selected", False)
            multiple_series = getattr(m[1], "multiple_series", False)
            index = getattr(m[1], "index", 0)
            config_lists.append({'name':m[0], 'index':index, 'dataurl': self.get_data_url(m[0]), 'multiple_series': multiple_series,
                                 'label': name, 'options': options, 'selected': selected, 'modes': modes, 'type': type})
        
        config_lists=sorted(config_lists, key=lambda aconfig: aconfig['index'])
        configs = SortedDict()        
        for aconfig in config_lists:
            configs['%s_%s' % (aconfig['name'], self.prefix)] = aconfig
            
        return configs
    
    def get_data_url(self, method):
        return reverse(method)

def apply_days_range(days):   
    def decorator(view_func):     
        def _wrapped_view_func(instance, request, *args, **kwargs):
            try:        
    
                today = datetime.date.today()
                startdate = today - datetime.timedelta(days=days)
                
                from_date = BaseGoogleAnalyticsStatistics.str_to_date(request.GET.get('from', ''), default=startdate)
                to_date = BaseGoogleAnalyticsStatistics.str_to_date(request.GET.get('to', ''), last_second=True, default=today)
                kwargs['from_date'] = from_date
                kwargs['to_date'] = to_date   
                data = view_func(instance, request, *args, **kwargs)
            except Exception, e:
                logger.exception('Error: Could not get statistic')
                data = []
            return HttpResponse(simplejson.dumps(data), mimetype='application/javascript')
            
        return wraps(view_func)(_wrapped_view_func)  
    return decorator

class BaseSequenceStatistics(BaseStatistics):

    default_options = {'lines': { 'show': True }}

    @classmethod
    def get_null_secquence(cls, start_date, end_date):
        
        if start_date is None or end_date is None:
            return {}
        
        currentdate = datetime.date(start_date.year, start_date.month, start_date.day)
        enddate = datetime.date(end_date.year, end_date.month, end_date.day)        
        timeline_dict = {}
        while currentdate <= enddate:
            timeline_dict[cls.datetime_to_stamp(currentdate)] = 0    
            currentdate += datetime.timedelta(days=1)        
        return timeline_dict
  
    def handle_sequence(self, queryset, mode, from_date, to_date, timeline_dict, datefield_name='created'):

        if from_date is None or to_date is None:
            return timeline_dict

        kwargs = {'%s__gte' % datefield_name: from_date,
                  '%s__lte' % datefield_name: to_date + datetime.timedelta(days=1)}        
        new_name = 'date_%s' % datefield_name
        
        # count all objects per datefield_name
        queryset = queryset.filter(**kwargs).extra({new_name:"date(%s.%s)" % (queryset.model._meta.db_table,datefield_name)}) \
        .values(new_name).annotate(created_count=Count('id')).order_by(new_name)

        for idict in queryset:
            stamp = self.datetime_to_stamp(idict[new_name])
            timeline_dict[stamp] = idict['created_count']
    
        return timeline_dict

    def datetime_sequence(self, queryset, from_date, to_date, datefield_name='created'):
        timeline_dict = self.get_null_secquence(from_date, to_date)
        
        kwargs = {'%s__gte' % datefield_name: from_date,
                  '%s__lt' % datefield_name: to_date + datetime.timedelta(days=1)}        
        new_name = 'date_%s' % datefield_name
        
        # count all objects per datefield_name
        queryset = queryset.filter(**kwargs).extra({new_name:"date(%s.%s)" % (queryset.model._meta.db_table,datefield_name)}) \
        .values(new_name).annotate(created_count=Count('id')).order_by(new_name)

        for idict in queryset:
            stamp = self.datetime_to_stamp(idict[new_name])
            timeline_dict[stamp] = idict['created_count']
    
        data = []
        for day, count in timeline_dict.items():
            data.append([day, count])

        return data

class BaseFractionStatistics(BaseStatistics):
    
    def _flatten(self, data):
        if len(data) == 1:
            
            data = data[0]
            if isinstance(data, basestring):
                if data == '(not set)':
                    data = _('(Unbekannt)')

            return data
        else:
            return data

    def normalize(self, keyvalue_list_mix, calc_percent=False, summerize=True, order=True):
        
        def value_compare(x, y):
                cmp = x[1] < y[1]
                if cmp:
                    return 1
                else:
                    return -1        
        
        data_norm = []
        if len(keyvalue_list_mix) == 0:
            return data_norm
              
        keyvalue_list = []
        
        for k,v in keyvalue_list_mix:
            if type(v) not in (tuple, list):
                v = [v]
            keyvalue_list.append([k,v])
        
        totals = [0 for m in keyvalue_list[0][1]]
        
        for item in keyvalue_list:            
            for idx, val in enumerate(totals):
                totals[idx] = val + item[1][idx]

            if not calc_percent:
                data_norm.append([self._flatten(item[0]), self._flatten(item[1])])
        
        if calc_percent:
            totals_per = [100.0/t for t in totals]
            for item in keyvalue_list:
                for idx, val in enumerate(totals_per):
                    item[1][idx] = round(item[1][idx] * val,1)
                
                data_norm.append([self._flatten(item[0]), self._flatten(item[1])])
        
        if order:
            data_norm = sorted(data_norm, cmp=value_compare)
        
        return data_norm
    
class BaseGoogleAnalyticsStatistics(BaseFractionStatistics):
    # http://code.google.com/intl/de-CH/apis/analytics/docs/gdata/gdataReferenceDimensionsMetrics.html

    def __init__(self, *args, **kwargs):
        super(BaseGoogleAnalyticsStatistics, self).__init__()
        self._account = None
        self.filters = []
        
    def get_account(self):
        
        if not self._account:                
            connection = Connection(settings.GOOGLE_ACCOUNT, settings.GOOGLE_ACCOUNT_PASSWORD)    
            self._account = connection.get_account(settings.GOOGLE_ACCOUNT_PROFILE_ID)
        
        return self._account
        
    def get_data(self, start_date=None, end_date=None, dimensions=None, metrics=None, sort=None, filters=None, calc_percent=False, summerize=True):
        
        try:
            if start_date > end_date:
                start_date = end_date
    
            data = self.get_account().get_data(start_date=start_date, end_date=end_date, dimensions=dimensions, metrics=metrics, sort=sort, filters=filters).list
            
            if dimensions and 'date' in dimensions:
                index = dimensions.index('date')
                for item in data:
                    data_str = item[0][index]
                    item[0][index] = self.datetime_to_stamp(datetime.datetime(int(data_str[:4]),  int(data_str[4:6]), int(data_str[6:])))
        except:
            data = []
            
        return self.normalize(data, calc_percent, summerize)
    
    def _get_visitor(self, from_date, to_date):
        return self.get_data(start_date=from_date, end_date=to_date, dimensions=['date'], metrics=['visitors',], sort=['-date',], filters=self.filters, calc_percent=False)
    
    def _get_country(self, from_date, to_date):
        return self.get_data(start_date=from_date, end_date=to_date, dimensions=['country'], metrics=['visitors'], sort=['-visitors',], filters=self.filters, calc_percent=True)
    
    def _get_browser(self, from_date, to_date):
        return self.get_data(start_date=from_date, end_date=to_date, dimensions=['browser'], metrics=['visitors',], sort=['-visitors',], filters=self.filters, calc_percent=True)
