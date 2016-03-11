# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url

from networkapi.api_task import views

urlpatterns = patterns(
    'networkapi.api_task.views',
    url(r'^task/list/?$', views.TaskListView.as_view()),
    url(r'^task/((?P<task_id>[-\w]+)/)?$', views.TaskView.as_view()),
)
