# -*- coding: utf-8 -*-
#
# ITerativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2012 ITerativ GmbH. All rights reserved.
#
# Created on May 6, 2012
# @author: maersu <me@maersu.ch>

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_request():
    return getattr(_thread_locals, "request", None)

def get_user():
    request = get_request()
    if request:
        return getattr(request, "user", None)

class ThreadLocalMiddleware(object):
    def process_request(self, request):
        _thread_locals.request = request
