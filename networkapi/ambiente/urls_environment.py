# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.ambiente.resource.EnvironmentAllGetByEnvironmentVipResource import EnvironmentAllGetByEnvironmentVipResource
from networkapi.ambiente.resource.EnvironmentBlocks import EnvironmentBlocks
from networkapi.ambiente.resource.EnvironmentConfigurationAddResource import EnvironmentConfigurationAddResource
from networkapi.ambiente.resource.EnvironmentConfigurationListResource import EnvironmentConfigurationListResource
from networkapi.ambiente.resource.EnvironmentConfigurationRemoveResource import EnvironmentConfigurationRemoveResource
from networkapi.ambiente.resource.EnvironmentEnvironmentVipAssociationResource import EnvironmentEnvironmentVipAssociationResource
from networkapi.ambiente.resource.EnvironmentGetAclPathsResource import EnvironmentGetAclPathsResource
from networkapi.ambiente.resource.EnvironmentGetByIdResource import EnvironmentGetByIdResource
from networkapi.ambiente.resource.EnvironmentListResource import EnvironmentListResource
from networkapi.ambiente.resource.EnvironmentSetTemplateResource import EnvironmentSetTemplateResource

environment_get_by_id_resource = EnvironmentGetByIdResource()
environment_get_acl_paths_resource = EnvironmentGetAclPathsResource()
environment_set_template = EnvironmentSetTemplateResource()
environment_blocks = EnvironmentBlocks()
environment_configuration_add_resource = EnvironmentConfigurationAddResource()
environment_configuration_list_resource = EnvironmentConfigurationListResource()
environment_configuration_remove_resource = EnvironmentConfigurationRemoveResource()
environment_environment_vip_association = EnvironmentEnvironmentVipAssociationResource()
environment_environment_vip_list = EnvironmentAllGetByEnvironmentVipResource()
environment_list_resource = EnvironmentListResource()

urlpatterns = patterns(
    '',
    url(r'^id/(?P<environment_id>[^/]+)/$', environment_get_by_id_resource.handle_request,
        name='environment.search.by.pk'),
    url(r'^acl_path[/]$', environment_get_acl_paths_resource.handle_request,
        name='environment.acl_path'),
    url(r'^set_template/(?P<environment_id>[^/]+)/$', environment_set_template.handle_request,
        name='environment.set.template'),
    url(r'^get_env_template/$', environment_set_template.handle_request,
        name='environment.get.template'),
    url(r'^configuration/save/$', environment_configuration_add_resource.handle_request,
        name='environment.configuration.save'),
    url(r'^configuration/list/(?P<environment_id>[^/]+)/$', environment_configuration_list_resource.handle_request,
        name='environment.configuration.list'),
    url(r'^configuration/remove/(?P<environment_id>[^/]+)/(?P<configuration_id>[^/]+)/$', environment_configuration_remove_resource.handle_request,
        name='environment.configuration.remove'),
    url(r'^save_blocks/$', environment_blocks.handle_request,
        name='environment.save.blocks'),
    url(r'^update_blocks/$', environment_blocks.handle_request,
        name='environment.update.blocks'),
    url(r'^get_blocks/(?P<environment_id>[^/]+)/$', environment_blocks.handle_request,
        name='environment.get.blocks'),
    url(r'^list_no_blocks/$', environment_list_resource.handle_request,
        name='environment.list.no_blocks'),
    url(r'^(?P<environment_id>[^/]+)/environmentvip/(?P<environment_vip_id>[^/]+)/$', environment_environment_vip_association.handle_request,
        name='environment.environmentvip.associate.disassociate'),
    url(r'^environmentvip/(?P<environment_vip_id>[^/]+)/$', environment_environment_vip_list.handle_request,
        name='environment.environmentvip.list'),
)
