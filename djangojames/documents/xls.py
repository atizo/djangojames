#!/usr/bin/env python
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
from xlwt import Workbook, easyxf, Formula
from django.http import HttpResponse
from django.template.defaultfilters import slugify
import logging

logger = logging.getLogger(__name__)

LINK_WIDTH = 900
MAX_WIDTH = 0x0d00 + 15000
SEPARATOR = '|'
INVALID_SHEET_CHAR = [('[','('), (']',')'), ('*',''), ('/',' '), ('\\',' '), ('?',' '), (':',' ')]

class XlsWriter:

    link_style = easyxf("""
     font:
        height 160,      
        colour_index blue;
     """)     

    normal_style = easyxf("""
    alignment:
        wrap yes;           
     """)   

    header_style = easyxf("""
     font:
         colour_index white;
     pattern:
         back_colour gray50,
         pattern thick_forward_diag;    
    alignment:
        wrap yes;           
     """)     

    title_style = easyxf("""
     font:
         height 250,       
         bold yes;
     """)   

    subtitle_style = easyxf("""
     font:
         height 200,       
         bold yes;
     """) 

    header_roate_style = easyxf("""
     font:
         colour_index white;
     pattern:
         back_colour gray50,
         pattern thick_forward_diag;
    alignment: 
        rota 90,
        wrap yes;
     """)     
   
    def __init__(self):
        self.book = Workbook(encoding='utf-8')
        self.sheet_inf = []

    def get_response(self, filename):
        self.response = HttpResponse(mimetype='application/excel')
        self.response['Content-Disposition'] = 'attachment; filename=%s' % filename 
        self.book.save(self.response)
        return self.response

    def save(self, path):
        self.book.save(path)

    def add_sheet(self, name, add_title=True):
        def _short_str(name):
            l = len(name)
            if l > 31:
                name = name[:13]+' ... '+name[-13:]             
            #replace invalid chars
            for i in INVALID_SHEET_CHAR:
                name = name.replace(i[0],i[1])
                    
            return name
        try:
            self.book.add_sheet(_short_str(name))
        except:
            #fallback one
            try:
                self.book.add_sheet(_short_str(slugify(name)))
            except:
                #fallback two
                self.book.add_sheet('Sheet %d ' % (len(self.sheet_inf)+1))
            
        self.sheet_inf.append(0)
        sheet = len(self.sheet_inf)-1
        
        if add_title:
            self.write_row(sheet, [name], self.title_style)
        return sheet

    def write_vheader_row(self, ws, rowlist, style=None):
        self.write_row(ws, rowlist, self.header_roate_style)

    def write_header_row(self, ws, rowlist, style=None):
        self.write_row(ws, rowlist, self.header_style)
           
    def write_row(self, ws, rowlist, style=None):
        sh = self.book.get_sheet(ws)
        r = self.sheet_inf[ws]
        
        row = sh.row(r)
        c = 0
        for v in rowlist:
            
            if v == SEPARATOR:
                row.write(c, '', self.normal_style)
                sh.col(c).width = LINK_WIDTH       

            elif isinstance(v, Formula):
                row.write(c,v, self.link_style)
                sh.col(c).width = LINK_WIDTH
                
            elif style is not None and (style != self.header_roate_style or len(v) > 0):
                try:
                    row.write(c,v, style)
                except:
                    logger.exception('Could not write cell')
            else:      
                try:          
                    row.write(c,v, self.normal_style)
                except:
                    logger.exception('Could not write cell')
                                    
            if (isinstance(v, str) or isinstance(v, unicode)) and style != self.header_roate_style and v != SEPARATOR:
                l = min(0x0d00 + len(v)*200, MAX_WIDTH)
                if l > sh.col(c).width: 
                    sh.col(c).width = l       
            c += 1
        
        self.sheet_inf[ws] = r+1