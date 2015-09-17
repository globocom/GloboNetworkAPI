# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *
from django.http import HttpResponse

from networkapi.ambiente.resource.DivisionDcAddResource import DivisionDcAddResource
from networkapi.ambiente.resource.DivisionDcAlterRemoveResource import DivisionDcAlterRemoveResource
from networkapi.ambiente.resource.DivisionDcGetAllResource import DivisionDcGetAllResource
from networkapi.ambiente.resource.GroupL3AddResource import GroupL3AddResource
from networkapi.ambiente.resource.GroupL3AlterRemoveResource import GroupL3AlterRemoveResource
from networkapi.ambiente.resource.GroupL3GetAllResource import GroupL3GetAllResource
from networkapi.ambiente.resource.LogicalEnvironmentAddResource import LogicalEnvironmentAddResource
from networkapi.ambiente.resource.LogicalEnvironmentAlterRemoveResource import LogicalEnvironmentAlterRemoveResource
from networkapi.ambiente.resource.LogicalEnvironmentGetAllResource import LogicalEnvironmentGetAllResource
from networkapi.ambiente.resource.EnvironmentIpConfigResource import EnvironmentIpConfigResource

from networkapi.grupo.resource.GrupoResource import DireitoGrupoEquipamentoResource
from networkapi.grupo.resource.AdministrativePermissionByGroupUserResource import AdministrativePermissionByGroupUserResource
from networkapi.grupo.resource.AdministrativePermissionAddResource import AdministrativePermissionAddResource
from networkapi.grupo.resource.AdministrativePermissionAlterRemoveResource import AdministrativePermissionAlterRemoveResource
from networkapi.grupo.resource.AdministrativePermissionGetAllResource import AdministrativePermissionGetAllResource
from networkapi.grupo.resource.AdministrativePermissionGetByIdResource import AdministrativePermissionGetByIdResource
from networkapi.grupo.resource.PermissionGetAllResource import PermissionGetAllResource

from networkapi.interface.resource.InterfaceTypeGetAllResource import InterfaceTypeGetAllResource
from networkapi.interface.resource.InterfaceChannelResource import InterfaceChannelResource

from networkapi.grupovirtual.resource.GrupoVirtualResource import GroupVirtualResource

from networkapi.filter.resource.FilterListAllResource import FilterListAllResource
from networkapi.filter.resource.FilterAddResource import FilterAddResource
from networkapi.filter.resource.FilterAlterRemoveResource import FilterAlterRemoveResource
from networkapi.filter.resource.FilterGetByIdResource import FilterGetByIdResource
from networkapi.filter.resource.FilterAssociateResource import FilterAssociateResource
from networkapi.filter.resource.FilterDissociateOneResource import FilterDissociateOneResource

from networkapi.eventlog.resource.EventLogFindResource import EventLogFindResource
from networkapi.eventlog.resource.EventLogChoiceResource import EventLogChoiceResource

from networkapi.check.CheckAction import CheckAction

from networkapi.rack.resource.RackAddResource import RackAddResource
from networkapi.rack.resource.RackFindResource import RackFindResource
from networkapi.rack.resource.RackEditResource import RackEditResource
from networkapi.rack.resource.RackDeleteResource import RackDeleteResource
from networkapi.rack.resource.RackConfigResource import RackConfigResource
from networkapi.rack.resource.RackAplicarConfigResource import RackAplicarConfigResource
from networkapi.rack.resource.RackListAllResource import RackListAllResource
from networkapi.rack.resource.RackEnvironmentResource import RackEnvironmentResource
from networkapi.rack.resource.RackGetByEquipResource import RackGetByEquipResource
check_action = CheckAction()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

rack_add_resource = RackAddResource()
find_rack_resource = RackFindResource()
edit_rack_resource = RackEditResource()
delete_rack_resource = RackDeleteResource()
gerar_config_rack_resource = RackConfigResource()
aplicar_config_rack_resource = RackAplicarConfigResource()
list_all_racks_resource = RackListAllResource()
list_rack_environment_resource = RackEnvironmentResource()
get_rack_by_equip_resource = RackGetByEquipResource()

env_ip_conf_resource = EnvironmentIpConfigResource()

division_dc_add_resource = DivisionDcAddResource()
division_dc_alter_remove_resource = DivisionDcAlterRemoveResource()
division_dc_get_all_resource = DivisionDcGetAllResource()

group_l3_add_resource = GroupL3AddResource()
group_l3_alter_remove_resource = GroupL3AlterRemoveResource()
group_l3_get_all_resource = GroupL3GetAllResource()

logical_environment_add_resource = LogicalEnvironmentAddResource()
logical_environment_alter_remove_resource = LogicalEnvironmentAlterRemoveResource()
logical_environment_get_all_resource = LogicalEnvironmentGetAllResource()

virtual_group_resource = GroupVirtualResource()

interface_type_get_all_resource = InterfaceTypeGetAllResource()

interface_channel_resource = InterfaceChannelResource()

aperms_get_by_group = AdministrativePermissionByGroupUserResource()
aperms_add_resource = AdministrativePermissionAddResource()
aperms_get_by_pk_resource = AdministrativePermissionGetByIdResource()
aperms_get_all_resource = AdministrativePermissionGetAllResource()
aperms_alter_remove_resource = AdministrativePermissionAlterRemoveResource()
perms_get_all_resource = PermissionGetAllResource()

access_right_resource = DireitoGrupoEquipamentoResource()

filter_list_all = FilterListAllResource()
filter_add = FilterAddResource()
filter_alter_remove = FilterAlterRemoveResource()
filter_get_by_id = FilterGetByIdResource()
filter_associate = FilterAssociateResource()
filter_dissociate_one = FilterDissociateOneResource()

# eventlog
eventlog_find_resource = EventLogFindResource()
eventlog_choice_resource = EventLogChoiceResource()

api_prefix = r'^api/'

urlpatterns = patterns('',
    url(api_prefix, include('networkapi.api_deploy.urls')),
    url(api_prefix, include('networkapi.api_healthcheck.urls')),
    url(api_prefix, include('networkapi.api_interface.urls')),
    url(api_prefix, include('networkapi.api_network.urls')),
    url(api_prefix, include('networkapi.api_pools.urls')),
    url(api_prefix, include('networkapi.api_vip_request.urls')),
    url(api_prefix, include('networkapi.api_vlan.urls')),
    url(api_prefix, include('networkapi.snippets.urls')),
)

urlpatterns += patterns('',
   #equipamento
   url(r'^equipamento/', include('networkapi.equipamento.urls')),
   url(r'^equipment/', include('networkapi.equipamento.urls_equipment')),
   url(r'^equipamentoacesso/', include('networkapi.equipamento.urls_equipamentoacesso')),
   url(r'^equipamentogrupo/', include('networkapi.equipamento.urls_equipamentogrupo')),
   url(r'^equipmenttype/', include('networkapi.equipamento.urls_equipmenttype')),
   url(r'^equipamentoambiente/', include('networkapi.equipamento.urls_equipamentoambiente')),
   url(r'^equipmentscript/', include('networkapi.equipamento.urls_equipmentscript')),
   url(r'^equipamentoroteiro/', include('networkapi.equipamento.urls_equipamentoroteiro')),
   url(r'^brand/', include('networkapi.equipamento.urls_brand')),
   url(r'^model/', include('networkapi.equipamento.urls_model')),

   #ambiente
   url(r'^ambiente/', include('networkapi.ambiente.urls')),
   url(r'^environment/', include('networkapi.ambiente.urls_environment')),

   #rules
   url(r'^rule/', include('networkapi.blockrules.urls')),

   url(r'^ipconfig/$', env_ip_conf_resource.handle_request,
       name="ipconfig.associate"),

   url(r'^divisiondc/$', division_dc_add_resource.handle_request,
       name='division_dc.add'),
   url(r'^divisiondc/all/$', division_dc_get_all_resource.handle_request,
       name='division_dc.get.all'),
   url(r'^divisiondc/(?P<id_divisiondc>[^/]+)/$',
       division_dc_alter_remove_resource.handle_request, name='division_dc.update.remove.by.pk'),

   url(r'^groupl3/$', group_l3_add_resource.handle_request,
       name='group_l3.add'),
   url(r'^groupl3/all/$', group_l3_get_all_resource.handle_request,
       name='group_l3.get.all'),
   url(r'^groupl3/(?P<id_groupl3>[^/]+)/$',
       group_l3_alter_remove_resource.handle_request, name='group_l3.update.remove.by.pk'),

   url(r'^logicalenvironment/$', logical_environment_add_resource.handle_request,
       name='logical_environment.add'),
   url(r'^logicalenvironment/all/$', logical_environment_get_all_resource.handle_request,
       name='logical_environment.get.all'),
   url(r'^logicalenvironment/(?P<id_logicalenvironment>[^/]+)/$',
       logical_environment_alter_remove_resource.handle_request, name='logical_environment.update.remove.by.pk'),

   #vlan
   url(r'^vlan/', include('networkapi.vlan.urls')),
   url(r'^net_type/', include('networkapi.vlan.urls_net_type')),

   #ip
   url(r'^ip/', include('networkapi.ip.urls')),
   url(r'^ipv4/', include('networkapi.ip.urls_ipv4')),
   url(r'^ipv6/', include('networkapi.ip.urls_ipv6')),
   url(r'^network/', include('networkapi.ip.urls_network')),
   url(r'^ip4/', include('networkapi.ip.urls_ip4')),

   #scripts
   url(r'^script/', include('networkapi.roteiro.urls')),
   url(r'^scripttype/', include('networkapi.roteiro.urls_scripttype')),

   #healthcheckexpect
   url(r'^healthcheckexpect/', include('networkapi.healthcheckexpect.urls')),

   #vips
   url(r'^vip/', include('networkapi.requisicaovips.urls')),
   url(r'^requestvip/', include('networkapi.requisicaovips.urls_requestvip')),
   url(r'^real/', include('networkapi.requisicaovips.urls_real')),
   url(r'^environment-vip/', include('networkapi.requisicaovips.urls_environment-vip')),
   url(r'^environmentvip/', include('networkapi.requisicaovips.urls_environmentvip')),
   url(r'^optionvip/', include('networkapi.requisicaovips.urls_optionvip')),

   #interface
   url(r'^interface/', include('networkapi.interface.urls')),
   url(r'^int/', include('networkapi.interface.urls_int')),

   url(r'^grupovirtual/$', virtual_group_resource.handle_request,
       name='virtual_group.add.remove'),

   #usario
   url(r'^usuario/', include('networkapi.usuario.urls')),
   url(r'^user/', include('networkapi.usuario.urls_user')),
   url(r'^authenticate/', include('networkapi.usuario.urls_authenticate')),
   url(r'^user-change-pass/', include('networkapi.usuario.urls_user-change-pass')),
   url(r'^usergroup/', include('networkapi.usuario.urls_usergroup')),

   #tipoacesso
   url(r'^tipoacesso/', include('networkapi.tipoacesso.urls')),

   #grupos
   url(r'^ugroup/', include('networkapi.grupo.urls')),
   url(r'^egroup/', include('networkapi.grupo.urls_egroup')),
   url(r'^egrupo/', include('networkapi.grupo.urls_egrupo')),

   url(r'^perms/all/$', perms_get_all_resource.handle_request,
       name='permission.get.all'),
   url(r'^aperms/$', aperms_add_resource.handle_request,
       name='administrative.permission.add'),
   url(r'^aperms/all/$', aperms_get_all_resource.handle_request,
       name='administrative.permission.get.all'),
   url(r'^aperms/(?P<id_perm>[^/]+)/$', aperms_alter_remove_resource.handle_request,
       name='administrative.permission.update.remove.by.pk'),
   url(r'^aperms/group/(?P<id_ugroup>[^/]+)/$', aperms_get_by_group.handle_request,
       name='administrative.permission.get.by.group'),
   url(r'^aperms/get/(?P<id_perm>[^/]+)/$', aperms_get_by_pk_resource.handle_request,
       name='administrative.permission.get.by.pk'),

   url(r'^direitosgrupoequipamento/$', access_right_resource.handle_request,
       name='access_right.search.insert'),
   url(r'^direitosgrupoequipamento/ugrupo/(?P<id_grupo_usuario>[^/]+)/$',
       access_right_resource.handle_request, name='access_right.search.by.ugroup'),
   url(r'^direitosgrupoequipamento/egrupo/(?P<id_grupo_equipamento>[^/]+)/$',
       access_right_resource.handle_request, name='access_right.search.by.egroup'),
   url(r'^direitosgrupoequipamento/(?P<id_direito>[^/]+)/$',
       access_right_resource.handle_request, name='access_right.search.update.remove.by.pk'),

   url(r'^check$', check_action.check, name='check'),
)

urlpatterns += patterns('',
   url(r'^filter/all/$', filter_list_all.handle_request,
       name='filter.list.all'),
   url(r'^filter/$', filter_add.handle_request,
       name='filter.add'),
   url(r'^filter/(?P<id_filter>[^/]+)/$',
       filter_alter_remove.handle_request, name='filter.alter.remove'),
   url(r'^filter/get/(?P<id_filter>[^/]+)/$',
       filter_get_by_id.handle_request, name='filter.get.by.id'),
   url(r'^filter/(?P<id_filter>[^/]+)/equiptype/(?P<id_equiptype>[^/]+)/$',
       filter_associate.handle_request, name='filter.associate'),
   url(r'^filter/(?P<id_filter>[^/]+)/dissociate/(?P<id_equip_type>[^/]+)/$',
       filter_dissociate_one.handle_request, name='filter.dissociate.one'),
)

urlpatterns += patterns('',
   url(r'^eventlog/find/$', eventlog_find_resource.handle_request,
       name='eventlog.find'),
   url(r'^eventlog/choices/$', eventlog_choice_resource.handle_request,
       name='eventlog.choices'),
   url(r'^eventlog/version/$', eventlog_find_resource.handle_request,
       name='eventlog.version'),
   url(r'^healthcheck$',lambda _: HttpResponse("WORKING")),
   url(r'^rack/insert[/]?$', rack_add_resource.handle_request,
       name='rack.add'),
   url(r'^rack/list[/]?$', list_all_racks_resource.handle_request,
       name='list.rack'),
   url(r'^rack/find/(?P<rack_name>[^/]+)/$', find_rack_resource.handle_request,
       name='find.rack'),
   url(r'^rack/edit[/]?$', edit_rack_resource.handle_request,
       name='edit.rack'),
   url(r'^rack/(?P<id_rack>[^/]+)/$', delete_rack_resource.handle_request,
       name='delete.rack'),
   url(r'^rack/gerar-configuracao/(?P<id_rack>[^/]+)/$', gerar_config_rack_resource.handle_request,
       name='config.rack'),
   url(r'^rack/aplicar-config/(?P<id_rack>[^/]+)/$', aplicar_config_rack_resource.handle_request,
       name='aplicar.rack'),
   url(r'^rack/get-by-equip/(?P<equip_id>[^/]+)/$', get_rack_by_equip_resource.handle_request,
       name='rack.get.equip.id'),
   url(r'^interfacetype/get-type[/]?$', interface_type_get_all_resource.handle_request,
       name='interfacetype.get'),
   url(r'^rack/list-rack-environment/(?P<rack_id>[^/]+)/$', list_rack_environment_resource.handle_request,
       name='interfacetype.get'),
   url(r'^channel/editar[/]?$', interface_channel_resource.handle_request,
       name='channel.edit'),
   url(r'^channel/inserir[/]?$', interface_channel_resource.handle_request,
       name='channel.add'),
   url(r'^channel/delete/(?P<channel_name>[^/]+)/$', interface_channel_resource.handle_request,
       name='channel.delete'),
   url(r'^channel/get-by-name[/]?$', interface_channel_resource.handle_request,
       name='channel.get'),
)

urlpatterns += patterns('networkapi.test_form.views',
    url('^test-vip[/]?$', 'test_form',
        name='test_form_vip',)
)