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

        try:
            id_grupo_l3 = models_env.GrupoL3().get_by_name(fabric).id
        except:
            grupo_l3_dict = models_env.GrupoL3()
            grupo_l3_dict.nome = fabric
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
                for sub in config_subnet:
                    config_spn = {
                        'subnet': str(sub.get("cidr")[spn]),
                        'new_prefix': str(31) if str(sub.get("type"))[-1] is "4" else str(127),
                        'type': str(sub.get("type")),
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
                    'min_num_vlan_2': env.min_num_vlan_2,
                    'max_num_vlan_2': env.max_num_vlan_2,
                    'min_num_vlan_1': env.min_num_vlan_1,
                    'max_num_vlan_1': env.max_num_vlan_1,
                    'vrf': env.vrf,
                    'father_environment': env.id,
                    'default_vrf': env.default_vrf.id,
                    'configs': config,
                    'fabric_id': self.rack.dcroom.id
                }

        return environment_spn_lf_list

    def spines_environment_read(self):
        pass

    def spine_leaf_vlans_save(self):
        log.debug("_create_spnlfvlans")

        spn_lf_envs = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                         father_environment__isnull=False,
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
                                                    father_environment__isnull=True,
                                                    grupo_l3__nome=str(self.rack.dcroom.name),
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
                    bloco = net.ip_config.subnet
                    prefix = bloco.split('/')[-1]
                    network = {
                        'prefix': prefix,
                        'network_type': id_network_type
                    }
                    if str(net.ip_config.type)[-1] is "4":
                        create_networkv4 = network
                    elif str(net.ip_config.type)[-1] is "6":
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

        if self.rack.dcroom.config:
            fabricconfig = self.rack.dcroom.config
        else:
            log.debug("sem configuracoes do fabric %s" % str(self.rack.dcroom.id))
            fabricconfig = list()

        try:
            fabricconfig = json.loads(fabricconfig)
        except:
            pass

        try:
            fabricconfig = ast.literal_eval(fabricconfig)
            log.debug("config -ast: %s" % str(fabricconfig))
        except:
            pass

        environment = []
        for env in prod_envs:

            father_id = env.id

            details = None
            for fab in fabricconfig.get("Ambiente"):
                if int(fab.get("id")) == int(father_id):
                    details = fab.get("details")

            config_subnet = []
            for net in env.configs:
                cidr = IPNetwork(str(net.network))
                prefix = int(net.subnet_mask)
                subnet_list = list(cidr.subnet(int(prefix)))
                # try:
                #     bloco = subnet_list[int(self.rack.numero)]
                # except IndexError:
                #     msg = "Rack number %d is greater than the maximum number of " \
                #           "subnets available with prefix %d from %s subnet" % \
                #           (self.rack.numero, prefix, cidr)
                #     raise Exception(msg)

                if isinstance(details, list) and len(details) > 0:
                    if details[0].get(str(net.ip_version)):
                        new_prefix = details[0].get(str(net.ip_version)).get("new_prefix")
                    else:
                        new_prefix = 31 if net.ip_version == "v4" else 127
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
                'father_environment': father_id,
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

        if self.rack.dcroom.config:
            fabricconfig = self.rack.dcroom.config
        else:
            log.debug("No fabric configurations %s" % str(self.rack.dcroom.id))
            fabricconfig = list()

        try:
            fabricconfig = json.loads(fabricconfig)
            fabricconfig = ast.literal_eval(fabricconfig)
            log.debug("config -ast: %s" % str(fabricconfig))
        except:
            log.debug("Error loading fabric json.")

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

        for idx, amb in enumerate(fabenv):
            log.debug("amb: %s" % amb)
            try:
                id_div = models_env.DivisaoDc().get_by_name(amb.get("name")).id
            except:
                div_dict = models_env.DivisaoDc()
                div_dict.nome = amb.get("name")
                div_dict.save()
                id_div = div_dict.id
                pass

            config_subnet = []
            for net in env.configs:
                for net_dict in amb.get("config"):
                    if net_dict.get("type") == net.ip_version:
                        cidr = IPNetwork(net.network)
                        prefixo = net_dict.get("mask")
                        initial_prefix = 20 if net.ip_version == "v4" else 56

                        if not idx:
                            bloco = list(cidr.subnet(int(prefixo)))[0]
                            log.debug(str(bloco))
                        else:
                            bloco1 = list(cidr.subnet(int(initial_prefix)))[1]
                            bloco = list(bloco1.subnet(int(prefixo)))[int(idx) - 1]
                            log.debug(str(bloco))
                        network = {
                            'ip_version': str(net.ip_version),
                            'network_type': int(net.id_network_type.id),
                            'subnet_mask': int(net_dict.get("new_prefix")),
                            'network': str(bloco)
                        }
                        config_subnet.append(network)

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

        envs = models_env.Ambiente.objects.filter(dcroom=int(self.rack.dcroom.id),
                                                  grupo_l3__nome=str(self.rack.nome))

        for env in envs:
            env.delete_v3()

        log.debug("PROD environments: %s. Total: %s" % (str(envs), len(envs)))

    def rack_vlans_remove(self):
        log.info("remove_vlans")

        vlans = models_vlan.Vlan.objects.filter(nome__icontains="_"+self.rack.nome)

        for vlan in vlans:
            vlan.delete_v3()

        log.debug("Vlans: %s. total: %s" % (vlans, len(vlans)))
