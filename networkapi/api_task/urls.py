# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_task import views

urlpatterns = patterns(
    '',
    url(r'^v3/task/(?P<task_id>[\w\d\-\.]+)/$', views.TaskView.as_view()),
)
