# -*- coding: utf-8 -*-

import ast
import logging
import operator
import re
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from netaddr import IPNetwork
from networkapi.rack.models import RackConfigError
from networkapi.system.facade import get_value as get_variable
from networkapi.system import exceptions as var_exceptions

log = logging.getLogger(__name__)


def replace(filein, fileout, dicionario):
    try:
        # Read contents from file as a single string
        file_handle = open(filein, 'r')
        file_string = file_handle.read()
        file_handle.close()
    except:
        raise RackConfigError(None, None, "Erro abrindo roteiro: %s." % filein)

    try:
        for key in dicionario:
            # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
            log.info("variavel: %s, valor: %s" % (str(key), str(dicionario[key])))
            file_string = (re.sub(key, dicionario[key], file_string))
    except:
        raise RackConfigError(None, None, "Erro atualizando as variáveis no roteiro: %s." % filein)

    try:
        # Write contents to file.
        # Using mode 'w' truncates the file.
        file_handle = open(fileout, 'w')
        file_handle.write(file_string)
        file_handle.close()
    except:
        raise RackConfigError(None, None, "Erro salvando arquivo de configuração: %s." % fileout)


def splitnetworkbyrack(net, bloco, posicao):
    subnets = list(net.subnet(bloco))
    return subnets[posicao]


def autoprovision_splf(rack, equips):

    log.info("AutoprovisionSPN-LF")

    numero_rack = rack.numero
    prefixspn = "SPN"
    prefixlf = "LF-"
    prefixoob = "OOB"
    # STRUCTURE: IPSPINE[rack][spine]: ip a configurar no spine 'spine' relativo à leaf do rack 'rack'
    # STRUCTURE: IPLEAF[rack][spine]: ip a configurar no leaf do rack 'rack' relativo ao spine 'spine'
    CIDREBGP = dict()
    IPSPINEipv4 = dict()
    IPSPINEipv6 = dict()
    IPLEAFipv4 = dict()
    IPLEAFipv6 = dict()
    IPSIBGPipv4 = dict()
    IPSIBGPipv6 = dict()
    ASLEAF = dict()
    #
    VLANBELEAF = dict()
    VLANFELEAF = dict()
    VLANBORDALEAF = dict()
    VLANBORDACACHOSLEAF = dict()
    #
    PODSBEipv4 = dict()
    redesPODSBEipv4 = dict()
    #
    subnetsRackBEipv4 = dict()
    #
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
    subnetsRackBEipv6 = dict()
    subnetsRackFEipv4 = dict()
    redesPODSFEipv4 = dict()
    subnetsRackFEipv6 = dict()
    redesPODSFEipv6 = dict()
    #
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
    ASLEAF[numero_rack] = list()
    #
    PODSBEipv4[numero_rack] = list()
    redesPODSBEipv4[numero_rack] = list()
    #
    subnetsRackBEipv4[numero_rack] = list()
    #
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
    subnetsRackBEipv6[numero_rack] = list()
    subnetsRackFEipv4[numero_rack] = list()
    redesPODSFEipv4[numero_rack] = list()
    subnetsRackFEipv6[numero_rack] = list()
    redesPODSFEipv6[numero_rack] = list()

    CIDRFEipv4 = dict()
    CIDRFEipv6 = dict()

    variablestochangespine1 = dict()
    variablestochangeleaf1 = dict()

    VLANBE = None
    VLANFE = None
    VLANBORDA = None
    VLANBORDACACHOS = None
    CIDRBEipv4 = None
    CIDRBEipv6 = None

    try:
        path_to_guide = get_variable("path_to_guide")
        path_to_add_config = get_variable("path_to_add_config")
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável PATH_TO_GUIDE")

    try:
        variablestochangeleaf1["KICKSTART_SO_LF"] = get_variable("kickstart_so_lf")
        variablestochangeleaf1["IMAGE_SO_LF"] = get_variable("image_so_lf")
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável KICKSTART_SO_LF ou IMAGE_SO_LF.")

    equips_sorted = sorted(equips, key=operator.itemgetter('sw'))

    dcroom = model_to_dict(rack.dcroom)
    envconfig = ast.literal_eval(dcroom.get("config"))
    BASE_RACK = dcroom.get("racks")
    BGP = envconfig.get("BGP")
    BASE_AS_SPN = int(BGP.get("ASNspn"))
    CIDREBGP[0] = IPNetwork(BGP.get("cidr"))
    IBGPToRLxLipv4 = IPNetwork(BGP.get("ibgp_v4"))
    IBGPToRLxLipv6 = IPNetwork(BGP.get("ibgp_v6"))

    for ambiente in envconfig.get("Ambiente"):
        nome = ambiente.get("nome")
        vlan_range = ambiente.get("vlans").get("range")[0]
        vlan_base = int(vlan_range.split("-")[0])
        net_v4 = ambiente.get("redes").get("cidr_v4")
        net_v6 = ambiente.get("redes").get("cidr_v6")
        if nome == "BE":
            VLANBE = vlan_base
            CIDRBEipv4 = IPNetwork(net_v4)
            CIDRBEipv6 = IPNetwork(net_v6)
        elif nome == "FE":
            VLANFE = vlan_base
            CIDRFEipv4[0] = IPNetwork(net_v4)
            CIDRFEipv6[0] = IPNetwork(net_v6)
        elif nome == "BO":
            VLANBORDA = vlan_base
        elif nome == "BOCA":
            VLANBORDACACHOS = vlan_base

    netv4_spn = IPNetwork(envconfig.get("sala").get("spines_v4"))

    SPINE1ipv4 = splitnetworkbyrack(netv4_spn, 24, 0)
    SPINE2ipv4 = splitnetworkbyrack(netv4_spn, 24, 1)
    SPINE3ipv4 = splitnetworkbyrack(netv4_spn, 24, 2)
    SPINE4ipv4 = splitnetworkbyrack(netv4_spn, 24, 3)
    SPINE1ipv6 = IPNetwork(envconfig.get("sala").get("spn1_v6"))
    SPINE2ipv6 = IPNetwork(envconfig.get("sala").get("spn2_v6"))
    SPINE3ipv6 = IPNetwork(envconfig.get("sala").get("spn3_v6"))
    SPINE4ipv6 = IPNetwork(envconfig.get("sala").get("spn4_v6"))

    id_vlt = [envconfig.get("VLT").get("id_vlt_lf1"), envconfig.get("VLT").get("id_vlt_lf2")]
    priority_vlt = [envconfig.get("VLT").get("priority_vlt_lf1"), envconfig.get("VLT").get("priority_vlt_lf2")]

    subSPINE1ipv4 = list(SPINE1ipv4.subnet(31))
    subSPINE2ipv4 = list(SPINE2ipv4.subnet(31))
    subSPINE3ipv4 = list(SPINE3ipv4.subnet(31))
    subSPINE4ipv4 = list(SPINE4ipv4.subnet(31))
    subSPINE1ipv6 = list(SPINE1ipv6.subnet(127))
    subSPINE2ipv6 = list(SPINE2ipv6.subnet(127))
    subSPINE3ipv6 = list(SPINE3ipv6.subnet(127))
    subSPINE4ipv6 = list(SPINE4ipv6.subnet(127))

    subIBGPToRLxLipv4 = list(IBGPToRLxLipv4.subnet(31))
    subIBGPToRLxLipv6 = list(IBGPToRLxLipv6.subnet(127))

    IPSPINEipv4[numero_rack].append(subSPINE1ipv4[numero_rack][0])
    IPSPINEipv4[numero_rack].append(subSPINE2ipv4[numero_rack][0])
    IPSPINEipv4[numero_rack].append(subSPINE3ipv4[numero_rack][0])
    IPSPINEipv4[numero_rack].append(subSPINE4ipv4[numero_rack][0])
    #
    IPLEAFipv4[numero_rack].append(subSPINE1ipv4[numero_rack][1])
    IPLEAFipv4[numero_rack].append(subSPINE2ipv4[numero_rack][1])
    IPLEAFipv4[numero_rack].append(subSPINE3ipv4[numero_rack][1])
    IPLEAFipv4[numero_rack].append(subSPINE4ipv4[numero_rack][1])
    #
    IPSIBGPipv4[numero_rack].append(subIBGPToRLxLipv4[numero_rack][0])
    IPSIBGPipv4[numero_rack].append(subIBGPToRLxLipv4[numero_rack][1])
    #
    IPSPINEipv6[numero_rack].append(subSPINE1ipv6[numero_rack][0])
    IPSPINEipv6[numero_rack].append(subSPINE2ipv6[numero_rack][0])
    IPSPINEipv6[numero_rack].append(subSPINE3ipv6[numero_rack][0])
    IPSPINEipv6[numero_rack].append(subSPINE4ipv6[numero_rack][0])
    #
    IPLEAFipv6[numero_rack].append(subSPINE1ipv6[numero_rack][1])
    IPLEAFipv6[numero_rack].append(subSPINE2ipv6[numero_rack][1])
    IPLEAFipv6[numero_rack].append(subSPINE3ipv6[numero_rack][1])
    IPLEAFipv6[numero_rack].append(subSPINE4ipv6[numero_rack][1])
    #
    IPSIBGPipv6[numero_rack].append(subIBGPToRLxLipv6[numero_rack][0])
    IPSIBGPipv6[numero_rack].append(subIBGPToRLxLipv6[numero_rack][1])
    #
    VLANBELEAF[numero_rack].append(VLANBE+numero_rack)
    VLANBELEAF[numero_rack].append(VLANBE+numero_rack+BASE_RACK)
    VLANBELEAF[numero_rack].append(VLANBE+numero_rack+2*BASE_RACK)
    VLANBELEAF[numero_rack].append(VLANBE+numero_rack+3*BASE_RACK)
    #
    VLANFELEAF[numero_rack].append(VLANFE+numero_rack)
    VLANFELEAF[numero_rack].append(VLANFE+numero_rack+BASE_RACK)
    VLANFELEAF[numero_rack].append(VLANFE+numero_rack+2*BASE_RACK)
    VLANFELEAF[numero_rack].append(VLANFE+numero_rack+3*BASE_RACK)
    #
    VLANBORDALEAF[numero_rack].append(VLANBORDA+numero_rack)
    VLANBORDALEAF[numero_rack].append(VLANBORDA+numero_rack+BASE_RACK)
    VLANBORDALEAF[numero_rack].append(VLANBORDA+numero_rack+2*BASE_RACK)
    VLANBORDALEAF[numero_rack].append(VLANBORDA+numero_rack+3*BASE_RACK)
    #
    VLANBORDACACHOSLEAF[numero_rack].append(VLANBORDACACHOS+numero_rack)
    VLANBORDACACHOSLEAF[numero_rack].append(VLANBORDACACHOS+numero_rack+BASE_RACK)
    VLANBORDACACHOSLEAF[numero_rack].append(VLANBORDACACHOS+numero_rack+2*BASE_RACK)
    VLANBORDACACHOSLEAF[numero_rack].append(VLANBORDACACHOS+numero_rack+3*BASE_RACK)
    #
    ASLEAF[numero_rack].append(BASE_AS_SPN+numero_rack)
    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::
    # Redes p/ rack => 10.128.0.0/19, 10.128.32.0/19 , ... ,10.143.224.0/19
    subnetsRackBEipv4[numero_rack] = splitnetworkbyrack(CIDRBEipv4, 19, numero_rack)
    subnetsRackBEipv6[numero_rack] = splitnetworkbyrack(CIDRBEipv6, 55, numero_rack)
    # PODS BE => /20
    #    ::::::::::::::::::::::::::::::::::: FRONTEND
    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::
    # Sumário do rack => 172.20.0.0/21
    subnetsRackFEipv4[numero_rack] = splitnetworkbyrack(CIDRFEipv4[0], 21, numero_rack)
    subnetsRackFEipv6[numero_rack] = splitnetworkbyrack(CIDRFEipv6[0], 57, numero_rack)
    #          ::::::: SUBNETING EACH RACK NETWORK:::::::
    # PODS FE => 128 redes /28 ; 128 redes /64
    redesPODSBEipv4[numero_rack] = list(subnetsRackFEipv4[numero_rack].subnet(28))
    redesPODSBEipv6[numero_rack] = list(subnetsRackFEipv6[numero_rack].subnet(64))

    for equip, spn, j in zip(equips_sorted[:2], [0, 2], [0, 1]):
        # lf 1/2
        log.info("for equip spn j")
        variablestochangeleaf1["IPLEAFSP1IPV4"] = str(IPLEAFipv4[numero_rack][spn])
        variablestochangeleaf1["IPLEAFSP2IPV4"] = str(IPLEAFipv4[numero_rack][spn+1])
        variablestochangeleaf1["IPIBGPIPV4"] = str(IPSIBGPipv4[numero_rack][j])
        variablestochangeleaf1["IPLEAFSP1IPV6"] = str(IPLEAFipv6[numero_rack][spn])
        variablestochangeleaf1["IPLEAFSP2IPV6"] = str(IPLEAFipv6[numero_rack][spn+1])
        variablestochangeleaf1["IPIBGPIPV6"] = str(IPSIBGPipv6[numero_rack][j])

        variablestochangeleaf1["VLANBELEAFSP1"] = str(VLANBELEAF[numero_rack][spn])
        variablestochangeleaf1["VLANBELEAFSP2"] = str(VLANBELEAF[numero_rack][spn+1])
        variablestochangeleaf1["VLANFELEAFSP1"] = str(VLANFELEAF[numero_rack][spn])
        variablestochangeleaf1["VLANFELEAFSP2"] = str(VLANFELEAF[numero_rack][spn+1])
        variablestochangeleaf1["VLANBORDALEAFSP1"] = str(VLANBORDALEAF[numero_rack][spn])
        variablestochangeleaf1["VLANBORDALEAFSP2"] = str(VLANBORDALEAF[numero_rack][spn+1])
        variablestochangeleaf1["VLANBORDACACHOSLEAFSP1"] = str(VLANBORDACACHOSLEAF[numero_rack][spn])
        variablestochangeleaf1["VLANBORDACACHOSLEAFSP2"] = str(VLANBORDACACHOSLEAF[numero_rack][spn+1])

        variablestochangeleaf1["ASLEAF"] = str(ASLEAF[numero_rack][0])

        variablestochangeleaf1["IPNEIGHSPINE1IPV4"] = str(IPSPINEipv4[numero_rack][spn])
        variablestochangeleaf1["IPNEIGHSPINE2IPV4"] = str(IPSPINEipv4[numero_rack][spn+1])
        variablestochangeleaf1["IPNEIGHSPINE1IPV6"] = str(IPSPINEipv6[numero_rack][spn])
        variablestochangeleaf1["IPNEIGHSPINE2IPV6"] = str(IPSPINEipv6[numero_rack][spn+1])

        if equip.get("nome")[-1] is 1:
            variablestochangeleaf1["IPNEIGHIBGPIPV4"] = str(IPSIBGPipv4[numero_rack][1])
            variablestochangeleaf1["IPNEIGHIBGPIPV6"] = str(IPSIBGPipv6[numero_rack][1])
        else:
            variablestochangeleaf1["IPNEIGHIBGPIPV4"] = str(IPSIBGPipv4[numero_rack][0])
            variablestochangeleaf1["IPNEIGHIBGPIPV6"] = str(IPSIBGPipv6[numero_rack][0])

        variablestochangeleaf1["NET_HOST_BE_IPV4"] = str(subnetsRackBEipv4[numero_rack])
        variablestochangeleaf1["NET_HOST_FE_IPV4"] = str(subnetsRackFEipv4[numero_rack])
        variablestochangeleaf1["NET_SPINE1_LF_IPV4"] = str(subSPINE1ipv4[numero_rack])
        variablestochangeleaf1["NET_SPINE2_LF_IPV4"] = str(subSPINE2ipv4[numero_rack])
        variablestochangeleaf1["NET_LF_LF_IPV4"] = str(subIBGPToRLxLipv4[numero_rack])
        variablestochangeleaf1["NET_HOST_BE_IPV6"] = str(subnetsRackBEipv6[numero_rack])
        variablestochangeleaf1["NET_HOST_FE_IPV6"] = str(subnetsRackFEipv6[numero_rack])
        variablestochangeleaf1["NET_SPINE1_LF_IPV6"] = str(subSPINE1ipv6[numero_rack])
        variablestochangeleaf1["NET_SPINE2_LF_IPV6"] = str(subSPINE2ipv6[numero_rack])
        variablestochangeleaf1["NET_LF_LF_IPV6"] = str(subIBGPToRLxLipv6[numero_rack])

        variablestochangeleaf1["ID_LEAF"] = str(equip.get("sw"))  # lf1 ou lf2
        variablestochangeleaf1["OWN_IP_MGMT"] = equip.get("ip_mngt")
        variablestochangeleaf1["LF_HOSTNAME"] = equip.get("nome")

        for i in equip.get("interfaces"):
            log.info("for i in equip")
            log.info(str(type(i.get("nome")[:3])))

            if i.get("nome")[:3] == prefixlf:
                variablestochangeleaf1["LFNEIGH_HOSTNAME"] = i.get("nome")
                variablestochangeleaf1["LFNEIGH_IP_MGMT"] = i.get("ip_mngt")
            elif i.get("nome")[:3] == prefixspn:
                spine_num = int(i.get("nome")[-1])
                variablestochangespine1["ASSPINE"] = str(BASE_AS_SPN+spine_num)
                variablestochangespine1["INTERFACE"] = i.get("interface")
                variablestochangespine1["LEAFNAME"] = equip.get("nome")
                variablestochangespine1["INT_LF_UPLINK"] = i.get("eq_interface")
                variablestochangespine1["IPSPINEIPV4"] = str(IPSPINEipv4[numero_rack][spine_num-1])
                variablestochangespine1["IPSPINEIPV6"] = str(IPSPINEipv6[numero_rack][spine_num-1])
                variablestochangespine1["VLANBELEAF"] = str(VLANBELEAF[numero_rack][spine_num-1])
                variablestochangespine1["VLANFELEAF"] = str(VLANFELEAF[numero_rack][spine_num-1])
                variablestochangespine1["VLANBORDALEAF"] = str(VLANBORDALEAF[numero_rack][spine_num-1])
                variablestochangespine1["VLANBORDACACHOSLEAF"] = str(VLANBORDACACHOSLEAF[numero_rack][spine_num-1])
                variablestochangespine1["ASLEAF"] = str(ASLEAF[numero_rack][0])
                variablestochangespine1["IPNEIGHLEAFIPV4"] = str(IPLEAFipv4[numero_rack][spine_num-1])
                variablestochangespine1["IPNEIGHLEAFIPV6"] = str(IPLEAFipv6[numero_rack][spine_num-1])
                if spine_num in [1, 3]:
                    variablestochangeleaf1["SP1_HOSTNAME"] = i.get("nome")
                    variablestochangeleaf1["INTERFACE_SP1"] = i.get("interface")
                    variablestochangeleaf1["ASSPINE1"] = str(BASE_AS_SPN+spine_num)
                else:
                    variablestochangeleaf1["SP2_HOSTNAME"] = i.get("nome")
                    variablestochangeleaf1["INTERFACE_SP2"] = i.get("interface")
                    variablestochangeleaf1["ASSPINE2"] = str(BASE_AS_SPN+spine_num)
                fileinspine1 = path_to_guide+i.get("roteiro")
                fileoutspine1 = path_to_add_config+i.get("nome")+"-ADD-"+rack.nome+".cfg"
                replace(fileinspine1, fileoutspine1, variablestochangespine1)
                variablestochangespine1 = dict()
            elif i.get("nome")[:3] == prefixoob:
                variablestochangeleaf1["HOSTNAME_OOB"] = i.get("nome")
                variablestochangeleaf1["INTERFACE_OOB"] = i.get("interface")

        variablestochangeleaf1["ID_VLT"] = str(id_vlt[j])
        variablestochangeleaf1["PRIORITY_VLT"] = str(priority_vlt[j])

        fileinleaf1 = path_to_guide + equip.get("roteiro")

        fileoutleaf1 = path_to_guide + equip.get("nome")+".cfg"
        replace(fileinleaf1, fileoutleaf1, variablestochangeleaf1)
        variablestochangeleaf1 = dict()

    return True


def autoprovision_coreoob(rack, equips):

    log.info("AutoprovisionOOB")

    variablestochangecore1 = dict()
    variablestochangecore2 = dict()
    variablestochangeoob = dict()

    prefixlf = "LF-"
    prefixoob = "OOB"

    try:
        path_to_guide = get_variable("path_to_guide")
        path_to_add_config = get_variable("path_to_add_config")
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável PATH_TO_GUIDE")

    envconfig = ast.literal_eval(rack.dcroom.config)
    vlan_base = envconfig.get("sala").get("gerencia_vlan")
    variablestochangeoob["VLAN_SO"] = str(int(vlan_base)+int(rack.numero))

    equips_sorted = sorted(equips, key=operator.itemgetter('sw'))
    oob = equips_sorted[-1]

    variablestochangeoob["OWN_IP_MGMT"] = oob.get("ip_mngt")
    variablestochangeoob["HOSTNAME_OOB"] = oob.get("nome")
    variablestochangeoob["HOSTNAME_RACK"] = rack.nome
    fileinoob = path_to_guide + oob.get("roteiro")
    fileoutoob = path_to_add_config + oob.get("nome") + ".cfg"

    for equip in oob.get("interfaces"):
        nome = equip.get("nome")
        roteiro = equip.get("roteiro")
        if nome[:3] == prefixlf:
            if nome[-1] == 1:
                variablestochangeoob["HOSTNAME_LF1"] = nome
            else:
                variablestochangeoob["HOSTNAME_LF2"] = nome
        elif nome[:3] == prefixoob:
            intoob = equip.get("eq_interface")
            intcore = equip.get("interface")
            if nome[-1] == "1":
                log.info("oob01")
                log.info(str(nome))
                hostname_core1 = nome
                variablestochangeoob["INT_OOBC1_UPLINK"] = intoob
                variablestochangeoob["INTERFACE_CORE1"] = intcore
                variablestochangeoob["HOSTNAME_CORE1"] = nome
                variablestochangecore1["INT_OOB_UPLINK"] = intoob
                variablestochangecore1["INTERFACE_CORE"] = intcore
                variablestochangecore1["HOSTNAME_RACK"] = rack.nome
                variablestochangecore1["SO_HOSTNAME_OOB"] = "SO_" + str(rack.nome)
                if (1+int(rack.numero)) % 2 == 0:
                    variablestochangecore1["HSRP_PRIORITY"] = "100"
                else:
                    variablestochangecore1["HSRP_PRIORITY"] = "101"
                fileincore1 = path_to_guide + roteiro
                fileoutcore1 = path_to_add_config + nome + "-ADD-" + str(rack.nome) + ".cfg"
            elif nome[-1] == "2":
                log.info("oob02")
                log.info(str(nome))
                hostname_core2 = nome
                variablestochangeoob["INT_OOBC2_UPLINK"] = intoob
                variablestochangeoob["INTERFACE_CORE2"] = intcore
                variablestochangeoob["HOSTNAME_CORE2"] = nome
                variablestochangecore2["INT_OOB_UPLINK"] = intoob
                variablestochangecore2["INTERFACE_CORE"] = intcore
                variablestochangecore2["HOSTNAME_RACK"] = rack.nome
                variablestochangecore2["SO_HOSTNAME_OOB"] = "SO_" + str(rack.nome)
                if (2+int(rack.numero)) % 2 == 0:
                    variablestochangecore2["HSRP_PRIORITY"] = "100"
                else:
                    variablestochangecore2["HSRP_PRIORITY"] = "101"
                fileincore2 = path_to_guide + roteiro
                fileoutcore2 = path_to_add_config + nome + "-ADD-" + str(rack.nome) + ".cfg"

    replace(fileincore1, fileoutcore1, variablestochangecore1)
    replace(fileincore2, fileoutcore2, variablestochangecore2)
    replace(fileinoob, fileoutoob, variablestochangeoob)

    return True
