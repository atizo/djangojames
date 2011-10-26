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
from StringIO import StringIO
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
#from svglib.svglib import SvgRenderer
#from reportlab.graphics import renderPDF, renderPM
#import xml.dom.minidom

@csrf_exempt
def export_highchart_svg(request):
    
    if request.method != 'POST':
        return HttpResponseBadRequest()
    
    if 'svg' not in request.POST or 'type' not in request.POST:
        return
    
    svg_data = request.POST['svg']
    content_type = request.POST['type']
    filename = 'filename' in request.POST and request.POST['filename'] or 'chart'

    ext = None
    if content_type == 'application/pdf':
        return HttpResponseBadRequest()
        # exprts ugly pdfs
        
        #http://alexandersimoes.com/journal/2011/07/12/convert-svg-to-pdf-and-prompt-for-download/
        
        # Need to parse SVG as utf-8 XML
        #doc = xml.dom.minidom.parseString(svg_data)
        #svg = doc.documentElement
        # Create new instance of SvgRenderer class
        #svgRenderer = SvgRenderer()
        #svgRenderer.render(svg)
        #drawing = svgRenderer.finish()
        #response = HttpResponse(mimetype=content_type)
        #ext = 'pdf'
        #pdf = renderPDF.drawToString(drawing)
        #response.write(pdf)
    elif content_type == 'image/svg+xml':
        ext = 'svg'
        response = HttpResponse(content=svg_data, mimetype=content_type)
    else:
        # invalid content type
        return HttpResponseBadRequest()
    
    response['Content-Disposition'] = 'attachment; filename=%s.%s' % (filename, ext)
    return response