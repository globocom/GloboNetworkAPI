# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns('networkapi.snippets.views',
                       url(r'^snippets/$', 'snippet_list'),
                       )
