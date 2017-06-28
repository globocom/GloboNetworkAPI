# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.api_virtual_interface.v4 import views

urlpatterns = patterns(
    '',
    url(r'^virtual-interface/((?P<obj_ids>[;\w]+)/)?$',
        views.VirtualInterfaceDBView.as_view()),
)
