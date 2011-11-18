#!/usr/bin/env python
# encoding: utf-8
"""
urls.py

Created by  on 2011-11-15.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'stock.gphq.views.index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
