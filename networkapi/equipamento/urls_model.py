# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.equipamento.resource.ModelAddResource import ModelAddResource
from networkapi.equipamento.resource.ModelAlterRemoveResource import ModelAlterRemoveResource
from networkapi.equipamento.resource.ModelGetAllResource import ModelGetAllResource
from networkapi.equipamento.resource.ModelGetByBrandResource import ModelGetByBrandResource

model_add_resource = ModelAddResource()
model_alter_remove_resource = ModelAlterRemoveResource()
model_get_all_resource = ModelGetAllResource()
model_get_by_brand_resource = ModelGetByBrandResource()

urlpatterns = patterns(
    '',
    url(r'^$', model_add_resource.handle_request, name='model.add'),
    url(r'^all/$', model_get_all_resource.handle_request, name='model.get.all'),
    url(r'^(?P<id_model>[^/]+)/$', model_alter_remove_resource.handle_request,
        name='model.update.remove.by.pk'),
    url(r'^brand/(?P<id_brand>[^/]+)/$',
        model_get_by_brand_resource.handle_request, name='model.get.by.brand'),
    url(r'^script/(?P<script_id>[^/]+)/$',
        model_get_all_resource.handle_request, name='model.get.all')
)
