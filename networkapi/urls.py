# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.conf.urls.defaults import *

from networkapi.vlan.resource.VlanResource import VlanResource
from networkapi.vlan.resource.VlanListResource import VlanListResource
from networkapi.vlan.resource.VlanSearchResource import VlanSearchResource
from networkapi.vlan.resource.VlanFindResource import VlanFindResource
from networkapi.vlan.resource.VlanAllocateResource import VlanAllocateResource
from networkapi.vlan.resource.VlanRemoveResource import VlanRemoveResource
from networkapi.vlan.resource.VlanDeallocateResource import VlanDeallocateResource
from networkapi.vlan.resource.VlanAllocateIPv6Resorce import VlanAllocateIPv6Resorce
from networkapi.vlan.resource.VlanCreateResource import VlanCreateResource
from networkapi.vlan.resource.VlanInsertResource import VlanInsertResource
from networkapi.vlan.resource.VlanEditResource import VlanEditResource
from networkapi.vlan.resource.VlanInvalidateResource import VlanInvalidateResource
from networkapi.vlan.resource.VlanValidateResource import VlanValidateResource
from networkapi.vlan.resource.VlanGetByEnvironmentResource import VlanGetByEnvironmentResource
from networkapi.vlan.resource.VlanCreateAclResource import VlanCreateAclResource
from networkapi.vlan.resource.VlanCreateScriptAclResource import VlanCreateScriptAclResource

from networkapi.vlan.resource.NetworkTypeResource import NetworkTypeResource

from networkapi.vlan.resource.VlanApplyAcl import VlanApplyAcl

from networkapi.equipamento.resource.EquipamentoResource import EquipamentoResource, EquipamentoAmbienteResource

from networkapi.equipamento.resource.EquipmentGetRealRelated import EquipmentGetRealRelated
from networkapi.equipamento.resource.BrandAddResource import BrandAddResource
from networkapi.equipamento.resource.BrandAlterRemoveResource import BrandAlterRemoveResource
from networkapi.equipamento.resource.BrandGetAllResource import BrandGetAllResource

from networkapi.equipamento.resource.ModelAddResource import ModelAddResource
from networkapi.equipamento.resource.ModelAlterRemoveResource import ModelAlterRemoveResource
from networkapi.equipamento.resource.ModelGetAllResource import ModelGetAllResource
from networkapi.equipamento.resource.ModelGetByBrandResource import ModelGetByBrandResource

from networkapi.equipamento.resource.EquipmentTypeGetAllResource import EquipmentTypeGetAllResource

from networkapi.equipamento.resource.EquipmentScriptAddResource import EquipmentScriptAddResource
from networkapi.equipamento.resource.EquipmentScriptRemoveResource import EquipmentScriptRemoveResource
from networkapi.equipamento.resource.EquipmentScriptGetAllResource import EquipmentScriptGetAllResource

from networkapi.equipamento.resource.EquipamentoEditResource import EquipamentoEditResource
from networkapi.equipamento.resource.EquipmentTypeAddResource import EquipmentTypeAddResource
from networkapi.equipamento.resource.EquipamentoGrupoResource import EquipamentoGrupoResource
from networkapi.equipamento.resource.EquipamentoAcessoResource import EquipamentoAcessoResource
from networkapi.equipamento.resource.EquipAccessListResource import EquipAccessListResource
from networkapi.equipamento.resource.EquipAccessGetResource import EquipAccessGetResource
from networkapi.equipamento.resource.EquipAccessEditResource import EquipAccessEditResource
from networkapi.equipamento.resource.EquipmentListResource import EquipmentListResource
from networkapi.equipamento.resource.EquipScriptListResource import EquipScriptListResource
from networkapi.equipamento.resource.EquipmentFindResource import EquipmentFindResource
from networkapi.equipamento.resource.EquipmentGetAllResource import EquipmentGetAllResource
from networkapi.equipamento.resource.EquipmentGetByGroupEquipmentResource import EquipmentGetByGroupEquipmentResource
from networkapi.equipamento.resource.EquipmentEnvironmentDeallocateResource import EquipmentEnvironmentDeallocateResource

from networkapi.ambiente.resource.AmbienteResource import AmbienteResource, AmbienteEquipamentoResource
from networkapi.ambiente.resource.DivisionDcAddResource import DivisionDcAddResource
from networkapi.ambiente.resource.DivisionDcAlterRemoveResource import DivisionDcAlterRemoveResource
from networkapi.ambiente.resource.DivisionDcGetAllResource import DivisionDcGetAllResource
from networkapi.ambiente.resource.GroupL3AddResource import GroupL3AddResource
from networkapi.ambiente.resource.GroupL3AlterRemoveResource import GroupL3AlterRemoveResource
from networkapi.ambiente.resource.GroupL3GetAllResource import GroupL3GetAllResource
from networkapi.ambiente.resource.LogicalEnvironmentAddResource import LogicalEnvironmentAddResource
from networkapi.ambiente.resource.LogicalEnvironmentAlterRemoveResource import LogicalEnvironmentAlterRemoveResource
from networkapi.ambiente.resource.LogicalEnvironmentGetAllResource import LogicalEnvironmentGetAllResource
from networkapi.ambiente.resource.EnvironmentListResource import EnvironmentListResource
from networkapi.ambiente.resource.EnvironmentGetByEquipResource import EnvironmentGetByEquipResource
from networkapi.ambiente.resource.EnvironmentIpConfigResource import EnvironmentIpConfigResource
from networkapi.ambiente.resource.EnvironmentVipResource import EnvironmentVipResource
from networkapi.ambiente.resource.EnvironmentVipSearchResource import EnvironmentVipSearchResource
from networkapi.ambiente.resource.RequestAllVipsEnviromentVipResource import RequestAllVipsEnviromentVipResource
from networkapi.ambiente.resource.EnvironmentBlocks import EnvironmentBlocks
from networkapi.ambiente.resource.EnvironmentConfigurationAddResource import EnvironmentConfigurationAddResource
from networkapi.ambiente.models import IP_VERSION

from networkapi.ambiente.resource.EnvironmentGetByIdResource import EnvironmentGetByIdResource

from networkapi.ip.resource.IpResource import IpResource
from networkapi.ip.resource.IPv4AddResource import IPv4AddResource
from networkapi.ip.resource.IPv6AddResource import IPv6AddResource
from networkapi.ip.resource.NetworkAddResource import NetworkAddResource
from networkapi.ip.resource.NetworkIPv4AddResource import NetworkIPv4AddResource
from networkapi.ip.resource.NetworkIPv6AddResource import NetworkIPv6AddResource
from networkapi.ip.resource.Ipv6AssociateResource import Ipv6AssociateResource
from networkapi.ip.resource.Ipv6RemoveResource import Ipv6RemoveResource
from networkapi.ip.resource.NetworkIPv4DeallocateResource import NetworkIPv4DeallocateResource
from networkapi.ip.resource.NetworkIPv6DeallocateResource import NetworkIPv6DeallocateResource
from networkapi.ip.resource.SearchIPv6EnvironmentResource import SearchIPv6EnvironmentResource
from networkapi.ip.resource.NetworkIPv4GetResource import NetworkIPv4GetResource
from networkapi.ip.resource.NetworkIPv6GetResource import NetworkIPv6GetResource
from networkapi.ip.resource.IPGetByEquipResource import IPGetByEquipResource
from networkapi.ip.resource.IPv4ListResource import IPv4ListResource
from networkapi.ip.resource.Ipv4GetByIdResource import Ipv4GetByIdResource
from networkapi.ip.resource.Ipv6GetByIdResource import Ipv6GetByIdResource
from networkapi.ip.resource.IPv6ListResource import IPv6ListResource
from networkapi.ip.resource.IPv4GetAvailableResource import IPv4GetAvailableResource
from networkapi.ip.resource.IPv6GetAvailableResource import IPv6GetAvailableResource
from networkapi.ip.resource.Ipv6GetAvailableForVipResource import Ipv6GetAvailableForVipResource
from networkapi.ip.resource.Ipv4GetAvailableForVipResource import Ipv4GetAvailableForVipResource
from networkapi.ip.resource.IPv4SaveResource import IPv4SaveResource
from networkapi.ip.resource.IPv6SaveResource import IPv6SaveResource
from networkapi.ip.resource.IPv4DeleteResource import IPv4DeleteResource
from networkapi.ip.resource.IPv6DeleteResource import IPv6DeleteResource
from networkapi.ip.resource.IPv4EditResource import IPv4EditResource
from networkapi.ip.resource.IPv6EditResource import IPv6EditResource
from networkapi.ip.resource.IPv6GetResource import IPv6GetResource
from networkapi.ip.resource.IPv4GetResource import IPv4GetResource
from networkapi.ip.resource.IPEquipEvipResource import IPEquipEvipResource
from networkapi.ip.resource.IpGetOctBlockResource import IpGetOctBlockResource
from networkapi.ip.resource.IpCheckForVipResource import IpCheckForVipResource
from networkapi.ip.resource.NetworkEditResource import NetworkEditResource
from networkapi.ip.resource.NetworkRemoveResource import NetworkRemoveResource

from networkapi.ip.resource.Ipv4AssocEquipResource import Ipv4AssocEquipResource
from networkapi.ip.resource.Ipv6AssocEquipResource import Ipv6AssocEquipResource

from networkapi.requisicaovips.resource.RequestVipL7Resource import RequestVipL7Resource
from networkapi.requisicaovips.resource.RequestVipL7ValidateResource import RequestVipL7ValidateResource
from networkapi.requisicaovips.resource.RequestVipL7ApplyResource import RequestVipL7ApplyResource
from networkapi.requisicaovips.resource.RequestVipL7RollbackResource import RequestVipL7RollbackResource
from networkapi.requisicaovips.resource.RequisicaoVipsResource import RequisicaoVipsResource
from networkapi.requisicaovips.resource.RequisicaoVipDeleteResource import RequisicaoVipDeleteResource
from networkapi.requisicaovips.resource.RequestVipValidateResource import RequestVipValidateResource
from networkapi.requisicaovips.resource.RequestAllVipsResource import RequestAllVipsResource
from networkapi.requisicaovips.resource.RequestAllVipsIPv4Resource import RequestAllVipsIPv4Resource
from networkapi.requisicaovips.resource.RequestAllVipsIPv6Resource import RequestAllVipsIPv6Resource
from networkapi.requisicaovips.resource.RequestHealthcheckResource import RequestHealthcheckResource
from networkapi.requisicaovips.resource.RequestMaxconResource import RequestMaxconResource
from networkapi.requisicaovips.resource.RequestPriorityResource import RequestPriorityResource
from networkapi.requisicaovips.resource.RequestVipsResource import RequestVipsResource
from networkapi.requisicaovips.resource.RequestVipGetIdIpResource import RequestVipGetIdIpResource
from networkapi.requisicaovips.resource.RequestVipGetByIdResource import RequestVipGetByIdResource
from networkapi.requisicaovips.resource.CreateVipResource import CreateVipResource
from networkapi.requisicaovips.resource.RemoveVipResource import RemoveVipResource
from networkapi.requisicaovips.resource.OptionVipResource import OptionVipResource
from networkapi.requisicaovips.resource.OptionVipEnvironmentVipAssociationResource import OptionVipEnvironmentVipAssociationResource
from networkapi.requisicaovips.resource.OptionVipAllResource import OptionVipAllResource
from networkapi.requisicaovips.resource.OptionVipAllGetByEnvironmentVipResource import OptionVipAllGetByEnvironmentVipResource
from networkapi.requisicaovips.resource.RequestVipsRealResource import RequestVipsRealResource
from networkapi.requisicaovips.resource.RequestVipRealEditResource import RequestVipRealEditResource
from networkapi.requisicaovips.resource.RequestVipRealValidResource import RequestVipRealValidResource
from networkapi.requisicaovips.resource.RequestVipRuleResource import RequestVipRuleResource

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
from networkapi.grupo.resource.GrupoEquipamentoAssociaEquipamentoResource import GrupoEquipamentoAssociaEquipamentoResource
from networkapi.grupo.resource.GroupEquipmentResource import GroupEquipmentResource

from networkapi.grupo.resource.GroupUserGetAllResource import GroupUserGetAllResource
from networkapi.grupo.resource.GroupUserGetByIdResource import GroupUserGetByIdResource
from networkapi.grupo.resource.GroupUserAlterRemoveResource import GroupUserAlterRemoveResource
from networkapi.grupo.resource.GroupUserAddResource import GroupUserAddResource

from networkapi.interface.resource.InterfaceResource import InterfaceResource
from networkapi.interface.resource.InterfaceGetResource import InterfaceGetResource
from networkapi.interface.resource.InterfaceDisconnectResource import InterfaceDisconnectResource

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

from networkapi.requisicaovips.resource.OptionVipGetTimeoutByEVipResource import OptionVipGetTimeoutByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetGrupoCacheByEVipResource import OptionVipGetGrupoCacheByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetPersistenciaByEVipResource import OptionVipGetPersistenciaByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetBalanceamentoByEVipResource import OptionVipGetBalanceamentoByEVipResource
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
from networkapi.ambiente.resource.EnvironmentGetAclPathsResource import EnvironmentGetAclPathsResource
from networkapi.ambiente.resource.EnvironmentSetTemplateResource import EnvironmentSetTemplateResource


from networkapi.requisicaovips.resource.RequestVipGetRulesByEVipResource import RequestVipGetRulesByEVipResource
from networkapi.blockrules.resource.RuleResource import RuleResource
from networkapi.blockrules.resource.RuleGetResource import RuleGetResource
from networkapi.vlan.resource.VlanCheckNumberAvailable import VlanCheckNumberAvailable
from networkapi.ambiente.resource.EnvironmentConfigurationListResource import EnvironmentConfigurationListResource
from networkapi.ambiente.resource.EnvironmentConfigurationRemoveResource import EnvironmentConfigurationRemoveResource
from networkapi.requisicaovips.resource.OptionVipGetHealthcheckByEVipResource import OptionVipGetHealthcheckByEVipResource


check_action = CheckAction()


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

vlan_resource = VlanResource()
vlan_list_resource = VlanListResource()
vlan_search_resource = VlanSearchResource()
vlan_find_resource = VlanFindResource()
vlan_allocate_resource = VlanAllocateResource()
vlan_remove_resource = VlanRemoveResource()
vlan_deallocate_resource = VlanDeallocateResource()
vlan_allocate_ipv6_resource = VlanAllocateIPv6Resorce()
vlan_create_resource = VlanCreateResource()
vlan_insert_resource = VlanInsertResource()
vlan_edit_resource = VlanEditResource()
vlan_invalidate_resource = VlanInvalidateResource()
vlan_validate_resource = VlanValidateResource()
vlan_check_number_available_resource = VlanCheckNumberAvailable()
vlan_get_by_env_resource = VlanGetByEnvironmentResource()
vlan_apply_resource = VlanApplyAcl()
vlan_create_acl_resource = VlanCreateAclResource()
vlan_create_script_acl_resource = VlanCreateScriptAclResource()

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

equipment_resource = EquipamentoResource()

equipment_get_real_related = EquipmentGetRealRelated()

equipment_edit_resource = EquipamentoEditResource()

equipment_type_get_all_resource = EquipmentTypeGetAllResource()

equipment_type_add_resource = EquipmentTypeAddResource()

# brand_resource = MarcaResource()
brand_add_resource = BrandAddResource()
brand_alter_remove_resource = BrandAlterRemoveResource()
brand_get_all_resource = BrandGetAllResource()

# model_resource = ModeloResource()
model_add_resource = ModelAddResource()
model_alter_remove_resource = ModelAlterRemoveResource()
model_get_all_resource = ModelGetAllResource()
model_get_by_brand_resource = ModelGetByBrandResource()

equipment_group_resource = EquipamentoGrupoResource()
equipment_group_associa_resource = GrupoEquipamentoAssociaEquipamentoResource()
equipment_access_resource = EquipamentoAcessoResource()
equipment_access_list_resource = EquipAccessListResource()
equipment_script_list_resource = EquipScriptListResource()
equipment_access_get_resource = EquipAccessGetResource()
equipment_access_edit_resource = EquipAccessEditResource()
equipment_environment_resource = EquipamentoAmbienteResource()
equipment_list_resource = EquipmentListResource()
equipment_find_resource = EquipmentFindResource()
equipment_get_all_resource = EquipmentGetAllResource()
equipment_get_by_group_resource = EquipmentGetByGroupEquipmentResource()
equipment_environment_remove = EquipmentEnvironmentDeallocateResource()

environment_resource = AmbienteResource()
environment_list_resource = EnvironmentListResource()
environment_by_equip_resource = EnvironmentGetByEquipResource()
env_ip_conf_resource = EnvironmentIpConfigResource()

environment_get_by_id_resource = EnvironmentGetByIdResource()
environment_get_acl_paths_resource = EnvironmentGetAclPathsResource()

environment_set_template = EnvironmentSetTemplateResource()

environment_blocks = EnvironmentBlocks()

environment_configuration_add_resource = EnvironmentConfigurationAddResource()

environment_configuration_list_resource = EnvironmentConfigurationListResource()

environment_configuration_remove_resource = EnvironmentConfigurationRemoveResource()

environment_equip_resource = AmbienteEquipamentoResource()

division_dc_add_resource = DivisionDcAddResource()
division_dc_alter_remove_resource = DivisionDcAlterRemoveResource()
division_dc_get_all_resource = DivisionDcGetAllResource()

group_l3_add_resource = GroupL3AddResource()
group_l3_alter_remove_resource = GroupL3AlterRemoveResource()
group_l3_get_all_resource = GroupL3GetAllResource()

logical_environment_add_resource = LogicalEnvironmentAddResource()
logical_environment_alter_remove_resource = LogicalEnvironmentAlterRemoveResource()
logical_environment_get_all_resource = LogicalEnvironmentGetAllResource()

ip_resource = IpResource()
ipv4_get_resource = Ipv4GetByIdResource()
ipv6_get_resource = Ipv6GetByIdResource()
ipv4_add_resource = IPv4AddResource()
ipv6_add_resource = IPv6AddResource()
networkip4_get_resource = NetworkIPv4GetResource()
networkip6_get_resource = NetworkIPv6GetResource()
network_edit_resource = NetworkEditResource()
networkip4_list_ip_resource = IPv4ListResource()
networkip6_list_ip_resource = IPv6ListResource()
ip4_available_resource = IPv4GetAvailableResource()
ip6_available_resource = IPv6GetAvailableResource()
ip6_available_vip_resource = Ipv6GetAvailableForVipResource()
ip4_available_vip_resource = Ipv4GetAvailableForVipResource()
ipv4_save_resource = IPv4SaveResource()
ipv6_save_resource = IPv6SaveResource()
ipv4_delete_resource = IPv4DeleteResource()
ipv6_delete_resource = IPv6DeleteResource()
ipv4_edit_resource = IPv4EditResource()
ipv6_edit_resource = IPv6EditResource()
ipv4_get_by_id_resource = IPv4GetResource()
ip_equip_evip_resource = IPEquipEvipResource()
ip_get_by_oct_block = IpGetOctBlockResource()
ip_check_for_vip = IpCheckForVipResource()
ipv6_get_by_id_resource = IPv6GetResource()
ip_get_by_equip_resource = IPGetByEquipResource()

ipv4_assoc_equip_resource = Ipv4AssocEquipResource()
ipv6_assoc_equip_resource = Ipv6AssocEquipResource()

network_add_resource = NetworkAddResource()
network_remove_resource = NetworkRemoveResource()
network_ipv4_add_resource = NetworkIPv4AddResource()
network_ipv4_deallocate_resource = NetworkIPv4DeallocateResource()
network_ipv6_add_resource = NetworkIPv6AddResource()
network_ipv6_deallocate_resource = NetworkIPv6DeallocateResource()
ipv6_associate = Ipv6AssociateResource()
ipv6_remove = Ipv6RemoveResource()
search_ipv6_environment = SearchIPv6EnvironmentResource()

# equipment_script_resource = EquipamentoRoteiroResource()

equipment_script_add_resource = EquipmentScriptAddResource()
equipment_script_remove_resource = EquipmentScriptRemoveResource()
equipment_script_get_all_resource = EquipmentScriptGetAllResource()

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


vip_l7_resource = RequestVipL7Resource()
vip_l7_validate_resource = RequestVipL7ValidateResource()
vip_l7_apply_resource = RequestVipL7ApplyResource()
vip_l7_rollback_resource = RequestVipL7RollbackResource()
vip_add_block_resource = RequestVipRuleResource()
vip_request_resource = RequisicaoVipsResource()
vip_delete_resource = RequisicaoVipDeleteResource()
vip_validate_resource = RequestVipValidateResource()
vip_create_resource = CreateVipResource()
vip_remove_resource = RemoveVipResource()
vip_list_all_resource = RequestAllVipsResource()
vip_list_all_ipv4_resource = RequestAllVipsIPv4Resource()
vip_list_all_ipv6_resource = RequestAllVipsIPv6Resource()
vip_healthcheck_resource = RequestHealthcheckResource()
vip_maxcon = RequestMaxconResource()
vip_priority = RequestPriorityResource()
vip_request = RequestVipsResource()
vip_request_get_id = RequestVipGetByIdResource()
vip_request_get_ip_id = RequestVipGetIdIpResource()
vip_real = RequestVipsRealResource()
vip_real_edit = RequestVipRealEditResource()
vip_real_valid = RequestVipRealValidResource()
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

urlpatterns = patterns('',
                       # Example:
                       # (r'^networkapi/', include('networkapi.foo.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
                       # to INSTALLED_APPS to enable admin documentation:
                       # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # (r'^admin/(.*)', admin.site.root),
                       url(r'^vlan/$', vlan_resource.handle_request, name='vlan.allocate'),
                       url(r'^vlan/all/$', vlan_list_resource.handle_request, name='vlan.list.all'),
                       url(r'^vlan/find/$', vlan_find_resource.handle_request, name='vlan.find'),
                       url(r'^vlan/ipv6/$', vlan_allocate_ipv6_resource.handle_request, name='vlan.allocate.ipv6'),
                       url(r'^vlan/no-network/$', vlan_allocate_resource.handle_request, name='vlan.allocate.without.network'),
                       url(r'^vlan/(?P<operacao>list)/$', vlan_resource.handle_request, name='vlan.list'),
                       url(r'^vlan/insert/$', vlan_insert_resource.handle_request, name='vlan.insert'),
                       url(r'^vlan/edit/$', vlan_edit_resource.handle_request, name='vlan.edit'),
                       url(r'^vlan/create/$', vlan_edit_resource.handle_request, name='vlan.create'),
                       url(r'^vlan/(?P<id_vlan>[^/]+)/$', vlan_resource.handle_request, name='vlan.get.by.pk'),
                       url(r'^vlan/(?P<id_vlan>[^/]+)/remove/$', vlan_remove_resource.handle_request, name='vlan.remove.by.pk'),
                       url(r'^vlan/(?P<id_vlan>[^/]+)/network/$', vlan_search_resource.handle_request, name='vlan.network.get.by.pk'),
                       url(r'^vlan/(?P<id_vlan>[^/]+)/deallocate/$', vlan_deallocate_resource.handle_request, name='vlan.deallocate'),
                       url(r'^vlan/ambiente/(?P<id_ambiente>[^/]+)/$', vlan_get_by_env_resource.handle_request, name='vlan.search.by.environment'),
                       url(r'^vlan/(?P<id_vlan>[^/]+)/invalidate/(?P<network>v4|v6)/$', vlan_invalidate_resource.handle_request, name='vlan.invalidate'),
                       url(r'^vlan/(?P<id_vlan>[^/]+)/validate/(?P<network>v4|v6)/$', vlan_validate_resource.handle_request, name='vlan.validate'),
                       url(r'^vlan/(?P<id_vlan>[^/]+)/(?P<operacao>criar|add|del|check)/$', vlan_resource.handle_request, name='vlan.create.add.remove.check.validate'),
                       url(r'^vlan/v4/create/$', vlan_create_resource.handle_request, {'network_version': IP_VERSION.IPv4[0]}, name='vlan.create.v4'),
                       url(r'^vlan/v6/create/$', vlan_create_resource.handle_request, {'network_version': IP_VERSION.IPv6[0]}, name='vlan.create.v6'),
                       url(r'^vlan/confirm/(?P<number>[^/]+)/(?P<id_environment>[^/]+)/(?P<ip_version>[^/]+)/$', vlan_validate_resource.handle_request, name='vlan.confirm.vlan'),
                       url(r'^vlan/check_number_available/(?P<id_environment>[^/]+)/(?P<num_vlan>[^/]+)/(?P<id_vlan>[^/]+)/$', vlan_check_number_available_resource.handle_request, name='vlan.check.num.available'),
                       url(r'^vlan/apply/acl/$', vlan_apply_resource.handle_request, name='vlan.apply.acl'),
                       url(r'^tipoacesso/$', access_type_resource.handle_request, name='access_type.insert.search'),
                       url(r'^tipoacesso/(?P<id_tipo_acesso>[^/]+)/$', access_type_resource.handle_request, name='access_type.update.remove.by.pk'),
                       url(r'^vlan/create/acl/$', vlan_create_acl_resource.handle_request, name='vlan.create.acl'),
                       url(r'^vlan/create/script/acl/$', vlan_create_script_acl_resource.handle_request, name='vlan.create.script.acl'),


                       url(r'^equipamentoacesso/$', equipment_access_resource.handle_request, name='equipmentaccess.insert.search'),
                       url(r'^equipamentoacesso/id/(?P<id_acesso>[^/]+)/$', equipment_access_get_resource.handle_request, name='equipmentaccess.get.by.id'),
                       url(r'^equipamentoacesso/(?P<id_equipamento>[^/]+)/(?P<id_tipo_acesso>[^/]+)/$', equipment_access_resource.handle_request, name='equipmentaccess.update.remove.by.pk'),
                       url(r'^equipamentoacesso/name/$', equipment_access_list_resource.handle_request, name='equipmentaccess.list.by.name'),
                       url(r'^equipamentoacesso/edit/$', equipment_access_edit_resource.handle_request, name='equipmentaccess.edit.by.id'),

                       url(r'^net_type/$', network_type_resource.handle_request, name='network_type.insert.search'),
                       url(r'^net_type/(?P<id_net_type>[^/]+)/$', network_type_resource.handle_request, name='network_type.update.remove.by.pk'),


                       url(r'^equipamento/get_real_related/(?P<id_equip>[^/]+)/$', equipment_get_real_related.handle_request, name='equipment.get.real.related'),
                       url(r'^equipamento/$', equipment_resource.handle_request, name='equipment.insert'),
                       url(r'^equipamento/edit/(?P<id_equip>[^/]+)/$', equipment_edit_resource.handle_request, name='equipment.edit.by.pk'),
                       url(r'^equipamento/list/$', equipment_list_resource.handle_request, name='equipment.list.all'),
                       url(r'^equipamento/find/$', equipment_find_resource.handle_request, name='equipment.find'),
                       url(r'^equipamento/(?P<id_equip>[^/]+)/$', equipment_resource.handle_request, name='equipment.remove.by.pk'),
                       url(r'^equipamento/nome/(?P<nome_equip>[^/]+)/$', equipment_resource.handle_request, name='equipment.get.by.name'),
                       url(r'^equipamento/id/(?P<id_equip>[^/]+)/$', equipment_resource.handle_request, name='equipment.get.by.id'),
                       url(r'^equipamento/tipoequipamento/(?P<id_tipo_equip>[^/]+)/ambiente/(?P<id_ambiente>[^/]+)/$', equipment_resource.handle_request, name='equipment.search.by.equipment_type.environment'),
                       url(r'^equipment/all/$', equipment_get_all_resource.handle_request, name='equipment.get.all'),
                       url(r'^equipment/group/(?P<id_egroup>[^/]+)/$', equipment_get_by_group_resource.handle_request, name='equipment.get.by.group'),

                       url(r'^equipamentogrupo/$', equipment_group_resource.handle_request, name='equipmentgroup.insert'),
                       url(r'^equipamentogrupo/associa/$', equipment_group_associa_resource.handle_request, name='equipmentgroup.associa'),
                       url(r'^equipamentogrupo/equipamento/(?P<id_equip>[^/]+)/egrupo/(?P<id_egrupo>[^/]+)/$', equipment_group_resource.handle_request, name='equipmentgroup.remove'),

                       url(r'^equipamentoroteiro/name/$', equipment_script_list_resource.handle_request, name='equipmentscript.list.by.name'),

                       url(r'^equipmentscript/$', equipment_script_add_resource.handle_request, name='equipment_script.add'),
                       url(r'^equipmentscript/all/$', equipment_script_get_all_resource.handle_request, name='equipment_script.get.all'),
                       url(r'^equipmentscript/(?P<id_equipment>[^/]+)/(?P<id_script>[^/]+)/$', equipment_script_remove_resource.handle_request, name='equipment_script.remove'),

                       url(r'^equipmenttype/all/$', equipment_type_get_all_resource.handle_request, name='equipment_type.get.all'),
                       url(r'^equipmenttype/$', equipment_type_add_resource.handle_request, name='equipment_type.add'),

                       url(r'^equipamentoambiente/$', equipment_environment_resource.handle_request, name='equipmentenvironment.insert'),
                       url(r'^equipamentoambiente/update/$', equipment_environment_resource.handle_request, name='equipmentenvironment.update'),
                       url(r'^equipment/(?P<id_equipment>[^/]+)/environment/(?P<id_environment>[^/]+)/$', equipment_environment_remove.handle_request, name='equipmentenvironment.remove'),

                       url(r'^ambiente/$', environment_resource.handle_request, name='environment.search.insert'),
                       url(r'^ambiente/list/$', environment_list_resource.handle_request, name='environment.list.all'),
                       url(r'^ambiente/equip/(?P<id_equip>[^/]+)/$', environment_by_equip_resource.handle_request, name='environment.list.by.equip'),
                       url(r'^ambiente/ipconfig/$', environment_resource.handle_request, {'ip_config': True}, name='environment.insert.ipconfig'),
                       url(r'^ambiente/divisao_dc/(?P<id_divisao_dc>[^/]+)/$', environment_resource.handle_request, name='environment.search.by.divisao_dc'),
                       url(r'^ambiente/divisao_dc/(?P<id_divisao_dc>[^/]+)/ambiente_logico/(?P<id_amb_logico>[^/]+)/$', environment_resource.handle_request, name='environment.search.by.divisao_dc.logic_environment'),
                       url(r'^ambiente/equipamento/(?P<nome_equip>[^/]+)/ip/(?P<x1>\d{1,3})\.(?P<x2>\d{1,3})\.(?P<x3>\d{1,3})\.(?P<x4>\d{1,3})/$', environment_equip_resource.handle_request, name='environment.get.by.equipment_name.ip'),
                       url(r'^ambiente/(?P<id_ambiente>[^/]+)/$', environment_resource.handle_request, name="environment.search.update.remove.by.pk"),
                       url(r'^environment/id/(?P<environment_id>[^/]+)/$', environment_get_by_id_resource.handle_request, name="environment.search.by.pk"),
                       url(r'^environment/acl_path[/]$', environment_get_acl_paths_resource.handle_request, name="environment.acl_path"),
                       url(r'^environment/set_template/(?P<environment_id>[^/]+)/$', environment_set_template.handle_request, name="environment.set.template"),
                       url(r'^environment/get_env_template/$', environment_set_template.handle_request, name="environment.get.template"),


                       url(r'^environment/configuration/save/$', environment_configuration_add_resource.handle_request, name="environment.configuration.save"),
                       url(r'^environment/configuration/list/(?P<environment_id>[^/]+)/$', environment_configuration_list_resource.handle_request, name="environment.configuration.list"),
                       url(r'^environment/configuration/remove/(?P<environment_id>[^/]+)/(?P<configuration_id>[^/]+)/$', environment_configuration_remove_resource.handle_request, name="environment.configuration.remove"),

                       url(r'^environment/save_blocks/$', environment_blocks.handle_request, name="environment.save.blocks"),
                       url(r'^environment/update_blocks/$', environment_blocks.handle_request, name="environment.update.blocks"),
                       url(r'^environment/get_blocks/(?P<environment_id>[^/]+)/$', environment_blocks.handle_request, name="environment.get.blocks"),
                       url(r'^environment/list_no_blocks/$', environment_list_resource.handle_request, name='environment.list.no_blocks'),

                       url(r'^environment-vip/get/finality/$', environment_vip_finality.handle_request, name='environemnt-vip.get.finality'),
                       url(r'^environment-vip/get/cliente_txt/$', environment_vip_cliente_txt.handle_request, name='environemnt-vip.get.cliente_txt'),
                       url(r'^environment-vip/get/ambiente_p44_txt/$', environment_vip_ambientep44_txt.handle_request, name='environemnt-vip.get.ambientep44_txt'),
                       url(r'^environment-vip/get/timeout/(?P<id_evip>[^/]+)/$', opt_vip_timeout.handle_request, name='option-vip.get.timeout'),
                       url(r'^environment-vip/get/grupo-cache/(?P<id_evip>[^/]+)/$', opt_vip_grupocache.handle_request, name='option-vip.get.grupocache'),
                       url(r'^environment-vip/get/persistencia/(?P<id_evip>[^/]+)/$', opt_vip_persistencia.handle_request, name='option-vip.get.persistencia'),
                       url(r'^environment-vip/get/balanceamento/(?P<id_evip>[^/]+)/$', opt_vip_balanceamento.handle_request, name='option-vip.get.balanceamento'),
                       url(r'^environment-vip/get/rules/(?P<id_evip>[^/]+)(?:/(?P<id_vip>[^/]+))?/$', environment_vip_rules.handle_request, name='environment-vip.get.rules'),
                       url(r'^environment-vip/get/healthcheck/(?P<id_evip>[^/]+)/$', opt_vip_healthcheck.handle_request, name='environment-vip.get.healthcheck'),

                       url(r'^rule/get_by_id/(?P<id_rule>[^/]+)/$', rule_resource.handle_request, name='rule.get.by.id'),
                       url(r'^rule/all/(?P<id_env>[^/]+)/$', rule_get_resource.handle_request, name='rule.all'),
                       url(r'^rule/save/$', rule_resource.handle_request, name='rule.save'),
                       url(r'^rule/update/$', rule_resource.handle_request, name='rule.update'),
                       url(r'^rule/delete/(?P<id_rule>[^/]+)/$', rule_resource.handle_request, name='rule.delete'),

                       url(r'^ipconfig/$', env_ip_conf_resource.handle_request, name="ipconfig.associate"),

                       url(r'^divisiondc/$', division_dc_add_resource.handle_request, name='division_dc.add'),
                       url(r'^divisiondc/all/$', division_dc_get_all_resource.handle_request, name='division_dc.get.all'),
                       url(r'^divisiondc/(?P<id_divisiondc>[^/]+)/$', division_dc_alter_remove_resource.handle_request, name='division_dc.update.remove.by.pk'),

                       url(r'^groupl3/$', group_l3_add_resource.handle_request, name='group_l3.add'),
                       url(r'^groupl3/all/$', group_l3_get_all_resource.handle_request, name='group_l3.get.all'),
                       url(r'^groupl3/(?P<id_groupl3>[^/]+)/$', group_l3_alter_remove_resource.handle_request, name='group_l3.update.remove.by.pk'),

                       url(r'^logicalenvironment/$', logical_environment_add_resource.handle_request, name='logical_environment.add'),
                       url(r'^logicalenvironment/all/$', logical_environment_get_all_resource.handle_request, name='logical_environment.get.all'),
                       url(r'^logicalenvironment/(?P<id_logicalenvironment>[^/]+)/$', logical_environment_alter_remove_resource.handle_request, name='logical_environment.update.remove.by.pk'),

                       url(r'^ip/(?P<id_ip>[^/]+)/equipamento/(?P<id_equipamento>[^/]+)/$', ip_resource.handle_request, name='ipequipment.insert.remove'),
                       url(r'^ip/(?P<ip>.+)/ambiente/(?P<id_amb>[^/]+)/$', ip_resource.handle_request, name='ip.get.by.ip.environment'),
                       url(r'^ip/id_network_ipv4/(?P<id_rede>[^/]+)/', networkip4_list_ip_resource.handle_request, name='ip4.list.by.network'),
                       url(r'^ip/id_network_ipv6/(?P<id_rede>[^/]+)/', networkip6_list_ip_resource.handle_request, name='ip6.list.by.network'),
                       url(r'^ip/availableip6/vip/(?P<id_evip>[^/]+)/', ip6_available_vip_resource.handle_request, name='ip6.get.available.for.vip'),
                       url(r'^ip/availableip4/vip/(?P<id_evip>[^/]+)/', ip4_available_vip_resource.handle_request, name='ip4.get.available.for.vip'),
                       url(r'^ip/availableip4/(?P<id_rede>[^/]+)/', ip4_available_resource.handle_request, name='ip4.get.available'),
                       url(r'^ip/availableip6/(?P<id_rede>[^/]+)/', ip6_available_resource.handle_request, name='ip6.get.available'),
                       url(r'^ip/$', ip_resource.handle_request, name='ip.insert'),
                       url(r'^ip/get-ipv4/(?P<id_ip>[^/]+)/$', ipv4_get_resource.handle_request, name='ipv4.get.by.pk'),
                       url(r'^ip/get-ipv6/(?P<id_ip>[^/]+)/$', ipv6_get_resource.handle_request, name='ipv6.get.by.pk'),
                       url(r'^ip/get-ipv4/$', ip_resource.handle_request, name='ip.insert'),
                       url(r'^ip4/delete/(?P<id_ipv4>[^/]+)', ipv4_delete_resource.handle_request, name='ip4.delete'),
                       url(r'^ip4/edit', ipv4_edit_resource.handle_request, name="ip4.edit"),
                       url(r'^ipv6/edit', ipv6_edit_resource.handle_request, name="ip6.edit"),
                       url(r'^ip/get/(?P<id_ip>[^/]+)/', ipv4_get_by_id_resource.handle_request, name='ip4.get.by.id'),
                       url(r'^ip/getbyoctblock/', ip_get_by_oct_block.handle_request, name='ip.get.by.oct.or.block'),
                       url(r'^ip/checkvipip/', ip_check_for_vip.handle_request, name='ip.check.for.vip'),
                       url(r'^ip/getbyequipandevip/$', ip_equip_evip_resource.handle_request, name='ip.get.by.equip.and.evip'),
                       url(r'^ip/getbyequip/(?P<id_equip>[^/]+)/', ip_get_by_equip_resource.handle_request, name='ip.get.by.equip'),
                       url(r'^ipv6/get/(?P<id_ipv6>[^/]+)/', ipv6_get_by_id_resource.handle_request, name='ip6.get.by.id'),
                       url(r'^ipv6/delete/(?P<id_ipv6>[^/]+)', ipv6_delete_resource.handle_request, name='ip6.delete'),
                       url(r'^ipv4/$', ipv4_add_resource.handle_request, name='ipv4.insert'),
                       url(r'^ipv4/save/$', ipv4_save_resource.handle_request, name='ipv4.save'),
                       url(r'^ipv6/save/$', ipv6_save_resource.handle_request, name='ipv6.save'),
                       url(r'^ipv6/$', ipv6_add_resource.handle_request, name='ipv6.insert'),
                       url(r'^ipv6/(?P<id_ipv6>[^/]+)/equipment/(?P<id_equip>[^/]+)/$', ipv6_associate.handle_request, name='ipv6equipment.associate'),
                       url(r'^ipv6/(?P<id_ipv6>[^/]+)/equipment/(?P<id_equip>[^/]+)/remove/$', ipv6_remove.handle_request, name='ipv6equipment.remove'),
                       url(r'^ipv6/environment/$', search_ipv6_environment.handle_request, name='ipv6.get.by.ip.environment'),
                       url(r'^ipv4/assoc/$', ipv4_assoc_equip_resource.handle_request, name='ipv4.assoc.equip'),
                       url(r'^ipv6/assoc/$', ipv6_assoc_equip_resource.handle_request, name='ipv6.assoc.equip'),

                       url(r'^script/$', script_add_resource.handle_request, name='script.add'),
                       url(r'^script/all/$', script_get_all_resource.handle_request, name='script.get.all'),
                       url(r'^script/(?P<id_script>[^/]+)/$', script_alter_remove_resource.handle_request, name='script.update.remove.by.pk'),
                       url(r'^script/scripttype/(?P<id_script_type>[^/]+)/$', script_get_script_type_resource.handle_request, name='script.get.script_type'),
                       url(r'^script/equipment/(?P<id_equipment>[^/]+)/$', script_get_equipment_resource.handle_request, name='script.get.equipment'),

                       url(r'^scripttype/$', script_type_add_resource.handle_request, name='script_type.add'),
                       url(r'^scripttype/all/$', script_type_get_all_resource.handle_request, name='script_type.get.all'),
                       url(r'^scripttype/(?P<id_script_type>[^/]+)/$', script_type_alter_remove_resource.handle_request, name='script_type.update.remove.by.pk'),

                       url(r'^healthcheckexpect/ambiente/(?P<id_amb>[^/]+)/$', healthcheckexpect_resource.handle_request, name='healthcheckexpect.search.by.environment'),
                       url(r'^healthcheckexpect/add/$', healthcheckexpect_add_resource.handle_request, name='healthcheckexpect.add'),
                       url(r'^healthcheckexpect/add/expect_string/$', healthcheckexpect_string_resource.handle_request, name='healthcheckexpect.string.add'),
                       url(r'^healthcheckexpect/distinct/busca/$', healthcheckexpect_distinct_resource.handle_request, name='healthcheckexpect.distinct'),
                       url(r'^healthcheckexpect/get/(?P<id_healthcheck>[^/]+)/$', healthcheckexpect_get_resource.handle_request, name='healthcheckexpect.get.by.pk'),

                       url(r'^requestvip/$', vip_request.handle_request, name='requestvip.insert'),
                       url(r'^requestvip/get_by_ip_id/$', vip_request_get_ip_id.handle_request, name='requestvip.get.by.id.ip'),
                       url(r'^requestvip/getbyid/(?P<id_vip>[^/]+)/$', vip_request_get_id.handle_request, name='requestvip.get.by.pk'),
                       url(r'^requestvip/(?P<id_vip>[^/]+)/$', vip_request.handle_request, name='requestvip.update.by.pk'),
                       url(r'^vip/$', vip_request_resource.handle_request, name='vip.insert'),
                       url(r'^vip/all/$', vip_list_all_resource.handle_request, name='vip.list_all'),
                       url(r'^vip/ipv4/all/$', vip_list_all_ipv4_resource.handle_request, name='vip.ipv4.all'),
                       url(r'^vip/ipv6/all/$', vip_list_all_ipv6_resource.handle_request, name='vip.ipv6.all'),
                       url(r'^vip/create/$', vip_create_resource.handle_request, name='vip.create'),

                       url(r'^vip/(?P<id_vip>\d+)/criar/$', vip_create_resource.handle_request, name='vip.create.by.pk'),

                       url(r'^vip/remove/$', vip_remove_resource.handle_request, name='vip.remove'),
                       url(r'^vip/real/$', vip_real.handle_request, name='vip.real'),
                       url(r'^vip/(?P<id_vip>[^/]+)/filter/$', vip_l7_resource.handle_request, name='vip.get.l7.by.pk'),
                       url(r'^vip/(?P<id_vip>[^/]+)/$', vip_request_resource.handle_request, name='vip.get.update.by.pk'),
                       url(r'^vip/(?P<id_vip>[^/]+)/(?P<operacao>maxcon)/(?P<maxcon>[^/]+)/$', vip_maxcon.handle_request, name='vip.update.maxcon.by.pk'),
                       url(r'^vip/(?P<id_vip>[^/]+)/(?P<operacao>healthcheck)/$', vip_healthcheck_resource.handle_request, name='vip.update.healthcheck.by.pk'),
                       url(r'^vip/(?P<id_vip>[^/]+)/(?P<operacao>priority)/$', vip_priority.handle_request, name='vip.update.priority.by.pk'),
                       url(r'^vip/delete/(?P<id_vip>[^/]+)/$', vip_delete_resource.handle_request, name='vip.delete.by.pk'),
                       url(r'^vip/validate/(?P<id_vip>[^/]+)/$', vip_validate_resource.handle_request, name='vip.validate.by.pk'),
                       url(r'^vip/real/edit/$', vip_real_edit.handle_request, name='vip.real.edit'),
                       url(r'^vip/real/valid/$', vip_real_valid.handle_request, name='vip.real.valid'),
                       url(r'^vip/l7/(?P<id_vip>[^/]+)/$', vip_l7_resource.handle_request, name='vip.get.l7.by.pk'),
                       url(r'^vip/l7/(?P<id_vip>[^/]+)/validate/$', vip_l7_validate_resource.handle_request, name='vip.l7.validate.by.pk'),
                       url(r'^vip/l7/(?P<id_vip>[^/]+)/apply/$', vip_l7_apply_resource.handle_request, name='vip.l7.apply.by.pk'),
                       url(r'^vip/l7/(?P<id_vip>[^/]+)/rollback/$', vip_l7_rollback_resource.handle_request, name='vip.l7.rollback.by.pk'),

                       url(r'^vip/add_block/(?P<id_vip>\d+)/(?P<id_block>\d+)/(?P<override>\d+)[/]?$', vip_add_block_resource.handle_request, name='vip.add.block'),


                       url(r'^real/equip/(?P<id_equip>\d+)/vip/(?P<id_vip>\d+)/ip/(?P<id_ip>\d+)/$', vip_real.handle_request, name='vip.real.add.remove'),
                       url(r'^real/(?P<status>enable|disable|check)/equip/(?P<id_equip>\d+)/vip/(?P<id_vip>\d+)/ip/(?P<id_ip>\d+)/$', vip_real.handle_request, name='vip.real.enable.disable'),

                       url(r'^grupovirtual/$', virtual_group_resource.handle_request, name='virtual_group.add.remove'),

                       url(r'^brand/$', brand_add_resource.handle_request, name='brand.add'),
                       url(r'^brand/all/$', brand_get_all_resource.handle_request, name='brand.get.all'),
                       url(r'^brand/(?P<id_brand>[^/]+)/$', brand_alter_remove_resource.handle_request, name='brand.update.remove.by.pk'),

                       url(r'^model/$', model_add_resource.handle_request, name='model.add'),
                       url(r'^model/all/$', model_get_all_resource.handle_request, name='model.get.all'),
                       url(r'^model/(?P<id_model>[^/]+)/$', model_alter_remove_resource.handle_request, name='model.update.remove.by.pk'),
                       url(r'^model/brand/(?P<id_brand>[^/]+)/$', model_get_by_brand_resource.handle_request, name='model.get.by.brand'),

                       url(r'^interface/$', interface_resource.handle_request, name='interface.insert'),
                       url(r'^interface/(?P<id_interface>[^/]+)/$', interface_resource.handle_request, name='interface.update.remove.by.pk'),
                       url(r'^interface/(?P<id_interface>[^/]+)/get/$', interface_get_resource.handle_request, name='interface.get.by.pk'),
                       url(r'^interface/equipamento/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, name='interface.search.by.equipment'),
                       url(r'^interface/equipment/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, {'new': True}, name='interface.search.by.equipment.new'),
                       url(r'^interface/(?P<id_interface>[^/]+)/(?P<back_or_front>[^/]+)/$', interface_disconnect_resource.handle_request, name='interface.remove.connection'),
                       url(r'^interface/(?P<nome_interface>.+?)/equipamento/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, name='interface.search.by.interface.equipment'),
                       url(r'^interface/(?P<nome_interface>.+?)/equipment/(?P<id_equipamento>[^/]+)/$', interface_resource.handle_request, {'new': True}, name='interface.search.by.interface.equipment.new'),

                       url(r'^authenticate/$', authenticate_resource.handle_request, name='user.authenticate'),
                       url(r'^user/$', user_add_resource.handle_request, name='user.add'),
                       url(r'^usuario/get/$', user_get_resource.handle_request, name='user.list.with.group'),
                       url(r'^user-change-pass/$', user_change_pass_resource.handle_request, name='user.change.pass'),
                       url(r'^user/all/$', user_get_all_resource.handle_request, name='user.get.all'),
                       url(r'^user/(?P<id_user>[^/]+)/$', user_alter_remove_resource.handle_request, name='user.update.remove.by.pk'),
                       url(r'^user/get/(?P<id_user>[^/]+)/$', user_get_by_pk_resource.handle_request, name='user.get.by.id'),
                       url(r'^user/group/(?P<id_ugroup>[^/]+)/$', user_get_by_group_resource.handle_request, name='user.get.by.group'),
                       url(r'^user/out/group/(?P<id_ugroup>[^/]+)/$', user_get_by_group_out_group_resource.handle_request, name='user.get.by.group.out.group'),
                       url(r'^user/get/ldap/(?P<user_name>[^/]+)/$', user_get_by_ldap_resource.handle_request, name='user.get.ldap'),

                       url(r'^ugroup/all/$', ugroup_get_all_resource.handle_request, name='ugroup.get.all'),
                       url(r'^ugroup/get/(?P<id_ugroup>[^/]+)/$', ugroup_get_by_id_resource.handle_request, name='ugroup.get'),
                       url(r'^ugroup/$', ugroup_add_resource.handle_request, name='ugroup.add'),
                       url(r'^ugroup/(?P<id_ugroup>[^/]+)/$', ugroup_alter_remove_resource.handle_request, name='ugroup.alter.remove'),

                       url(r'^egrupo/$', egroup_resource.handle_request, name='egroup.search.insert'),
                       url(r'^egrupo/equipamento/(?P<id_equipamento>[^/]+)/egrupo/(?P<id_egrupo>[^/]+)/$', egroup_remove_association_equip_resource.handle_request, name='egroup.remove.equip.association'),
                       url(r'^egrupo/equip/(?P<id_equip>[^/]+)/$', egroup_get_by_equip_resource.handle_request, name='egroup.get.by.equip'),
                       url(r'^egrupo/(?P<id_grupo>[^/]+)/$', egroup_resource.handle_request, name='egroup.update.remove.by.pk'),
                       url(r'^egroup/(?P<id_egroup>[^/]+)/$', egroup_get_resource.handle_request, name='egroup.get.by.pk'),

                       url(r'^usergroup/user/(?P<id_user>[^/]+)/ugroup/(?P<id_group>[^/]+)/associate/$', user_group_associate_resource.handle_request, name='user_group.associate'),
                       url(r'^usergroup/user/(?P<id_user>[^/]+)/ugroup/(?P<id_group>[^/]+)/dissociate/$', user_group_dissociate_resource.handle_request, name='user_group.dissociate'),

                       url(r'^perms/all/$', perms_get_all_resource.handle_request, name='permission.get.all'),
                       url(r'^aperms/$', aperms_add_resource.handle_request, name='administrative.permission.add'),
                       url(r'^aperms/all/$', aperms_get_all_resource.handle_request, name='administrative.permission.get.all'),
                       url(r'^aperms/(?P<id_perm>[^/]+)/$', aperms_alter_remove_resource.handle_request, name='administrative.permission.update.remove.by.pk'),
                       url(r'^aperms/group/(?P<id_ugroup>[^/]+)/$', aperms_get_by_group.handle_request, name='administrative.permission.get.by.group'),
                       url(r'^aperms/get/(?P<id_perm>[^/]+)/$', aperms_get_by_pk_resource.handle_request, name='administrative.permission.get.by.pk'),

                       url(r'^direitosgrupoequipamento/$', access_right_resource.handle_request, name='access_right.search.insert'),
                       url(r'^direitosgrupoequipamento/ugrupo/(?P<id_grupo_usuario>[^/]+)/$', access_right_resource.handle_request, name='access_right.search.by.ugroup'),
                       url(r'^direitosgrupoequipamento/egrupo/(?P<id_grupo_equipamento>[^/]+)/$', access_right_resource.handle_request, name='access_right.search.by.egroup'),
                       url(r'^direitosgrupoequipamento/(?P<id_direito>[^/]+)/$', access_right_resource.handle_request, name='access_right.search.update.remove.by.pk'),

                       url(r'^check$', check_action.check, name='check'),

                       url(r'^network/ipv4/id/(?P<id_rede4>[^/]+)/$', networkip4_get_resource.handle_request, name='network.ip4.get.by.id'),
                       url(r'^network/ipv6/id/(?P<id_rede6>[^/]+)/$', networkip6_get_resource.handle_request, name='network.ip6.get.by.id'),
                       url(r'^network/add/$', network_add_resource.handle_request, name='network.add'),
                       url(r'^network/edit/$', network_edit_resource.handle_request, name='network.edit'),
                       url(r'^network/create/$', network_edit_resource.handle_request, name='network.create'),
                       url(r'^network/remove/$', network_remove_resource.handle_request, name='network.remove'),
                       url(r'^network/ipv4/add/$', network_ipv4_add_resource.handle_request, name='network.ipv4.add'),
                       url(r'^network/ipv4/(?P<id_network_ipv4>[^/]+)/deallocate/$', network_ipv4_deallocate_resource.handle_request, name='network.ipv4.deallocate'),
                       url(r'^network/ipv6/add/$', network_ipv6_add_resource.handle_request, name='network.ipv6.add'),
                       url(r'^network/ipv6/(?P<id_network_ipv6>[^/]+)/deallocate/$', network_ipv6_deallocate_resource.handle_request, name='network.ipv6.deallocate'),

                       url(r'^environmentvip/$', environment_vip_resource.handle_request, name='environment.vip.add'),
                       url(r'^environmentvip/all/', environment_vip_resource.handle_request, name='environment.vip.all'),
                       url(r'^environmentvip/search/$', environment_vip_search_resource.handle_request, name='environment.vip.search'),
                       url(r'^environmentvip/search/(?P<id_vlan>[^/]+)/$', environment_vip_search_resource.handle_request, name='environment.vip.search'),
                       url(r'^environmentvip/(?P<id_environment_vip>[^/]+)/$', environment_vip_resource.handle_request, name='environment.vip.update.remove'),
                       url(r'^environmentvip/(?P<id_environment_vip>[^/]+)/vip/all/$', environment_vip_search_all_vips_resource.handle_request, name='environmentvip.vips.all'),

                       url(r'^optionvip/all/$', option_vip_all.handle_request, name='option.vip.all'),
                       url(r'^optionvip/$', option_vip.handle_request, name='option.vip.add'),
                       url(r'^optionvip/(?P<id_option_vip>[^/]+)/$', option_vip.handle_request, name='option.vip.update.remove.search'),
                       url(r'^optionvip/(?P<id_option_vip>[^/]+)/environmentvip/(?P<id_environment_vip>[^/]+)/$', option_vip_environment_vip_association.handle_request, name='option.vip.environment.vip.associate.disassociate'),
                       url(r'^optionvip/environmentvip/(?P<id_environment_vip>[^/]+)/$', option_vip_environment_vip.handle_request, name='option.vip.by.environment.vip'),

                       url(r'^filter/all/$', filter_list_all.handle_request, name='filter.list.all'),
                       url(r'^filter/$', filter_add.handle_request, name='filter.add'),
                       url(r'^filter/(?P<id_filter>[^/]+)/$', filter_alter_remove.handle_request, name='filter.alter.remove'),
                       url(r'^filter/get/(?P<id_filter>[^/]+)/$', filter_get_by_id.handle_request, name='filter.get.by.id'),
                       url(r'^filter/(?P<id_filter>[^/]+)/equiptype/(?P<id_equiptype>[^/]+)/$', filter_associate.handle_request, name='filter.associate'),
                       url(r'^filter/(?P<id_filter>[^/]+)/dissociate/(?P<id_equip_type>[^/]+)/$', filter_dissociate_one.handle_request, name='filter.dissociate.one'),

                       url(r'^eventlog/find/$', eventlog_find_resource.handle_request, name='eventlog.find'),
                       url(r'^eventlog/choices/$', eventlog_choice_resource.handle_request, name='eventlog.choices'),
                       url(r'^eventlog/version/$', eventlog_find_resource.handle_request, name='eventlog.version'),
                       )


urlpatterns += patterns('networkapi.test_form.views',
                        url('^test-vip[/]?$',
                            'test_form',
                            name='test_form_vip',
                            ))
