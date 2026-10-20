# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_template.v4 import views

urlpatterns = patterns(
    '',
    url(r'^templates/(?P<template_type>config|rack)/'
        r'(?P<file_path>.+?)/?$',
        views.TemplateView.as_view()),
)
