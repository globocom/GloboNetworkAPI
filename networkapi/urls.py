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

from networkapi.vlan.resource.NetworkTypeResource import NetworkTypeResource

from networkapi.equipamento.resource.BrandAddResource import BrandAddResource
from networkapi.equipamento.resource.BrandAlterRemoveResource import BrandAlterRemoveResource
from networkapi.equipamento.resource.BrandGetAllResource import BrandGetAllResource

from networkapi.equipamento.resource.ModelAddResource import ModelAddResource
from networkapi.equipamento.resource.ModelAlterRemoveResource import ModelAlterRemoveResource
from networkapi.equipamento.resource.ModelGetAllResource import ModelGetAllResource
from networkapi.equipamento.resource.ModelGetByBrandResource import ModelGetByBrandResource

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
from networkapi.ambiente.resource.EnvironmentVipResource import EnvironmentVipResource
from networkapi.ambiente.resource.EnvironmentVipSearchResource import EnvironmentVipSearchResource
from networkapi.ambiente.resource.RequestAllVipsEnviromentVipResource import RequestAllVipsEnviromentVipResource

from networkapi.ip.resource.NetworkAddResource import NetworkAddResource
from networkapi.ip.resource.NetworkIPv4AddResource import NetworkIPv4AddResource
from networkapi.ip.resource.NetworkIPv6AddResource import NetworkIPv6AddResource
from networkapi.ip.resource.NetworkIPv4DeallocateResource import NetworkIPv4DeallocateResource
from networkapi.ip.resource.NetworkIPv6DeallocateResource import NetworkIPv6DeallocateResource
from networkapi.ip.resource.SearchIPv6EnvironmentResource import SearchIPv6EnvironmentResource
from networkapi.ip.resource.NetworkIPv4GetResource import NetworkIPv4GetResource
from networkapi.ip.resource.NetworkIPv6GetResource import NetworkIPv6GetResource
from networkapi.ip.resource.IPv4DeleteResource import IPv4DeleteResource
from networkapi.ip.resource.IPv4EditResource import IPv4EditResource
from networkapi.ip.resource.NetworkEditResource import NetworkEditResource
from networkapi.ip.resource.NetworkRemoveResource import NetworkRemoveResource

from networkapi.requisicaovips.resource.OptionVipResource import OptionVipResource
from networkapi.requisicaovips.resource.OptionVipEnvironmentVipAssociationResource import OptionVipEnvironmentVipAssociationResource
from networkapi.requisicaovips.resource.OptionVipAllResource import OptionVipAllResource
from networkapi.requisicaovips.resource.OptionVipAllGetByEnvironmentVipResource import OptionVipAllGetByEnvironmentVipResource

from networkapi.usuario.resource.UserGroupAssociateResource import UserGroupAssociateResource
from networkapi.usuario.resource.UserGroupDissociateResource import UserGroupDissociateResource
from networkapi.usuario.resource.UsuarioGetResource import UsuarioGetResource
from networkapi.usuario.resource.UserAddResource import UserAddResource
from networkapi.usuario.resource.UserAlterRemoveResource import UserAlterRemoveResource
from networkapi.usuario.resource.UserGetAllResource import UserGetAllResource
from networkapi.usuario.resource.UserGetByIdResource import UserGetByIdResource

from networkapi.usuario.resource.UsuarioChangePassResource import UsuarioChangePassResource
from networkapi.usuario.resource.AuthenticateResource import AuthenticateResource
from networkapi.usuario.resource.UserGetByGroupUserResource import UserGetByGroupUserResource
from networkapi.usuario.resource.UserGetByGroupUserOutGroup import UserGetByGroupUserOutGroup

from networkapi.grupo.resource.GrupoResource import GrupoEquipamentoResource, DireitoGrupoEquipamentoResource
from networkapi.grupo.resource.AdministrativePermissionByGroupUserResource import AdministrativePermissionByGroupUserResource
from networkapi.grupo.resource.AdministrativePermissionAddResource import AdministrativePermissionAddResource
from networkapi.grupo.resource.AdministrativePermissionAlterRemoveResource import AdministrativePermissionAlterRemoveResource
from networkapi.grupo.resource.AdministrativePermissionGetAllResource import AdministrativePermissionGetAllResource
from networkapi.grupo.resource.AdministrativePermissionGetByIdResource import AdministrativePermissionGetByIdResource
from networkapi.grupo.resource.PermissionGetAllResource import PermissionGetAllResource
from networkapi.grupo.resource.GrupoEquipamentoGetByEquipResource import GrupoEquipamentoGetByEquipResource
from networkapi.grupo.resource.GrupoEquipamentoRemoveAssociationEquipResource import GrupoEquipamentoRemoveAssociationEquipResource
from networkapi.grupo.resource.GroupEquipmentResource import GroupEquipmentResource

from networkapi.grupo.resource.GroupUserGetAllResource import GroupUserGetAllResource
from networkapi.grupo.resource.GroupUserGetByIdResource import GroupUserGetByIdResource
from networkapi.grupo.resource.GroupUserAlterRemoveResource import GroupUserAlterRemoveResource
from networkapi.grupo.resource.GroupUserAddResource import GroupUserAddResource

from networkapi.interface.resource.InterfaceResource import InterfaceResource
from networkapi.interface.resource.InterfaceGetResource import InterfaceGetResource
from networkapi.interface.resource.InterfaceDisconnectResource import InterfaceDisconnectResource
from networkapi.interface.resource.InterfaceTypeGetAllResource import InterfaceTypeGetAllResource
from networkapi.interface.resource.InterfaceGetSwRouterResource import InterfaceGetSwRouterResource
from networkapi.interface.resource.InterfaceEnvironmentResource import InterfaceEnvironmentResource
from networkapi.interface.resource.InterfaceChannelResource import InterfaceChannelResource

from networkapi.grupovirtual.resource.GrupoVirtualResource import GroupVirtualResource

from networkapi.tipoacesso.resource.TipoAcessoResource import TipoAcessoResource

from networkapi.roteiro.resource.ScriptAddResource import ScriptAddResource
from networkapi.roteiro.resource.ScriptAlterRemoveResource import ScriptAlterRemoveResource
from networkapi.roteiro.resource.ScriptGetAllResource import ScriptGetAllResource
from networkapi.roteiro.resource.ScriptGetScriptTypeResource import ScriptGetScriptTypeResource
from networkapi.roteiro.resource.ScriptGetEquipmentResource import ScriptGetEquipmentResource

from networkapi.roteiro.resource.ScriptTypeAddResource import ScriptTypeAddResource
from networkapi.roteiro.resource.ScriptTypeAlterRemoveResource import ScriptTypeAlterRemoveResource
from networkapi.roteiro.resource.ScriptTypeGetAllResource import ScriptTypeGetAllResource


from networkapi.healthcheckexpect.resource.HealthcheckExpectResource import HealthcheckExpectResource
from networkapi.healthcheckexpect.resource.HealthcheckAddResource import HealthcheckAddResource

from networkapi.ambiente.resource.EnvironmentVipGetFinalityResource import EnvironmentVipGetFinalityResource
from networkapi.ambiente.resource.EnvironmentVipGetClienteTxtResource import EnvironmentVipGetClienteTxtResource
from networkapi.ambiente.resource.EnvironmentVipGetAmbienteP44TxtResource import EnvironmentVipGetAmbienteP44TxtResource
from networkapi.requisicaovips.resource.OptionVipGetTimeoutByEVipResource import OptionVipGetTimeoutByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetGrupoCacheByEVipResource import OptionVipGetGrupoCacheByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetPersistenciaByEVipResource import OptionVipGetPersistenciaByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetBalanceamentoByEVipResource import OptionVipGetBalanceamentoByEVipResource
from networkapi.healthcheckexpect.resource.HealthcheckAddExpectStringResource import HealthcheckAddExpectStringResource
from networkapi.healthcheckexpect.resource.HealthcheckExpectDistinctResource import HealthcheckExpectDistinctResource
from networkapi.healthcheckexpect.resource.HealthcheckExpectGetResource import HealthcheckExpectGetResource

# Filter
from networkapi.filter.resource.FilterListAllResource import FilterListAllResource
from networkapi.filter.resource.FilterAddResource import FilterAddResource
from networkapi.filter.resource.FilterAlterRemoveResource import FilterAlterRemoveResource
from networkapi.filter.resource.FilterGetByIdResource import FilterGetByIdResource
from networkapi.filter.resource.FilterAssociateResource import FilterAssociateResource
from networkapi.filter.resource.FilterDissociateOneResource import FilterDissociateOneResource

from networkapi.eventlog.resource.EventLogFindResource import EventLogFindResource
from networkapi.eventlog.resource.EventLogChoiceResource import EventLogChoiceResource

# Healthcheck
from networkapi.check.CheckAction import CheckAction
from usuario.resource.UserGetByLdapResource import UserGetByLdapResource


from networkapi.requisicaovips.resource.RequestVipGetRulesByEVipResource import RequestVipGetRulesByEVipResource
from networkapi.blockrules.resource.RuleResource import RuleResource
from networkapi.blockrules.resource.RuleGetResource import RuleGetResource
from networkapi.requisicaovips.resource.OptionVipGetHealthcheckByEVipResource import OptionVipGetHealthcheckByEVipResource


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

healthcheckexpect_string_resource = HealthcheckAddExpectStringResource()

healthcheckexpect_distinct_resource = HealthcheckExpectDistinctResource()

healthcheckexpect_get_resource = HealthcheckExpectGetResource()

opt_vip_timeout = OptionVipGetTimeoutByEVipResource()
opt_vip_grupocache = OptionVipGetGrupoCacheByEVipResource()
opt_vip_persistencia = OptionVipGetPersistenciaByEVipResource()
opt_vip_balanceamento = OptionVipGetBalanceamentoByEVipResource()
opt_vip_healthcheck = OptionVipGetHealthcheckByEVipResource()

environment_vip_finality = EnvironmentVipGetFinalityResource()
environment_vip_cliente_txt = EnvironmentVipGetClienteTxtResource()
environment_vip_ambientep44_txt = EnvironmentVipGetAmbienteP44TxtResource()
environment_vip_rules = RequestVipGetRulesByEVipResource()


rule_resource = RuleResource()
rule_get_resource = RuleGetResource()



# brand_resource = MarcaResource()
brand_add_resource = BrandAddResource()
brand_alter_remove_resource = BrandAlterRemoveResource()
brand_get_all_resource = BrandGetAllResource()

# model_resource = ModeloResource()
model_add_resource = ModelAddResource()
model_alter_remove_resource = ModelAlterRemoveResource()
model_get_all_resource = ModelGetAllResource()
model_get_by_brand_resource = ModelGetByBrandResource()

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

networkip4_get_resource = NetworkIPv4GetResource()
networkip6_get_resource = NetworkIPv6GetResource()
network_edit_resource = NetworkEditResource()

ipv4_delete_resource = IPv4DeleteResource()

ipv4_edit_resource = IPv4EditResource()


network_add_resource = NetworkAddResource()
network_remove_resource = NetworkRemoveResource()
network_ipv4_add_resource = NetworkIPv4AddResource()
network_ipv4_deallocate_resource = NetworkIPv4DeallocateResource()
network_ipv6_add_resource = NetworkIPv6AddResource()
network_ipv6_deallocate_resource = NetworkIPv6DeallocateResource()
search_ipv6_environment = SearchIPv6EnvironmentResource()

# equipment_script_resource = EquipamentoRoteiroResource()

# script_resource = RoteiroResource()

script_add_resource = ScriptAddResource()
script_alter_remove_resource = ScriptAlterRemoveResource()
script_get_all_resource = ScriptGetAllResource()
script_get_script_type_resource = ScriptGetScriptTypeResource()
script_get_equipment_resource = ScriptGetEquipmentResource()


script_type_add_resource = ScriptTypeAddResource()
script_type_alter_remove_resource = ScriptTypeAlterRemoveResource()
script_type_get_all_resource = ScriptTypeGetAllResource()

healthcheckexpect_resource = HealthcheckExpectResource()
healthcheckexpect_add_resource = HealthcheckAddResource()


option_vip = OptionVipResource()
option_vip_environment_vip_association = OptionVipEnvironmentVipAssociationResource()
option_vip_all = OptionVipAllResource()
option_vip_environment_vip = OptionVipAllGetByEnvironmentVipResource()

virtual_group_resource = GroupVirtualResource()

access_type_resource = TipoAcessoResource()

network_type_resource = NetworkTypeResource()

interface_resource = InterfaceResource()
interface_get_resource = InterfaceGetResource()
interface_disconnect_resource = InterfaceDisconnectResource()
interface_type_get_all_resource = InterfaceTypeGetAllResource()
interface_get_sw_router_resource = InterfaceGetSwRouterResource()
interface_environment_resource = InterfaceEnvironmentResource()
interface_channel_resource = InterfaceChannelResource()

authenticate_resource = AuthenticateResource()

user_add_resource = UserAddResource()
user_alter_remove_resource = UserAlterRemoveResource()
user_get_by_pk_resource = UserGetByIdResource()
user_get_all_resource = UserGetAllResource()
user_get_by_ldap_resource = UserGetByLdapResource()

user_get_resource = UsuarioGetResource()

user_change_pass_resource = UsuarioChangePassResource()

user_get_by_group_resource = UserGetByGroupUserResource()
user_get_by_group_out_group_resource = UserGetByGroupUserOutGroup()

ugroup_get_all_resource = GroupUserGetAllResource()
ugroup_get_by_id_resource = GroupUserGetByIdResource()
ugroup_alter_remove_resource = GroupUserAlterRemoveResource()
ugroup_add_resource = GroupUserAddResource()

aperms_get_by_group = AdministrativePermissionByGroupUserResource()
aperms_add_resource = AdministrativePermissionAddResource()
aperms_get_by_pk_resource = AdministrativePermissionGetByIdResource()
aperms_get_all_resource = AdministrativePermissionGetAllResource()
aperms_alter_remove_resource = AdministrativePermissionAlterRemoveResource()
perms_get_all_resource = PermissionGetAllResource()

egroup_resource = GrupoEquipamentoResource()

egroup_remove_association_equip_resource = GrupoEquipamentoRemoveAssociationEquipResource()

egroup_get_by_equip_resource = GrupoEquipamentoGetByEquipResource()

egroup_get_resource = GroupEquipmentResource()

user_group_associate_resource = UserGroupAssociateResource()
user_group_dissociate_resource = UserGroupDissociateResource()

access_right_resource = DireitoGrupoEquipamentoResource()

environment_vip_resource = EnvironmentVipResource()

environment_vip_search_resource = EnvironmentVipSearchResource()

environment_vip_search_all_vips_resource = RequestAllVipsEnviromentVipResource()

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
   url(r'^vlan/', include('networkapi.vlan.urls')),
   url(r'^tipoacesso/$', access_type_resource.handle_request,
       name='access_type.insert.search'),
   url(r'^tipoacesso/(?P<id_tipo_acesso>[^/]+)/$',
       access_type_resource.handle_request, name='access_type.update.remove.by.pk'),

   url(r'^net_type/$', network_type_resource.handle_request,
       name='network_type.insert.search'),
   url(r'^net_type/(?P<id_net_type>[^/]+)/$',
       network_type_resource.handle_request, name='network_type.update.remove.by.pk'),

   #equipamento
   url(r'^equipamento/', include('networkapi.equipamento.urls')),
   url(r'^equipment/', include('networkapi.equipamento.urls_equipment')),
   url(r'^equipamentoacesso/', include('networkapi.equipamento.urls_equipamentoacesso')),
   url(r'^equipamentogrupo/', include('networkapi.equipamento.urls_equipamentogrupo')),
   url(r'^equipmenttype/', include('networkapi.equipamento.urls_equipmenttype')),
   url(r'^equipamentoambiente/', include('networkapi.equipamento.urls_equipamentoambiente')),
   url(r'^equipmentscript/', include('networkapi.equipamento.urls_equipmentscript')),
   url(r'^equipamentoroteiro/', include('networkapi.equipamento.urls_equipamentoroteiro')),

   #ambiente
   url(r'^ambiente/', include('networkapi.ambiente.urls')),
   url(r'^environment/', include('networkapi.ambiente.urls_environment')),

   url(r'^environment-vip/get/finality/$',
       environment_vip_finality.handle_request, name='environemnt-vip.get.finality'),
   url(r'^environment-vip/get/cliente_txt/$',
       environment_vip_cliente_txt.handle_request, name='environemnt-vip.get.cliente_txt'),
   url(r'^environment-vip/get/ambiente_p44_txt/$',
       environment_vip_ambientep44_txt.handle_request, name='environemnt-vip.get.ambientep44_txt'),
   url(r'^environment-vip/get/timeout/(?P<id_evip>[^/]+)/$',
       opt_vip_timeout.handle_request, name='option-vip.get.timeout'),
   url(r'^environment-vip/get/grupo-cache/(?P<id_evip>[^/]+)/$',
       opt_vip_grupocache.handle_request, name='option-vip.get.grupocache'),
   url(r'^environment-vip/get/persistencia/(?P<id_evip>[^/]+)/$',
       opt_vip_persistencia.handle_request, name='option-vip.get.persistencia'),
   url(r'^environment-vip/get/balanceamento/(?P<id_evip>[^/]+)/$',
       opt_vip_balanceamento.handle_request, name='option-vip.get.balanceamento'),
   url(r'^environment-vip/get/rules/(?P<id_evip>[^/]+)(?:/(?P<id_vip>[^/]+))?/$',
       environment_vip_rules.handle_request, name='environment-vip.get.rules'),
   url(r'^environment-vip/get/healthcheck/(?P<id_evip>[^/]+)/$',
       opt_vip_healthcheck.handle_request, name='environment-vip.get.healthcheck'),

   url(r'^rule/get_by_id/(?P<id_rule>[^/]+)/$',
       rule_resource.handle_request, name='rule.get.by.id'),
   url(r'^rule/all/(?P<id_env>[^/]+)/$',
       rule_get_resource.handle_request, name='rule.all'),
   url(r'^rule/save/$', rule_resource.handle_request,
       name='rule.save'),
   url(r'^rule/update/$', rule_resource.handle_request,
       name='rule.update'),
   url(r'^rule/delete/(?P<id_rule>[^/]+)/$',
       rule_resource.handle_request, name='rule.delete'),

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

   #ip
   url(r'^ip/', include('networkapi.ip.urls')),

   url(r'^ip4/delete/(?P<id_ipv4>[^/]+)',
       ipv4_delete_resource.handle_request, name='ip4.delete'),
   url(r'^ip4/edit', ipv4_edit_resource.handle_request,
       name="ip4.edit"),

   url(r'^ipv4/', include('networkapi.ip.urls_ipv4')),
   url(r'^ipv6/', include('networkapi.ip.urls_ipv6')),

   url(r'^script/$', script_add_resource.handle_request,
       name='script.add'),
   url(r'^script/all/$', script_get_all_resource.handle_request,
       name='script.get.all'),
   url(r'^script/(?P<id_script>[^/]+)/$',
       script_alter_remove_resource.handle_request, name='script.update.remove.by.pk'),
   url(r'^script/scripttype/(?P<id_script_type>[^/]+)/$',
       script_get_script_type_resource.handle_request, name='script.get.script_type'),
   url(r'^script/equipment/(?P<id_equipment>[^/]+)/$',
       script_get_equipment_resource.handle_request, name='script.get.equipment'),

   url(r'^scripttype/$', script_type_add_resource.handle_request,
       name='script_type.add'),
   url(r'^scripttype/all/$', script_type_get_all_resource.handle_request,
       name='script_type.get.all'),
   url(r'^scripttype/(?P<id_script_type>[^/]+)/$',
       script_type_alter_remove_resource.handle_request, name='script_type.update.remove.by.pk'),

   url(r'^healthcheckexpect/ambiente/(?P<id_amb>[^/]+)/$',
       healthcheckexpect_resource.handle_request, name='healthcheckexpect.search.by.environment'),
   url(r'^healthcheckexpect/add/$',
       healthcheckexpect_add_resource.handle_request, name='healthcheckexpect.add'),
   url(r'^healthcheckexpect/add/expect_string/$',
       healthcheckexpect_string_resource.handle_request, name='healthcheckexpect.string.add'),
   url(r'^healthcheckexpect/distinct/busca/$',
       healthcheckexpect_distinct_resource.handle_request, name='healthcheckexpect.distinct'),
   url(r'^healthcheckexpect/get/(?P<id_healthcheck>[^/]+)/$',
       healthcheckexpect_get_resource.handle_request, name='healthcheckexpect.get.by.pk'),

   #vips
   url(r'^vip/', include('networkapi.requisicaovips.urls')),
   url(r'^requestvip/', include('networkapi.requisicaovips.urls_requestvip')),
   url(r'^real/', include('networkapi.requisicaovips.urls_real')),

   url(r'^grupovirtual/$', virtual_group_resource.handle_request,
       name='virtual_group.add.remove'),

   url(r'^brand/$', brand_add_resource.handle_request,
       name='brand.add'),
   url(r'^brand/all/$', brand_get_all_resource.handle_request,
       name='brand.get.all'),
   url(r'^brand/(?P<id_brand>[^/]+)/$',
       brand_alter_remove_resource.handle_request, name='brand.update.remove.by.pk'),

   url(r'^model/$', model_add_resource.handle_request,
       name='model.add'),
   url(r'^model/all/$', model_get_all_resource.handle_request,
       name='model.get.all'),
   url(r'^model/(?P<id_model>[^/]+)/$',
       model_alter_remove_resource.handle_request, name='model.update.remove.by.pk'),
   url(r'^model/brand/(?P<id_brand>[^/]+)/$',
       model_get_by_brand_resource.handle_request, name='model.get.by.brand'),

   url(r'^interface/$', interface_resource.handle_request,
       name='interface.insert'),
   url(r'^interface/(?P<id_interface>[^/]+)/$', interface_resource.handle_request,
       name='interface.update.remove.by.pk'),
   url(r'^interface/(?P<id_interface>[^/]+)/get/$', interface_get_resource.handle_request,
       name='interface.get.by.pk'),
   url(r'^interface/get/(?P<channel_name>[^/]+)/(?P<id_equipamento>[^/]+)[/]?$', interface_get_resource.handle_request,
       name='interface.list.by.equip'),
   url(r'^interface/get-by-channel/(?P<channel_name>[^/]+)[/]/?$', interface_get_resource.handle_request,
       name='interface.get.by.pk'),
   url(r'^interface/equipamento/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request,
       name='interface.search.by.equipment'),
   url(r'^interface/equipment/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, {
       'new': True}, name='interface.search.by.equipment.new'),
   url(r'^interface/(?P<id_interface>[^/]+)/(?P<back_or_front>[^/]+)/$', interface_disconnect_resource.handle_request,
       name='interface.remove.connection'),
   url(r'^interface/(?P<nome_interface>.+?)/equipamento/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request,
       name='interface.search.by.interface.equipment'),
   url(r'^interface/(?P<nome_interface>.+?)/equipment/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, {
       'new': True}, name='interface.search.by.interface.equipment.new'),
   url(r'^int/getbyidequip/(?P<id_equipamento>[^/]+)/$', interface_get_sw_router_resource.handle_request,
       name='interface.get_sw_router'),
   url(r'^int/associar-ambiente[/]?$', interface_environment_resource.handle_request,
       name='interface.associar'),
   url(r'^int/get-env-by-interface/(?P<id_interface>[^/]+)[/]?$', interface_environment_resource.handle_request,
       name='interface.ambiente.get'),

   url(r'^authenticate/$', authenticate_resource.handle_request,
       name='user.authenticate'),
   url(r'^user/$', user_add_resource.handle_request,
       name='user.add'),
   url(r'^usuario/get/$', user_get_resource.handle_request,
       name='user.list.with.group'),
   url(r'^user-change-pass/$', user_change_pass_resource.handle_request,
       name='user.change.pass'),
   url(r'^user/all/$', user_get_all_resource.handle_request,
       name='user.get.all'),
   url(r'^user/(?P<id_user>[^/]+)/$',
       user_alter_remove_resource.handle_request, name='user.update.remove.by.pk'),
   url(r'^user/get/(?P<id_user>[^/]+)/$',
       user_get_by_pk_resource.handle_request, name='user.get.by.id'),
   url(r'^user/group/(?P<id_ugroup>[^/]+)/$',
       user_get_by_group_resource.handle_request, name='user.get.by.group'),
   url(r'^user/out/group/(?P<id_ugroup>[^/]+)/$',
       user_get_by_group_out_group_resource.handle_request, name='user.get.by.group.out.group'),
   url(r'^user/get/ldap/(?P<user_name>[^/]+)/$',
       user_get_by_ldap_resource.handle_request, name='user.get.ldap'),

   url(r'^ugroup/all/$', ugroup_get_all_resource.handle_request,
       name='ugroup.get.all'),
   url(r'^ugroup/get/(?P<id_ugroup>[^/]+)/$',
       ugroup_get_by_id_resource.handle_request, name='ugroup.get'),
   url(r'^ugroup/$', ugroup_add_resource.handle_request,
       name='ugroup.add'),
   url(r'^ugroup/(?P<id_ugroup>[^/]+)/$',
       ugroup_alter_remove_resource.handle_request, name='ugroup.alter.remove'),

   url(r'^egrupo/$', egroup_resource.handle_request,
       name='egroup.search.insert'),
   url(r'^egrupo/equipamento/(?P<id_equipamento>[^/]+)/egrupo/(?P<id_egrupo>[^/]+)/$',
       egroup_remove_association_equip_resource.handle_request, name='egroup.remove.equip.association'),
   url(r'^egrupo/equip/(?P<id_equip>[^/]+)/$',
       egroup_get_by_equip_resource.handle_request, name='egroup.get.by.equip'),
   url(r'^egrupo/(?P<id_grupo>[^/]+)/$',
       egroup_resource.handle_request, name='egroup.update.remove.by.pk'),
   url(r'^egroup/(?P<id_egroup>[^/]+)/$',
       egroup_get_resource.handle_request, name='egroup.get.by.pk'),

   url(r'^usergroup/user/(?P<id_user>[^/]+)/ugroup/(?P<id_group>[^/]+)/associate/$',
       user_group_associate_resource.handle_request, name='user_group.associate'),
   url(r'^usergroup/user/(?P<id_user>[^/]+)/ugroup/(?P<id_group>[^/]+)/dissociate/$',
       user_group_dissociate_resource.handle_request, name='user_group.dissociate'),

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

   url(r'^network/ipv4/id/(?P<id_rede4>[^/]+)/$',
       networkip4_get_resource.handle_request, name='network.ip4.get.by.id'),
   url(r'^network/ipv6/id/(?P<id_rede6>[^/]+)/$',
       networkip6_get_resource.handle_request, name='network.ip6.get.by.id'),
   url(r'^network/add/$', network_add_resource.handle_request,
       name='network.add'),
   url(r'^network/edit/$', network_edit_resource.handle_request,
       name='network.edit'),
   url(r'^network/create/$', network_edit_resource.handle_request,
       name='network.create'),
   url(r'^network/remove/$', network_remove_resource.handle_request,
       name='network.remove'),
   url(r'^network/ipv4/add/$', network_ipv4_add_resource.handle_request,
       name='network.ipv4.add'),
   url(r'^network/ipv4/(?P<id_network_ipv4>[^/]+)/deallocate/$',
       network_ipv4_deallocate_resource.handle_request, name='network.ipv4.deallocate'),
   url(r'^network/ipv6/add/$', network_ipv6_add_resource.handle_request,
       name='network.ipv6.add'),
   url(r'^network/ipv6/(?P<id_network_ipv6>[^/]+)/deallocate/$',
       network_ipv6_deallocate_resource.handle_request, name='network.ipv6.deallocate'),
)

urlpatterns += patterns('',
   url(r'^environmentvip/$', environment_vip_resource.handle_request,
       name='environment.vip.add'),
   url(r'^environmentvip/all/', environment_vip_resource.handle_request,
       name='environment.vip.all'),
   url(r'^environmentvip/search/$',
       environment_vip_search_resource.handle_request, name='environment.vip.search'),
   url(r'^environmentvip/search/(?P<id_vlan>[^/]+)/$',
       environment_vip_search_resource.handle_request, name='environment.vip.search'),
   url(r'^environmentvip/(?P<id_environment_vip>[^/]+)/$',
       environment_vip_resource.handle_request, name='environment.vip.update.remove'),
   url(r'^environmentvip/(?P<id_environment_vip>[^/]+)/vip/all/$',
       environment_vip_search_all_vips_resource.handle_request, name='environmentvip.vips.all'),

   url(r'^optionvip/all/$', option_vip_all.handle_request,
       name='option.vip.all'),
   url(r'^optionvip/$', option_vip.handle_request,
       name='option.vip.add'),
   url(r'^optionvip/(?P<id_option_vip>[^/]+)/$',
       option_vip.handle_request, name='option.vip.update.remove.search'),
   url(r'^optionvip/(?P<id_option_vip>[^/]+)/environmentvip/(?P<id_environment_vip>[^/]+)/$',
       option_vip_environment_vip_association.handle_request, name='option.vip.environment.vip.associate.disassociate'),
   url(r'^optionvip/environmentvip/(?P<id_environment_vip>[^/]+)/$',
       option_vip_environment_vip.handle_request, name='option.vip.by.environment.vip'),

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


# Healthcheck
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
