# -*- coding: utf-8 -*-

import ast
import json
import logging
import operator
import re
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from netaddr import IPNetwork
from networkapi.rack.models import Rack, RackConfigError
from networkapi.ambiente import models as models_env
from networkapi.vlan import models as models_vlan
from networkapi.system.facade import get_value as get_variable
from networkapi.system import exceptions as var_exceptions

log = logging.getLogger(__name__)


class Provision:

    def __init__(self, rack_id):
        self.rack = Rack().get_by_pk(rack_id)
        self.spine_prefix = "SPN"
        self.leaf_prefix = "LF-"
        self.oob_prefix = "OOB"

    @staticmethod
    def replace_file(filein, fileout, dicionario):

        try:
            # Read contents from file as a single string
            file_handle = open(filein, 'r')
            file_string = file_handle.read()
            file_handle.close()
        except Exception as e:
            log.error("Erro abrindo roteiro: %s. Error: %s" % (str(filein), e))
            raise RackConfigError(None, None, "Erro abrindo roteiro: %s." % str(filein))

        try:
            for key in dicionario:
                # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
                log.debug("variavel: %s, valor: %s" % (str(key), str(dicionario[key])))
                file_string = (re.sub(key, dicionario[key], file_string))
        except Exception as e:
            log.error("Erro atualizando as variáveis no roteiro: %s. Error: %s" % (filein, e))
            raise RackConfigError(None, None, "Erro atualizando as variáveis no roteiro: %s." % filein)

        try:
            # Write contents to file.
            # Using mode 'w' truncates the file.
            file_handle = open(fileout, 'w')
            file_handle.write(file_string)
            file_handle.close()
        except Exception as e:
            log.error("Erro salvando arquivo de configuração: %s. Error: %s" % (fileout, e))
            raise RackConfigError(None, None, "Erro salvando arquivo de configuração: %s." % fileout)

    @staticmethod
    def split_network(net, bloco, posicao):
        subnets = list(net.subnet(bloco))
        return subnets[posicao]

    def spine_provision(self, rack, equips):

        log.info("AutoprovisionSPN-LF")

        numero_rack = self.rack.numero

        IPSPINEipv4 = dict()
        IPSPINEipv6 = dict()
        IPLEAFipv4 = dict()
        IPLEAFipv6 = dict()
        IPSIBGPipv4 = dict()
        IPSIBGPipv6 = dict()
        ASLEAF = dict()

        PODSBEipv4 = dict()
        redesPODSBEipv4 = dict()

        subnetsRackBEipv4 = dict()

        PODSBEipv6 = dict()
        redesPODSBEipv6 = dict()
        PODSBEFEipv6 = dict()
        redesPODSBEFEipv6 = dict()
        PODSBEBOipv6 = dict()
        redesPODSBEBOipv6 = dict()
        PODSBECAipv6 = dict()
        redesPODSBECAipv6 = dict()
        redesHostsipv6 = dict()
        redeHostsBEipv6 = dict()
        redeHostsFEipv6 = dict()
        redeHostsBOipv6 = dict()
        redeHostsCAipv6 = dict()
        redeHostsFILERipv6 = dict()

        redesPODSFEipv4 = dict()
        redesPODSFEipv6 = dict()

        VLANBELEAF = dict()
        VLANFELEAF = dict()
        VLANBORDALEAF = dict()
        VLANBORDACACHOSLEAF = dict()
        VLANBORDACACHOSBLEAF = dict()

        IPSPINEipv4[numero_rack] = list()
        IPSPINEipv6[numero_rack] = list()
        IPLEAFipv4[numero_rack] = list()
        IPLEAFipv6[numero_rack] = list()
        IPSIBGPipv4[numero_rack] = list()
        IPSIBGPipv6[numero_rack] = list()
        VLANBELEAF[numero_rack] = list()
        VLANFELEAF[numero_rack] = list()
        VLANBORDALEAF[numero_rack] = list()
        VLANBORDACACHOSLEAF[numero_rack] = list()
        VLANBORDACACHOSBLEAF[numero_rack] = list()
        ASLEAF[numero_rack] = list()

        PODSBEipv4[numero_rack] = list()
        redesPODSBEipv4[numero_rack] = list()

        subnetsRackBEipv4[numero_rack] = list()

        PODSBEipv6[numero_rack] = list()
        redesPODSBEipv6[numero_rack] = list()
        PODSBEFEipv6[numero_rack] = list()
        redesPODSBEFEipv6[numero_rack] = list()
        PODSBEBOipv6[numero_rack] = list()
        redesPODSBEBOipv6[numero_rack] = list()
        PODSBECAipv6[numero_rack] = list()
        redesPODSBECAipv6[numero_rack] = list()
        redesHostsipv6[numero_rack] = list()
        redeHostsBEipv6[numero_rack] = list()
        redeHostsFEipv6[numero_rack] = list()
        redeHostsBOipv6[numero_rack] = list()
        redeHostsCAipv6[numero_rack] = list()
        redeHostsFILERipv6[numero_rack] = list()
        redesPODSFEipv4[numero_rack] = list()
        redesPODSFEipv6[numero_rack] = list()

        variablestochangespine1 = dict()
        variablestochangeleaf1 = dict()

        VLANBE = None
        VLANFE = None
        VLANBORDA = None
        VLANBORDACACHOS = None
        VLANBORDACACHOSB = None

        CIDRBEipv4 = list()
        CIDRBO_DSRipv4interno = None
        CIDRBO_DSRipv6interno = None
        CIDRBOCAAipv4interno = None

        CIDRBEipv6 = list()
        CIDRBOCAAipv6interno = None
        CIDRBOCABipv4interno = None
        CIDRBOCABipv6interno = None

        try:
            path_to_guide = get_variable("path_to_guide")
            path_to_add_config = get_variable("path_to_add_config")
            path_to_config = get_variable("path_to_config")
        except ObjectDoesNotExist:
            raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável PATH_TO_GUIDE")

        try:
            variablestochangeleaf1["KICKSTART_SO_LF"] = get_variable("kickstart_so_lf")
            variablestochangeleaf1["IMAGE_SO_LF"] = get_variable("image_so_lf")
        except ObjectDoesNotExist:
            raise var_exceptions.VariableDoesNotExistException(
                "Erro buscando a variável KICKSTART_SO_LF ou IMAGE_SO_LF.")

        equips_sorted = sorted(equips, key=operator.itemgetter('sw'))

        dcroom = model_to_dict(rack.dcroom)
        log.debug("type: %s" % str(type(dcroom.get("config"))))
        fabricconfig = dcroom.get("config")

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

        envconfig = fabricconfig
        BASE_RACK = dcroom.get("racks")
        BGP = envconfig.get("BGP")
        BASE_AS_SPN = int(BGP.get("spines"))
        BASE_AS_LFS = int(BGP.get("leafs"))

        # get fathers environments
        dc_name = ["BE", "FE", "BO", "BOCACHOS-A", "BOCACHOS-B"]
        vlan_name = list()
        for env in dc_name:
            for spn in range(1, 5):
                name = "VLAN_" + env + "_SPINE0" + str(spn) + "LEAF_" + self.rack.nome
                vlan_name.append(name)

        spn_vlan = models_vlan.Vlan.objects.filter(nome__in=vlan_name).order_by("nome")

        log.debug("spn_vlan %s" % spn_vlan)

        prod_envs = models_env.Ambiente.objects.filter(grupo_l3__nome=str(self.rack.nome),
                                                       ambiente_logico__nome="PRODUCAO",
                                                       divisao_dc__nome__in=["BE", "FE", "BO_DSR",
                                                                             "BOCACHOS-A", "BOCACHOS-B"])
        log.debug("prod_envs %s" % prod_envs)

        lf_env = models_env.Ambiente.objects.filter(grupo_l3__nome=str(self.rack.nome),
                                                    divisao_dc__nome="BE",
                                                    ambiente_logico__nome="LEAF-LEAF").uniqueResult()
        log.debug("lf_env %s" % lf_env)

        vlanBE = list()
        vlanFE = list()
        vlanBO = list()
        vlanBOCA = list()
        vlanBOCAB = list()

        for vlan in spn_vlan:
            if "_BE_" in vlan.nome:
                vlanBE.append(vlan.num_vlan)
                CIDRBEipv4.append(IPNetwork(vlan.networks_ipv4[0].networkv4))
                CIDRBEipv6.append(IPNetwork(vlan.networks_ipv6[0].networkv6))
            elif "_FE_" in vlan.nome:
                vlanFE.append(vlan.num_vlan)
            elif "_BO_" in vlan.nome:
                vlanBO.append(vlan.num_vlan)
            elif "_BOCACHOS-A_" in vlan.nome:
                vlanBOCA.append(vlan.num_vlan)
            elif "_BOCACHOS-B_" in vlan.nome:
                vlanBOCAB.append(vlan.num_vlan)

        for prod in prod_envs:
            if prod.divisao_dc.nome[:2] == "BE":
                for net in prod.configs:
                    if net.ip_version == "v4":
                        CIDRBEipv4interno = str(net.network)
                    else:
                        CIDRBEipv6interno = str(net.network)
            elif prod.divisao_dc.nome[:2] == "FE":
                for net in prod.configs:
                    if net.ip_version == "v4":
                        CIDRFEipv4interno = str(net.network)
                    else:
                        CIDRFEipv6interno = str(net.network)

            elif prod.divisao_dc.nome == "BO_DSR":
                for net in prod.configs:
                    if net.ip_version == "v4":
                        CIDRBO_DSRipv4interno = str(net.network)
                    else:
                        CIDRBO_DSRipv6interno = str(net.network)

            elif prod.divisao_dc.nome == "BOCACHOS-A":
                for net in prod.configs:
                    if net.ip_version == "v4":
                        CIDRBOCAAipv4interno = str(net.network)
                    else:
                        CIDRBOCAAipv6interno = str(net.network)
            elif prod.divisao_dc.nome == "BOCACHOS-B":
                for net in prod.configs:
                    if net.ip_version == "v4":
                        CIDRBOCABipv4interno = str(net.network)
                    else:
                        CIDRBOCABipv6interno = str(net.network)

        for netlf in lf_env.configs:
            if netlf.ip_version == "v4":
                IBGPToRLxLipv4 = IPNetwork(str(netlf.network))
            elif netlf.ip_version == "v6":
                IBGPToRLxLipv6 = IPNetwork(str(netlf.network))

        id_vlt = [envconfig.get("VLT").get("id_vlt_lf1"), envconfig.get("VLT").get("id_vlt_lf2")]
        priority_vlt = [envconfig.get("VLT").get("priority_vlt_lf1"), envconfig.get("VLT").get("priority_vlt_lf2")]

        for i in range(len(CIDRBEipv4)):
            IPSPINEipv4[numero_rack].append(CIDRBEipv4[i][0])
            IPLEAFipv4[numero_rack].append(CIDRBEipv4[i][1])

            IPSPINEipv6[numero_rack].append(CIDRBEipv6[i][0])
            IPLEAFipv6[numero_rack].append(CIDRBEipv6[i][1])

        #
        IPSIBGPipv4[numero_rack].append(IBGPToRLxLipv4[0])
        IPSIBGPipv4[numero_rack].append(IBGPToRLxLipv4[1])
        #
        #
        IPSIBGPipv6[numero_rack].append(IBGPToRLxLipv6[0])
        IPSIBGPipv6[numero_rack].append(IBGPToRLxLipv6[1])
        #
        log.debug("vlan subnet")
        log.debug(vlanBE)
        log.debug(BASE_RACK)
        log.debug(numero_rack)
        log.debug(vlanFE)
        log.debug(vlanBO)
        log.debug(vlanBOCA)
        log.debug(vlanBOCAB)
        log.debug(CIDRBEipv4)
        log.debug(CIDRBEipv6)

        log.debug("as")
        log.debug(BASE_AS_LFS)
        log.debug(numero_rack)
        log.debug(numero_rack)
        log.debug("zip equips_sorted")
        log.debug(zip(equips_sorted[:2], [0, 2], [0, 1]))

        ASLEAF[numero_rack].append(BASE_AS_LFS + numero_rack)

        for equip, spn, j in zip(equips_sorted[:2], [0, 2], [0, 1]):
            variablestochangeleaf1["IPLEAFSP1IPV4"] = str(IPLEAFipv4[numero_rack][spn])
            variablestochangeleaf1["IPLEAFSP2IPV4"] = str(IPLEAFipv4[numero_rack][spn + 1])
            variablestochangeleaf1["IPIBGPIPV4"] = str(IPSIBGPipv4[numero_rack][j])
            variablestochangeleaf1["IPLEAFSP1IPV6"] = str(IPLEAFipv6[numero_rack][spn])
            variablestochangeleaf1["IPLEAFSP2IPV6"] = str(IPLEAFipv6[numero_rack][spn + 1])
            variablestochangeleaf1["IPIBGPIPV6"] = str(IPSIBGPipv6[numero_rack][j])
            log.debug("1")
            variablestochangeleaf1["VLANBELEAFSP1"] = str(vlanBE[spn])
            variablestochangeleaf1["VLANBELEAFSP2"] = str(vlanBE[spn + 1])
            variablestochangeleaf1["VLANFELEAFSP1"] = str(vlanFE[spn])
            variablestochangeleaf1["VLANFELEAFSP2"] = str(vlanFE[spn + 1])
            variablestochangeleaf1["VLANBORDALEAFSP1"] = str(vlanBO[spn])
            variablestochangeleaf1["VLANBORDALEAFSP2"] = str(vlanBO[spn + 1])
            variablestochangeleaf1["VLANBORDACACHOSLEAFSP1"] = str(vlanBOCA[spn])
            variablestochangeleaf1["VLANBORDACACHOSLEAFSP2"] = str(vlanBOCA[spn + 1])
            variablestochangeleaf1["VLANBORDACACHOSBLEAFSP1"] = str(vlanBOCAB[spn])
            variablestochangeleaf1["VLANBORDACACHOSBLEAFSP2"] = str(vlanBOCAB[spn + 1])

            ### To pop Berrini
            variablestochangeleaf1["VLANBERBELEAFSP1"] = str(vlanBE[0])
            variablestochangeleaf1["VLANBERBELEAFSP2"] = str(vlanBE[1])
            variablestochangeleaf1["VLANBERFELEAFSP1"] = str(vlanFE[0])
            variablestochangeleaf1["VLANBERFELEAFSP2"] = str(vlanFE[1])
            variablestochangeleaf1["VLANBERBORDALEAFSP1"] = str(vlanBO[0])
            variablestochangeleaf1["VLANBERBORDALEAFSP2"] = str(vlanBO[1])
            variablestochangeleaf1["VLANBERBORDACACHOSLEAFSP1"] = str(vlanBOCA[0])
            variablestochangeleaf1["VLANBERBORDACACHOSLEAFSP2"] = str(vlanBOCA[1])
            variablestochangeleaf1["VLANBERBORDACACHOSBLEAFSP1"] = str(vlanBOCAB[0])
            variablestochangeleaf1["VLANBERBORDACACHOSBLEAFSP2"] = str(vlanBOCAB[1])

            log.debug("2")
            variablestochangeleaf1["ASLEAF"] = str(ASLEAF[numero_rack][0])

            variablestochangeleaf1["IPNEIGHSPINE1IPV4"] = str(IPSPINEipv4[numero_rack][spn])
            variablestochangeleaf1["IPNEIGHSPINE2IPV4"] = str(IPSPINEipv4[numero_rack][spn + 1])
            variablestochangeleaf1["IPNEIGHSPINE1IPV6"] = str(IPSPINEipv6[numero_rack][spn])
            variablestochangeleaf1["IPNEIGHSPINE2IPV6"] = str(IPSPINEipv6[numero_rack][spn + 1])

            if equip.get("nome")[-1] == "1":
                log.debug("lf-name: %s. Ip: %s" % (equip.get("nome"), IPSIBGPipv4[numero_rack][1]))
                variablestochangeleaf1["IPNEIGHIBGPIPV4"] = str(IPSIBGPipv4[numero_rack][1])
                variablestochangeleaf1["IPNEIGHIBGPIPV6"] = str(IPSIBGPipv6[numero_rack][1])
            else:
                log.debug("lf-name: %s. Ip: %s" % (equip.get("nome"), IPSIBGPipv4[numero_rack][0]))
                variablestochangeleaf1["IPNEIGHIBGPIPV4"] = str(IPSIBGPipv4[numero_rack][0])
                variablestochangeleaf1["IPNEIGHIBGPIPV6"] = str(IPSIBGPipv6[numero_rack][0])

            try:
                variablestochangeleaf1["NET_HOST_BE_IPV4"] = CIDRBEipv4interno
                variablestochangeleaf1["NET_HOST_FE_IPV4"] = CIDRFEipv4interno
            except Exception as e:
                raise Exception("Error while getting IPv4 CIDR from BE or FE production environment. E: %s" % e)

            if CIDRBO_DSRipv4interno:
                variablestochangeleaf1["NET_HOST_BO_DSR_IPV4"] = CIDRBO_DSRipv4interno
            if CIDRBOCAAipv4interno:
                variablestochangeleaf1["NET_HOST_BOCAA_IPV4"] = CIDRBOCAAipv4interno
            if CIDRBOCABipv4interno:
                variablestochangeleaf1["NET_HOST_BOCAB_IPV4"] = CIDRBOCABipv4interno
            log.debug("3")
            variablestochangeleaf1["NET_SPINE1_LF_IPV4"] = str(CIDRBEipv4[0])
            variablestochangeleaf1["NET_SPINE2_LF_IPV4"] = str(CIDRBEipv4[1])
            variablestochangeleaf1["NET_LF_LF_IPV4"] = str(IBGPToRLxLipv4)

            try:
                variablestochangeleaf1["NET_HOST_BE_IPV6"] = CIDRBEipv6interno
                variablestochangeleaf1["NET_HOST_FE_IPV6"] = CIDRFEipv6interno
            except Exception as e:
                raise Exception("Error while getting IPv6 CIDR from BE or FE production environment. E: %s" % e)

            if CIDRBO_DSRipv6interno:
                variablestochangeleaf1["NET_HOST_BO_DSR_IPV6"] = CIDRBO_DSRipv6interno
            if CIDRBOCAAipv6interno:
                variablestochangeleaf1["NET_HOST_BOCAA_IPV6"] = CIDRBOCAAipv6interno
            if CIDRBOCABipv6interno:
                variablestochangeleaf1["NET_HOST_BOCAB_IPV6"] = CIDRBOCABipv6interno
            log.debug("4")
            variablestochangeleaf1["NET_SPINE1_LF_IPV6"] = str(CIDRBEipv6[0])
            variablestochangeleaf1["NET_SPINE2_LF_IPV6"] = str(CIDRBEipv6[1])
            variablestochangeleaf1["NET_LF_LF_IPV6"] = str(IBGPToRLxLipv6)

            variablestochangeleaf1["ID_LEAF"] = str(equip.get("sw"))  # lf1 ou lf2
            variablestochangeleaf1["OWN_IP_MGMT"] = equip.get("ip_mngt")
            variablestochangeleaf1["LF_HOSTNAME"] = equip.get("nome")
            log.debug("5")
            for i in equip.get("interfaces"):
                if i.get("nome")[:3] == self.leaf_prefix:
                    variablestochangeleaf1["LFNEIGH_HOSTNAME"] = i.get("nome")
                    variablestochangeleaf1["LFNEIGH_IP_MGMT"] = i.get("ip_mngt")
                elif i.get("nome")[:3] == self.spine_prefix:
                    spine_num = int(i.get("nome")[-1])
                    log.debug(spn)
                    log.debug(spine_num)
                    variablestochangespine1["ASSPINE"] = str(BASE_AS_SPN + spine_num - 1)
                    variablestochangespine1["INTERFACE"] = i.get("interface")
                    variablestochangespine1["LEAFNAME"] = equip.get("nome")
                    variablestochangespine1["INT_LF_UPLINK"] = i.get("eq_interface")
                    log.debug("ok if spn")
                    variablestochangespine1["IPSPINEIPV4"] = str(IPSPINEipv4[numero_rack][spine_num - 1])
                    variablestochangespine1["IPSPINEIPV6"] = str(IPSPINEipv6[numero_rack][spine_num - 1])
                    variablestochangespine1["VLANBELEAF"] = str(vlanBE[spine_num - 1])
                    variablestochangespine1["VLANFELEAF"] = str(vlanFE[spine_num - 1])
                    variablestochangespine1["VLANBORDALEAF"] = str(vlanBO[spine_num - 1])
                    variablestochangespine1["VLANBORDACACHOSLEAF"] = str(vlanBOCA[spine_num - 1])
                    variablestochangespine1["VLANBORDACACHOSB"] = str(vlanBOCAB[spine_num - 1])
                    variablestochangespine1["ASLEAF"] = str(ASLEAF[numero_rack][0])

                    ### TO BERRINI
                    if spine_num == 1:
                        variablestochangespine1["DESCRIPTION1CONNECT"] = equips_sorted[0].get("nome")
                        variablestochangespine1["DESCRIPTION2CONNECT"] = equips_sorted[1].get("nome")
                        variablestochangespine1["VLANBORDA2LEAF"] = str(vlanBO[spine_num])
                        variablestochangespine1["VLANBORDA2CACHOSLEAF"] = str(vlanBOCA[spine_num])
                        variablestochangespine1["VLANBORDA2CACHOSB"] = str(vlanBOCAB[spine_num])
                        variablestochangespine1["VLANFE2LEAF"] = str(vlanFE[spine_num])

                        counter = 1
                        for ipv6 in IPSPINEipv6[numero_rack]:
                            variablestochangespine1["IPSPINE{}IPV6".format(counter)] = str(ipv6)
                            variablestochangespine1["IPNEIGHLEAF{}IPV6".format(counter)] = str(IPLEAFipv6[numero_rack][counter -1])

                            counter += 1

                        counter = 1
                        for ipv4 in IPSPINEipv4[numero_rack]:
                            variablestochangespine1["IPSPINE{}IPV4".format(counter)] = str(ipv4)
                            variablestochangespine1["IPNEIGHLEAF{}IPV4".format(counter)] = str(IPLEAFipv4[numero_rack][counter -1])

                            counter += 1

                        # variablestochangespine1["IPSPI2NEIPV6"] = str(IPSPINEipv6[numero_rack][spine_num])
                        # variablestochangespine1["IPSPI2NEIPV4"] = str(IPSPINEipv4[numero_rack][spine_num])
                        variablestochangespine1["VLANBE2LEAF"] = str(vlanBE[spine_num])
                        # variablestochangespine1["IPNEIGHLEAF2IPV4"] = str(IPLEAFipv4[numero_rack][spine_num])
                        # variablestochangespine1["IPNEIGHLEAF2IPV6"] = str(IPLEAFipv6[numero_rack][spine_num])
                    elif spine_num == 2:
                        variablestochangespine1["DESCRIPTION1CONNECT"] = equips_sorted[1].get("nome")
                        variablestochangespine1["DESCRIPTION2CONNECT"] = equips_sorted[0].get("nome")
                        variablestochangespine1["VLANBORDA2LEAF"] = str(vlanBO[spine_num - 2])
                        variablestochangespine1["VLANBORDA2CACHOSLEAF"] = str(vlanBOCA[spine_num - 2])
                        variablestochangespine1["VLANBORDA2CACHOSB"] = str(vlanBOCAB[spine_num - 2])
                        variablestochangespine1["VLANFE2LEAF"] = str(vlanFE[spine_num - 2])
                        counter = 0
                        log.debug(IPSPINEipv6[numero_rack])
                        for ipv6 in IPSPINEipv6[numero_rack]:
                            if spine_num + counter < len(IPLEAFipv6[numero_rack]):
                                variablestochangespine1["IPSPINE{}IPV6".format(counter + 1)] = str(IPSPINEipv6[numero_rack][counter + spine_num])
                                variablestochangespine1["IPNEIGHLEAF{}IPV6".format(counter + 1)] = str(IPLEAFipv6[numero_rack][counter + spine_num])
                            counter += 1

                        counter = 0
                        for ipv4 in IPSPINEipv4[numero_rack]:
                            if spine_num + counter < len(IPLEAFipv4[numero_rack]):
                                variablestochangespine1["IPSPINE{}IPV4".format(counter + 1)] = str(IPSPINEipv4[numero_rack][counter + spine_num])
                                variablestochangespine1["IPNEIGHLEAF{}IPV4".format(counter + 1)] = str(IPLEAFipv4[numero_rack][counter + spine_num])


                            counter += 1
                        # variablestochangespine1["IPSPI2NEIPV6"] = str(IPSPINEipv6[numero_rack][spine_num - 2])
                        # variablestochangespine1["IPSPI2NEIPV4"] = str(IPSPINEipv4[numero_rack][spine_num - 2])
                        variablestochangespine1["VLANBE2LEAF"] = str(vlanBE[spine_num - 2])
                        # variablestochangespine1["IPNEIGHLEAF2IPV4"] = str(IPLEAFipv4[numero_rack][spine_num - 2])
                        # variablestochangespine1["IPNEIGHLEAF2IPV6"] = str(IPLEAFipv6[numero_rack][spine_num - 2])

                        # e_counter = 1
                        # for e in equips_sorted[:2]:
                        #     # "DESCRIPTION{}CONNECT"

                            # e_counter += 1
                    #### END to Berrini Block #####

                    variablestochangespine1["IPNEIGHLEAFIPV4"] = str(IPLEAFipv4[numero_rack][spine_num - 1])
                    variablestochangespine1["IPNEIGHLEAFIPV6"] = str(IPLEAFipv6[numero_rack][spine_num - 1])

                    if spine_num in [1, 3]:
                        variablestochangeleaf1["SP1_HOSTNAME"] = i.get("nome")
                        variablestochangeleaf1["INTERFACE_SP1"] = i.get("interface")
                        variablestochangeleaf1["ASSPINE1"] = str(BASE_AS_SPN + spine_num - 1)
                    else:
                        variablestochangeleaf1["SP2_HOSTNAME"] = i.get("nome")
                        variablestochangeleaf1["INTERFACE_SP2"] = i.get("interface")
                        variablestochangeleaf1["ASSPINE2"] = str(BASE_AS_SPN + spine_num - 1)

                    fileinspine1 = path_to_guide + i.get("roteiro")
                    fileoutspine1 = path_to_add_config + i.get("nome") + "-ADD-" + rack.nome + ".cfg"
                    self.replace_file(fileinspine1, fileoutspine1, variablestochangespine1)
                    variablestochangespine1 = dict()

                elif i.get("nome")[:3] == self.oob_prefix:
                    variablestochangeleaf1["HOSTNAME_OOB"] = i.get("nome")
                    variablestochangeleaf1["INTERFACE_OOB"] = i.get("interface")

            variablestochangeleaf1["ID_VLT"] = str(id_vlt[j])
            variablestochangeleaf1["PRIORITY_VLT"] = str(priority_vlt[j])

            fileinleaf1 = path_to_guide + equip.get("roteiro")
            fileoutleaf1 = path_to_config + equip.get("nome") + ".cfg"

            self.replace_file(fileinleaf1, fileoutleaf1, variablestochangeleaf1)
            log.debug(fileoutleaf1)
            variablestochangeleaf1 = dict()

        return True

    def oob_provision(self, equips):
        log.info("AutoprovisionOOB")

        variablestochangecore1 = dict()
        variablestochangecore2 = dict()
        variablestochangeoob = dict()

        fileincore1 = None
        fileoutcore1 = None
        fileincore2 = None
        fileoutcore2 = None

        dcroom = model_to_dict(self.rack.dcroom)
        log.debug("type: %s" % str(type(dcroom.get("config"))))
        fabricconfig = dcroom.get("config")

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

        envconfig = fabricconfig
        BASE_CHANNEL = int(envconfig.get("Channel").get("channel")) if envconfig.get("Channel") else 10

        try:
            path_to_guide = get_variable("path_to_guide")
            path_to_add_config = get_variable("path_to_add_config")
            path_to_config = get_variable("path_to_config")
        except ObjectDoesNotExist:
            raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável PATH_TO_GUIDE")

        try:
            vlan_name = "VLAN_GERENCIA_" + self.rack.nome
            vlan = models_vlan.Vlan.objects.filter(nome=vlan_name).uniqueResult()
        except Exception as e:
            log.debug("Error while getting %s. Error: %s" % (vlan_name, e))
            vlan = False

        if not vlan:
            try:
                vlan_name = "OOB_SO_" + self.rack.nome
                vlan = models_vlan.Vlan.objects.filter(nome=vlan_name).uniqueResult()
            except Exception as e:
                raise Exception("O rack não tem vlan de gerencia. Error: %s" % e)

        log.debug("Vlan OOB: %s" % vlan.nome)
        log.debug("Rede OOB: %s" % IPNetwork(vlan.networks_ipv4[0].networkv4))
        log.debug("equips: %s" % str(equips))

        if not vlan.networks_ipv4:
            raise Exception("Vlan de OOB do rack não possui rede associada.")

        variablestochangeoob["VLAN_SO"] = str(vlan.num_vlan)

        equips_sorted = sorted(equips, key=operator.itemgetter('sw'))
        oob = equips_sorted[-1]

        variablestochangeoob["OWN_IP_MGMT"] = oob.get("ip_mngt")
        variablestochangeoob["HOSTNAME_OOB"] = oob.get("nome")
        variablestochangeoob["HOSTNAME_RACK"] = self.rack.nome

        fileinoob = path_to_guide + oob.get("roteiro")
        fileoutoob = path_to_config + oob.get("nome") + ".cfg"

        for equip in oob.get("interfaces"):
            nome = equip.get("nome")
            log.debug(str(nome))
            roteiro = equip.get("roteiro")
            if nome[:3] == self.leaf_prefix:
                if nome[-1] == "1":
                    variablestochangeoob["HOSTNAME_LF1"] = nome
                else:
                    variablestochangeoob["HOSTNAME_LF2"] = nome
            elif nome[:3] == self.oob_prefix:
                intoob = equip.get("eq_interface")
                intcore = equip.get("interface")
                if nome[-1] == "1":
                    log.info(str(nome))
                    variablestochangeoob["INT_OOBC1_UPLINK"] = intoob
                    variablestochangeoob["INTERFACE_CORE1"] = intcore
                    variablestochangeoob["HOSTNAME_CORE1"] = nome
                    variablestochangecore1["INT_OOB_UPLINK"] = intoob
                    variablestochangecore1["INTERFACE_CORE"] = intcore
                    variablestochangecore1["HOSTNAME_RACK"] = self.rack.nome
                    variablestochangecore1["SO_HOSTNAME_OOB"] = "SO_" + str(self.rack.nome)
                    variablestochangecore1["VLAN_SO"] = str(vlan.num_vlan)
                    variablestochangecore1['IPCORE'] = str(IPNetwork(vlan.networks_ipv4[0].networkv4).broadcast-2)
                    variablestochangecore1['IPHSRP'] = str(IPNetwork(vlan.networks_ipv4[0].networkv4).ip+1)
                    variablestochangecore1['NUM_CHANNEL'] = str(BASE_CHANNEL + int(self.rack.numero))
                    if (1 + int(self.rack.numero)) % 2 == 0:
                        variablestochangecore1["HSRP_PRIORITY"] = "100"
                    else:
                        variablestochangecore1["HSRP_PRIORITY"] = "101"
                    fileincore1 = path_to_guide + roteiro
                    fileoutcore1 = path_to_add_config + nome + "-ADD-" + str(self.rack.nome) + ".cfg"
                elif nome[-1] == "2":
                    log.info(str(nome))
                    variablestochangeoob["INT_OOBC2_UPLINK"] = intoob
                    variablestochangeoob["INTERFACE_CORE2"] = intcore
                    variablestochangeoob["HOSTNAME_CORE2"] = nome
                    variablestochangecore2["INT_OOB_UPLINK"] = intoob
                    variablestochangecore2["INTERFACE_CORE"] = intcore
                    variablestochangecore2["HOSTNAME_RACK"] = self.rack.nome
                    variablestochangecore2["SO_HOSTNAME_OOB"] = "SO_" + str(self.rack.nome)
                    variablestochangecore2["VLAN_SO"] = str(vlan.num_vlan)
                    variablestochangecore2['IPCORE'] = str(IPNetwork(vlan.networks_ipv4[0].networkv4).broadcast-1)
                    variablestochangecore2['IPHSRP'] = str(IPNetwork(vlan.networks_ipv4[0].networkv4).ip+1)
                    variablestochangecore2['NUM_CHANNEL'] = str(BASE_CHANNEL + int(self.rack.numero))
                    if (2 + int(self.rack.numero)) % 2 == 0:
                        variablestochangecore2["HSRP_PRIORITY"] = "100"
                    else:
                        variablestochangecore2["HSRP_PRIORITY"] = "101"
                    fileincore2 = path_to_guide + roteiro
                    fileoutcore2 = path_to_add_config + nome + "-ADD-" + str(self.rack.nome) + ".cfg"

        self.replace_file(fileincore1, fileoutcore1, variablestochangecore1)
        self.replace_file(fileincore2, fileoutcore2, variablestochangecore2)
        self.replace_file(fileinoob, fileoutoob, variablestochangeoob)

        return True
