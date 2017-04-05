# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.interface.resource.InterfaceTypeGetAllResource import InterfaceTypeGetAllResource

interface_type_get_all_resource = InterfaceTypeGetAllResource()

urlpatterns = patterns(
    '',
    url(r'^get-type[/]?$', interface_type_get_all_resource.handle_request,
        name='interfacetype.get'),
)
