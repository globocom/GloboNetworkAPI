# -*- coding: utf-8 -*-

import ast
import json
import logging
import operator
from netaddr import IPNetwork
from networkapi.rack.models import Rack
from networkapi.ambiente import models as models_env
from networkapi.vlan import models as models_vlan
from networkapi.api_environment import facade as facade_env
from networkapi.api_vlan.facade import v3 as facade_vlan_v3
from networkapi.api_network.facade.v3 import networkv4 as facade_redev4_v3
from networkapi.api_network.facade.v3 import networkv6 as facade_redev6_v3
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.equipamento.models import EquipamentoAmbienteDuplicatedError

log = logging.getLogger(__name__)


class RackEnvironment:

    def __init__(self, user, rack_id):
        self.rack = Rack().get_by_pk(rack_id)
        self.user = user
        self.dcroom_config = self._get_config_file()
        self.rack_asn = self._get_rack_asn()

    @staticmethod
    def save_environment(self, env):
        pass

    @staticmethod
    def save_vlan(self, vlan):
        pass

    def allocate(self):
        self.rack.__dict__.update(
            id=self.rack.id, create_vlan_amb=True)
        self.rack.save()

    def deallocate(self):
        self.rack.__dict__.update(
            id=self.rack.id, create_vlan_amb=False)
        self.rack.save()

    def spines_environment_save(self):
        log.debug("_create_spnlfenv")

        envfathers = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                        father_environment__isnull=True,
                                                        grupo_l3__nome=str(self.rack.dcroom.name),
                                                        ambiente_logico__nome="SPINES")
        log.debug("SPN environments" + str(envfathers))

        environment_spn_lf_list = list()
        spines = int(self.rack.dcroom.spines)
        fabric = self.rack.dcroom.name
        rackname = self.rack.nome
        grupoL3name = fabric+"_"+racknome

        try:
            id_grupo_l3 = models_env.GrupoL3().get_by_name(grupoL3name).id
        except:
            grupo_l3_dict = models_env.GrupoL3()
            grupo_l3_dict.nome = grupoL3name
            grupo_l3_dict.save()
            id_grupo_l3 = grupo_l3_dict.id
            pass

        for env in envfathers:
            config_subnet = list()
            for net in env.configs:
                # verificar se o ambiente possui range associado.
                cidr = IPNetwork(net.network)
                prefix = int(net.subnet_mask)
                network = {
                    'cidr': list(cidr.subnet(prefix)),
                    'type': net.ip_version,
                    'network_type': net.id_network_type.id
                }
                config_subnet.append(network)
            for spn in range(spines):
                amb_log_name = "SPINE0" + str(spn + 1) + "LEAF"
                try:
                    id_amb_log = models_env.AmbienteLogico().get_by_name(amb_log_name).id
                except:
                    amb_log_dict = models_env.AmbienteLogico()
                    amb_log_dict.nome = amb_log_name
                    amb_log_dict.save()
                    id_amb_log = amb_log_dict.id
                    pass
                config = list()
                subnet_index = (spn*int(self.rack.dcroom.racks))+int(self.rack.numero)
                for sub in config_subnet:
                    config_spn = {
                        'subnet': str(sub.get("cidr")[subnet_index]),
                        'network': str(sub.get("cidr")[subnet_index]),
                        'new_prefix': str(31) if str(sub.get("type"))[-1] is "4" else str(127),
                        'subnet_mask': str(31) if str(sub.get("type"))[-1] is "4" else str(127),
                        'type': str(sub.get("type")),
                        'ip_version': str(sub.get("type")),
                        'network_type': sub.get("network_type")
                    }
                    config.append(config_spn)
                obj = {
                    'grupo_l3': id_grupo_l3,
                    'ambiente_logico': id_amb_log,
                    'divisao_dc': env.divisao_dc.id,
                    'acl_path': env.acl_path,
                    'ipv4_template': env.ipv4_template,
                    'ipv6_template': env.ipv6_template,
                    'link': env.link,
                    'min_num_vlan_2': env.min_num_vlan_1+subnet_index,
                    'max_num_vlan_2': env.min_num_vlan_1+subnet_index,
                    'min_num_vlan_1': env.min_num_vlan_1+subnet_index,
                    'max_num_vlan_1': env.min_num_vlan_1+subnet_index,
                    'vrf': env.vrf,
                    'father_environment': env.id,
                    'default_vrf': env.default_vrf.id,
                    'configs': config,
                    'fabric_id': self.rack.dcroom.id
                }
                environment = facade_env.create_environment(obj)
                
        return environment_spn_lf_list

    def spines_environment_read(self):
        pass

    def spine_leaf_vlans_save(self):
        log.debug("_create_spnlfvlans")

        spn_lf_envs = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                         grupo_l3__nome=str(self.rack.dcroom.name),
                                                         ambiente_logico__nome__in=["SPINE01LEAF",
                                                                                    "SPINE02LEAF",
                                                                                    "SPINE03LEAF",
                                                                                    "SPINE04LEAF"])
        log.debug("SPN environments" + str(spn_lf_envs))

        tipo_rede = "Ponto a ponto"
        try:
            id_network_type = models_vlan.TipoRede().get_by_name(tipo_rede).id
        except:
            network_type = models_vlan.TipoRede()
            network_type.tipo_rede = tipo_rede
            network_type.save()
            id_network_type = network_type.id
            pass

        for env in spn_lf_envs:

            obj = {
                'name': "VLAN_" + env.divisao_dc.nome + "_" + env.ambiente_logico.nome + "_" + self.rack.nome,
                'environment': env.id,
                'default_vrf': env.default_vrf.id,
                'vrf': env.vrf,
                'create_networkv4': None,
                'create_networkv6': None,
                'description': "Vlan spinexleaf do rack " + self.rack.nome

            }
            vlan = facade_vlan_v3.create_vlan(obj, self.user)

            log.debug("Vlan allocated: " + str(vlan))

            for config in env.configs:
                log.debug("Configs: " + str(config))
                network = dict(prefix=config.subnet_mask,
                               cluster_unit=None,
                               vlan=vlan.id,
                               network_type=id_network_type,
                               environmentvip=None)
                log.debug("Network allocated: " + str(network))
                if str(config.ip_version)[-1] is "4":
                    facade_redev4_v3.create_networkipv4(network, self.user)
                elif str(config.ip_version)[-1] is "6":
                    facade_redev6_v3.create_networkipv6(network, self.user)

    def spine_leaf_vlans_read(self):
        pass

    def leaf_leaf_vlans_save(self):
        log.debug("_create_lflf_vlans")

        env_lf = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                    grupo_l3__nome=str(self.rack.nome),
                                                    ambiente_logico__nome="LEAF-LEAF")
        log.debug("Leaf-leaf environments: " + str(env_lf))

        tipo_rede = "Ponto a ponto"
        try:
            id_network_type = models_vlan.TipoRede().get_by_name(tipo_rede).id
        except:
            network_type = models_vlan.TipoRede()
            network_type.tipo_rede = tipo_rede
            network_type.save()
            id_network_type = network_type.id
            pass

        for env in env_lf:
            env_id = env.id
            vlan_number = int(env.min_num_vlan_1)
            vlan_name = "VLAN_LFxLF_" + env.divisao_dc.nome + "_" + env.grupo_l3.nome

            try:
                models_vlan.Vlan.objects.all().filter(nome=vlan_name).uniqueResult()
            except:
                log.debug("debug lfxlf")
                for net in env.configs:
                    bloco = net.network
                    prefix = bloco.split('/')[-1]
                    network = {
                        'prefix': prefix,
                        'network_type': id_network_type
                    }
                    if str(net.ip_version)[-1] is "4":
                        create_networkv4 = network
                    elif str(net.ip_version)[-1] is "6":
                        create_networkv6 = network
                obj = {
                    'name': vlan_name,
                    'num_vlan': vlan_number,
                    'environment': env_id,
                    'default_vrf': env.default_vrf.id,
                    'vrf': env.vrf,
                    'create_networkv4': create_networkv4 if create_networkv4 else None,
                    'create_networkv6': create_networkv6 if create_networkv6 else None
                }
                facade_vlan_v3.create_vlan(obj, self.user)

    def leaf_leaf_envs_save(self):
        log.debug("_create_lflf_envs")

        env_lf = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                    grupo_l3__nome=str(self.rack.dcroom.name),
                                                    ambiente_logico__nome="LEAF-LEAF")
        log.debug("Leaf-leaf environments: " + str(env_lf))

        try:
            id_l3 = models_env.GrupoL3().get_by_name(self.rack.nome).id
        except:
            l3_dict = models_env.GrupoL3()
            l3_dict.nome = self.rack.nome
            l3_dict.save()
            id_l3 = l3_dict.id
            pass

        for env in env_lf:
            config_subnet = []
            for net in env.configs:
                cidr = list(IPNetwork(net.network).subnet(int(net.subnet_mask)))[self.rack.numero]
                network = {
                    'network': str(cidr),
                    'ip_version': str(net.ip_version),
                    'network_type': int(net.id_network_type.id),
                    'subnet_mask': int(net.subnet_mask)
                }
                config_subnet.append(network)

            obj = {
                'grupo_l3': id_l3,
                'ambiente_logico': env.ambiente_logico.id,
                'divisao_dc': env.divisao_dc.id,
                'acl_path': env.acl_path,
                'ipv4_template': env.ipv4_template,
                'ipv6_template': env.ipv6_template,
                'link': env.link,
                'min_num_vlan_2': env.min_num_vlan_1,
                'max_num_vlan_2': env.max_num_vlan_1,
                'min_num_vlan_1': env.min_num_vlan_1,
                'max_num_vlan_1': env.max_num_vlan_1,
                'vrf': env.vrf,
                'father_environment': env.id,
                'default_vrf': env.default_vrf.id,
                'configs': config_subnet,
                'fabric_id': self.rack.dcroom.id
            }
            environment = facade_env.create_environment(obj)
            log.debug("Environment object: %s" % str(environment))

    def prod_environment_save(self):
        log.debug("_create_prod_envs")

        prod_envs = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                       grupo_l3__nome=str(self.rack.dcroom.name),
                                                       ambiente_logico__nome="PRODUCAO"
                                                       ).exclude(divisao_dc__nome="BO_DMZ")

        log.debug("PROD environments: " + str(prod_envs))

        try:
            id_grupo_l3 = models_env.GrupoL3().get_by_name(self.rack.nome).id
        except:
            grupo_l3_dict = models_env.GrupoL3()
            grupo_l3_dict.nome = self.rack.nome
            grupo_l3_dict.save()
            id_grupo_l3 = grupo_l3_dict.id
            pass

        fabricconfig = self.dcroom_config

        environment = list()
        for env in prod_envs:
            details = None
            for fab in fabricconfig.get("Ambiente"):
                if int(fab.get("id")) == env.id:
                    details = fab.get("details")

            config_subnet = list()
            for net in env.configs:

                if isinstance(details, list) and len(details) > 0:
                    if details[0].get(str(net.ip_version)):
                        new_prefix = details[0].get(str(net.ip_version)).get("new_prefix")
                    else:
                        new_prefix = 27 if net.ip_version == "v4" else 64
                    network = {
                        'ip_version': net.ip_version,
                        'network_type': net.id_network_type.id,
                        'subnet_mask': new_prefix
                    }
                    config_subnet.append(network)

            obj = {
                'grupo_l3': id_grupo_l3,
                'ambiente_logico': env.ambiente_logico.id,
                'divisao_dc': env.divisao_dc.id,
                'acl_path': env.acl_path,
                'ipv4_template': env.ipv4_template,
                'ipv6_template': env.ipv6_template,
                'link': env.link,
                'min_num_vlan_2': env.min_num_vlan_1,
                'max_num_vlan_2': env.max_num_vlan_1,
                'min_num_vlan_1': env.min_num_vlan_1,
                'max_num_vlan_1': env.max_num_vlan_1,
                'vrf': env.vrf,
                'father_environment': env.id,
                'default_vrf': env.default_vrf.id,
                'configs': config_subnet,
                'fabric_id': self.rack.dcroom.id
            }
            obj_env = facade_env.create_environment(obj)
            environment.append(obj_env)
            log.debug("Environment Prod. object: %s" % str(obj_env))

            for switch in [self.rack.id_sw1, self.rack.id_sw2]:
                try:
                    equipamento_ambiente = EquipamentoAmbiente()
                    equipamento_ambiente.ambiente = obj_env
                    equipamento_ambiente.equipamento = switch
                    equipamento_ambiente.is_router = True
                    equipamento_ambiente.create(self.user)
                except EquipamentoAmbienteDuplicatedError:
                    pass

        return environment

    def children_prod_environment_save(self):
        log.debug("_create_prod_children")

        try:
            env = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                     divisao_dc__nome="BE",
                                                     grupo_l3__nome=str(self.rack.nome),
                                                     ambiente_logico__nome="PRODUCAO"
                                                     ).uniqueResult()
            log.debug("BE environments: %s" % env)
        except Exception as e:
            raise Exception("Erro: %s" % e)

        fabricconfig = self.dcroom_config

        environment = None
        father_id = env.id
        fabenv = None

        for fab in fabricconfig.get("Ambiente"):
            if int(fab.get("id")) == int(env.father_environment.id):
                fabenv = fab.get("details")

        if not fabenv:
            log.debug("No configurations for child environment of env id=%s" % (
                str(env.id)))
            return False

        fabenv.sort(key=operator.itemgetter('min_num_vlan_1'))
        log.debug("Order by min_num_vlan: %s" % str(fabenv))

        for amb in fabenv:
            log.debug("amb: %s" % amb)
            try:
                id_div = models_env.DivisaoDc().get_by_name(amb.get("name")).id
            except:
                div_dict = models_env.DivisaoDc()
                div_dict.nome = amb.get("name")
                div_dict.save()
                id_div = div_dict.id
                pass

            config_subnet = list()
            for net_dict in amb.get("config"):
                network = {
                    'ip_version': net_dict.get("type"),
                    'network_type': int(net_dict.get("network_type")),
                    'subnet_mask': int(net_dict.get("new_prefix")),
                    'network_mask': int(net_dict.get("mask"))
                }
                config_subnet.append(network)
            log.debug("config: %s" % config_subnet)
            obj = {
                'grupo_l3': env.grupo_l3.id,
                'ambiente_logico': env.ambiente_logico.id,
                'divisao_dc': id_div,
                'acl_path': env.acl_path,
                'ipv4_template': env.ipv4_template,
                'ipv6_template': env.ipv6_template,
                'link': env.link,
                'min_num_vlan_2': amb.get("min_num_vlan_1"),
                'max_num_vlan_2': amb.get("max_num_vlan_1"),
                'min_num_vlan_1': amb.get("min_num_vlan_1"),
                'max_num_vlan_1': amb.get("max_num_vlan_1"),
                'vrf': env.vrf,
                'father_environment': father_id,
                'default_vrf': env.default_vrf.id,
                'configs': config_subnet,
                'fabric_id': self.rack.dcroom.id
            }
            environment = facade_env.create_environment(obj)
            log.debug("Environment object: %s" % str(environment))

            for switch in [self.rack.id_sw1, self.rack.id_sw2]:
                try:
                    equipamento_ambiente = EquipamentoAmbiente()
                    equipamento_ambiente.ambiente = environment
                    equipamento_ambiente.equipamento = switch
                    equipamento_ambiente.is_router = True
                    equipamento_ambiente.create(self.user)
                except EquipamentoAmbienteDuplicatedError:
                    pass
                except Exception as e:
                    log.debug("error %s" % e)

        return environment

    def manage_vlan_save(self):
        log.debug("_create_oobvlans")

        env_oob = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                     divisao_dc__nome="OOB",
                                                     grupo_l3__nome=str(self.rack.dcroom.name),
                                                     ambiente_logico__nome="GERENCIA").uniqueResult()
        log.debug("OOB environments: " + str(env_oob))

        for env in [env_oob]:

            obj = {
                'name': "VLAN_" + env.ambiente_logico.nome + "_" + self.rack.nome,
                'environment': env.id,
                'default_vrf': env.default_vrf.id,
                'vrf': env.vrf,
                'create_networkv4': None,
                'create_networkv6': None,
                'description': "Vlan de gerência do rack " + self.rack.nome

            }
            vlan = facade_vlan_v3.create_vlan(obj, self.user)

            log.debug("Vlan allocated: " + str(vlan))

            network = dict()
            for config in env.configs:
                log.debug("Configs: " + str(config))
                network = dict(prefix=config.subnet_mask,
                               cluster_unit=None,
                               vlan=vlan.id,
                               network_type=config.id_network_type.id,
                               environmentvip=None)
                log.debug("Network allocated: " + str(network))
            facade_redev4_v3.create_networkipv4(network, self.user)

        return vlan

    def rack_environment_remove(self):
        log.info("_remove_envs")

        envs_racks = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                  grupo_l3__nome=str(self.rack.nome))

        log.debug("PROD RACK environments to be removed: %s. Total: %s" % (str(envs_racks), len(envs_racks)))

        for env in envs_racks:
            env.delete_v3()

        log.debug("PROD RACK environments removed.")

        envs_spines = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id),
                                                     grupo_l3__nome=str(rack.dcroom.name),
                                                     ambiente_logico__nome__in=["SPINE01LEAF",
                                                                                "SPINE02LEAF",
                                                                                "SPINE03LEAF",
                                                                                "SPINE04LEAF"])

        log.debug("PROD SPINELEAF environments to be removed: %s. Total: %s" % (str(envs_spines), len(envs_spines)))

        for env in envs_spines:
            env.delete_v3()

        log.debug("PROD SPINELEAF environments removed.")

    def rack_vlans_remove(self):
        log.info("remove_vlans")

        vlans = models_vlan.Vlan.objects.filter(nome__icontains="_"+self.rack.nome)

        for vlan in vlans:
            vlan.delete_v3()

        log.debug("Vlans: %s. total: %s" % (vlans, len(vlans)))

    def rack_asn_remove(self):
        from networkapi.api_asn.models import Asn
        from networkapi.api_asn.v4 import facade

        if self.rack_asn:
            asn = facade.get_as_by_asn(self.rack_asn)
            asn_equipment = facade.get_as_equipment_by_asn([asn])
            log.debug(asn_equipment)
            for obj in asn_equipment:
                obj.delete_v4()

            Asn.delete_as([asn])

    def create_asn_equipment(self):
        from networkapi.api_asn.v4 import facade

        if self.rack_asn:
            try:
                asn_obj = dict(name=self.rack_asn, description=self.rack.nome)
                asn = facade.create_as(asn_obj)

                obj = dict(asn=asn.id, equipment=[self.rack.id_sw1.id,
                                                  self.rack.id_sw2.id,
                                                  self.rack.id_ilo.id])
                facade.create_asn_equipment(obj)
            except Exception as e:
                log.debug("Error while trying to create the asn %s for rack %s. "
                          "E: %s" % (self.rack_asn, self.rack.nome, e))

    def _get_rack_asn(self):

        if self.dcroom_config:
            BGP = self.dcroom_config.get("BGP")
            BASE_AS_LFS = int(BGP.get("leafs"))
            rack_as = BASE_AS_LFS + self.rack.numero

            if rack_as:
                return rack_as
            else:
                return None

    def _get_config_file(self):

        fabricconfig = self.rack.dcroom.config

        try:
            fabricconfig = json.loads(fabricconfig)
            log.debug("type -ast: %s" % str(type(fabricconfig)))
        except:
            pass

        try:
            fabricconfig = ast.literal_eval(fabricconfig)
            log.debug("config -ast: %s" % str(fabricconfig))
        except:
            pass

        if fabricconfig:
            return fabricconfig
        else:
            log.debug("sem configuracoes do fabric %s" % str(self.rack.dcroom.id))
            return list()
