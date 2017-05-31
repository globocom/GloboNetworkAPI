# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.equipamento.resource.BrandAddResource import BrandAddResource
from networkapi.equipamento.resource.BrandAlterRemoveResource import BrandAlterRemoveResource
from networkapi.equipamento.resource.BrandGetAllResource import BrandGetAllResource

brand_add_resource = BrandAddResource()
brand_alter_remove_resource = BrandAlterRemoveResource()
brand_get_all_resource = BrandGetAllResource()

urlpatterns = patterns(
    '',
    url(r'^$', brand_add_resource.handle_request,
        name='brand.add'),
    url(r'^all/$', brand_get_all_resource.handle_request,
        name='brand.get.all'),
    url(r'^(?P<id_brand>[^/]+)/$', brand_alter_remove_resource.handle_request,
        name='brand.update.remove.by.pk')
)
