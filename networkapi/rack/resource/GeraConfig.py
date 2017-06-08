# -*- coding: utf-8 -*-
import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from netaddr import IPNetwork

from networkapi.rack.models import RackConfigError
from networkapi.system import exceptions as var_exceptions
from networkapi.system.facade import get_value as get_variable

log = logging.getLogger(__name__)


def replace(filein, fileout, dicionario):
    try:
        # Read contents from file as a single string
        file_handle = open(filein, 'r')
        file_string = file_handle.read()
        file_handle.close()
    except:
        raise RackConfigError(
            None, None, 'Erro abrindo roteiro: %s.' % (filein))
    try:
        #
        for key in dicionario:
            # Use RE package to allow for replacement (also allowing for
            # (multiline) REGEX)
            file_string = (re.sub(key, dicionario[key], file_string))
    except:
        raise RackConfigError(
            None, None, 'Erro atualizando as variáveis no roteiro: %s.' % (filein))
    try:
        # Write contents to file.
        # Using mode 'w' truncates the file.
        file_handle = open(fileout, 'w')
        file_handle.write(file_string)
        file_handle.close()
    except:
        raise RackConfigError(
            None, None, 'Erro salvando arquivo de configuração: %s.' % (fileout))


def splitnetworkbyrack(net, bloco, posicao):
    subnets = list(net.subnet(bloco))
    return subnets[posicao]


def dic_vlan_core(variablestochangecore, rack, name_core, name_rack):
    """
    variablestochangecore: list
    rack: Numero do Rack
    name_core: Nome do Core
    name_rack: Nome do rack
    """

    core = int(name_core.split('-')[2])

    try:
        # valor base para as vlans e portchannels
        BASE_SO = int(get_variable('base_so'))
        # rede para conectar cores aos racks
        SO_OOB_NETipv4 = IPNetwork(get_variable('net_core'))
        # Vlan para cadastrar
        vlan_so_name = get_variable('vlan_so_name')
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável BASE_SO ou SO_OOB_NETipv4.')

    variablestochangecore['VLAN_SO'] = str(BASE_SO + rack)
    variablestochangecore['VLAN_NAME'] = vlan_so_name + name_rack
    variablestochangecore['VLAN_NUM'] = str(BASE_SO + rack)

    # Rede para cadastrar
    subSO_OOB_NETipv4 = list(SO_OOB_NETipv4.subnet(25))
    variablestochangecore['REDE_IP'] = str(
        subSO_OOB_NETipv4[rack]).split('/')[0]
    variablestochangecore['REDE_MASK'] = str(subSO_OOB_NETipv4[rack].prefixlen)
    variablestochangecore['NETMASK'] = str(subSO_OOB_NETipv4[rack].netmask)
    variablestochangecore['BROADCAST'] = str(subSO_OOB_NETipv4[rack].broadcast)

    # cadastro ip
    ip = 124 + core
    variablestochangecore['EQUIP_NAME'] = name_core
    variablestochangecore['IPCORE'] = str(subSO_OOB_NETipv4[rack][ip])

    # ja cadastrado
    variablestochangecore['IPHSRP'] = str(subSO_OOB_NETipv4[rack][1])
    variablestochangecore['NUM_CHANNEL'] = str(BASE_SO + rack)

    return variablestochangecore


def dic_lf_spn(user, rack):

    CIDREBGP = {}
    CIDRBE = {}
    ########
    VLANBELEAF = {}
    VLANFELEAF = {}
    VLANBORDALEAF = {}
    VLANBORDACACHOSLEAF = {}
    ########
    VLANBELEAF[rack] = []
    VLANFELEAF[rack] = []
    VLANBORDALEAF[rack] = []
    VLANBORDACACHOSLEAF[rack] = []

    ipv4_spn1 = dict()
    ipv4_spn2 = dict()
    ipv4_spn3 = dict()
    ipv4_spn4 = dict()
    redev6_spn1 = dict()
    redev6_spn2 = dict()
    redev6_spn3 = dict()
    redev6_spn4 = dict()

    try:
        BASE_RACK = int(get_variable('base_rack'))
        VLANBE = int(get_variable('vlanbe'))
        VLANFE = int(get_variable('vlanfe'))
        VLANBORDA = int(get_variable('vlanborda'))
        VLANBORDACACHOS = int(get_variable('vlanbordacachos'))
        VLANBETORxTOR = int(get_variable('vlanbetorxtor'))
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBE[0] = IPNetwork(get_variable('cidr_sl01'))
        CIDREBGP[0] = IPNetwork(get_variable('cidr_bgp'))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável BASE_RACK ou VLAN<BE,FE,BORDA,CACHOS,TORxTOR> ou CIDR<BE,EBGP>.')

    SPINE1ipv4 = IPNetwork(get_variable('net_spn01'))
    SPINE2ipv4 = IPNetwork(get_variable('net_spn02'))
    SPINE3ipv4 = IPNetwork(get_variable('net_spn03'))
    SPINE4ipv4 = IPNetwork(get_variable('net_spn04'))
    # REDE subSPINE1ipv4[rack]
    subSPINE1ipv4 = list(SPINE1ipv4.subnet(31))
    subSPINE2ipv4 = list(SPINE2ipv4.subnet(31))
    subSPINE3ipv4 = list(SPINE3ipv4.subnet(31))
    subSPINE4ipv4 = list(SPINE4ipv4.subnet(31))

    SPINE1ipv6 = IPNetwork(get_variable('net_spn01_v6'))
    SPINE2ipv6 = IPNetwork(get_variable('net_spn02_v6'))
    SPINE3ipv6 = IPNetwork(get_variable('net_spn03_v6'))
    SPINE4ipv6 = IPNetwork(get_variable('net_spn04_v6'))
    subSPINE1ipv6 = list(SPINE1ipv6.subnet(127))
    subSPINE2ipv6 = list(SPINE2ipv6.subnet(127))
    subSPINE3ipv6 = list(SPINE3ipv6.subnet(127))
    subSPINE4ipv6 = list(SPINE4ipv6.subnet(127))

    # Vlans BE RANGE
    VLANBELEAF[rack].append(VLANBE + rack)
    # rede subSPINE1ipv4[rack]
    VLANBELEAF[rack].append(VLANBE + rack + BASE_RACK)
    VLANBELEAF[rack].append(VLANBE + rack + 2 * BASE_RACK)
    VLANBELEAF[rack].append(VLANBE + rack + 3 * BASE_RACK)
    # Vlans FE RANGE
    VLANFELEAF[rack].append(VLANFE + rack)
    VLANFELEAF[rack].append(VLANFE + rack + BASE_RACK)
    VLANFELEAF[rack].append(VLANFE + rack + 2 * BASE_RACK)
    VLANFELEAF[rack].append(VLANFE + rack + 3 * BASE_RACK)
    # Vlans BORDA RANGE
    VLANBORDALEAF[rack].append(VLANBORDA + rack)
    VLANBORDALEAF[rack].append(VLANBORDA + rack + BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA + rack + 2 * BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA + rack + 3 * BASE_RACK)
    # Vlans BORDACACHOS RANGE
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack + BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack + 2 * BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack + 3 * BASE_RACK)
    #################
    # BD            #
    #################
    vlans = dict()
    vlans['VLANBELEAF'] = VLANBELEAF
    vlans['VLANFELEAF'] = VLANFELEAF
    vlans['VLANBORDALEAF'] = VLANBORDALEAF
    vlans['VLANBORDACACHOSLEAF'] = VLANBORDACACHOSLEAF
    vlans['BE'] = [VLANBE, VLANFE]
    vlans['FE'] = [VLANFE, VLANBORDA]
    vlans['BORDA'] = [VLANBORDA, VLANBORDACACHOS]
    vlans['BORDACACHOS'] = [VLANBORDACACHOS, VLANBETORxTOR]

    ipv4_spn1['REDE_IP'] = str(subSPINE1ipv4[rack].ip)
    ipv4_spn1['REDE_MASK'] = subSPINE1ipv4[rack].prefixlen
    ipv4_spn1['NETMASK'] = str(subSPINE1ipv4[rack].netmask)
    ipv4_spn1['BROADCAST'] = str(subSPINE1ipv4[rack].broadcast)

    ipv4_spn2['REDE_IP'] = str(subSPINE2ipv4[rack].ip)
    ipv4_spn2['REDE_MASK'] = subSPINE2ipv4[rack].prefixlen
    ipv4_spn2['NETMASK'] = str(subSPINE2ipv4[rack].netmask)
    ipv4_spn2['BROADCAST'] = str(subSPINE2ipv4[rack].broadcast)

    ipv4_spn3['REDE_IP'] = str(subSPINE3ipv4[rack].ip)
    ipv4_spn3['REDE_MASK'] = subSPINE3ipv4[rack].prefixlen
    ipv4_spn3['NETMASK'] = str(subSPINE3ipv4[rack].netmask)
    ipv4_spn3['BROADCAST'] = str(subSPINE3ipv4[rack].broadcast)

    ipv4_spn4['REDE_IP'] = str(subSPINE4ipv4[rack].ip)
    ipv4_spn4['REDE_MASK'] = subSPINE4ipv4[rack].prefixlen
    ipv4_spn4['NETMASK'] = str(subSPINE4ipv4[rack].netmask)
    ipv4_spn4['BROADCAST'] = str(subSPINE4ipv4[rack].broadcast)

    redev6_spn1['REDE_IP'] = str(subSPINE1ipv6[rack].ip)
    redev6_spn1['REDE_MASK'] = subSPINE1ipv6[rack].prefixlen
    redev6_spn1['NETMASK'] = str(subSPINE1ipv6[rack].netmask)
    redev6_spn1['BROADCAST'] = str(subSPINE1ipv6[rack].broadcast)

    redev6_spn2['REDE_IP'] = str(subSPINE2ipv6[rack].ip)
    redev6_spn2['REDE_MASK'] = subSPINE2ipv6[rack].prefixlen
    redev6_spn2['NETMASK'] = str(subSPINE2ipv6[rack].netmask)
    redev6_spn2['BROADCAST'] = str(subSPINE2ipv6[rack].broadcast)

    redev6_spn3['REDE_IP'] = str(subSPINE3ipv6[rack].ip)
    redev6_spn3['REDE_MASK'] = subSPINE3ipv6[rack].prefixlen
    redev6_spn3['NETMASK'] = str(subSPINE3ipv6[rack].netmask)
    redev6_spn3['BROADCAST'] = str(subSPINE3ipv6[rack].broadcast)

    redev6_spn4['REDE_IP'] = str(subSPINE4ipv6[rack].ip)
    redev6_spn4['REDE_MASK'] = subSPINE4ipv6[rack].prefixlen
    redev6_spn4['NETMASK'] = str(subSPINE4ipv6[rack].netmask)
    redev6_spn4['BROADCAST'] = str(subSPINE4ipv6[rack].broadcast)

    redes = dict()
    redes['SPINE1ipv4'] = str(SPINE1ipv4)
    redes['SPINE1ipv4_net'] = ipv4_spn1
    redes['SPINE2ipv4'] = str(SPINE2ipv4)
    redes['SPINE2ipv4_net'] = ipv4_spn2
    redes['SPINE3ipv4'] = str(SPINE3ipv4)
    redes['SPINE3ipv4_net'] = ipv4_spn3
    redes['SPINE4ipv4'] = str(SPINE4ipv4)
    redes['SPINE4ipv4_net'] = ipv4_spn4

    ipv6 = dict()
    ipv6['SPINE1ipv6'] = str(SPINE1ipv6)
    ipv6['SPINE1ipv6_net'] = redev6_spn1
    ipv6['SPINE2ipv6'] = str(SPINE2ipv6)
    ipv6['SPINE2ipv6_net'] = redev6_spn2
    ipv6['SPINE3ipv6'] = str(SPINE3ipv6)
    ipv6['SPINE3ipv6_net'] = redev6_spn3
    ipv6['SPINE4ipv6'] = str(SPINE4ipv6)
    ipv6['SPINE4ipv6_net'] = redev6_spn4

    return vlans, redes, ipv6


def dic_pods(rack):

    subnetsRackBEipv4 = {}
    subnetsRackBEipv4[rack] = []

    PODSBEipv4 = {}
    redesPODSBEipv4 = {}
    PODSBEFEipv4 = {}
    redesPODSBEFEipv4 = {}
    PODSBEBOipv4 = {}
    redesPODSBEBOipv4 = {}
    PODSBECAipv4 = {}
    redesPODSBECAipv4 = {}

    PODSBEipv4[rack] = []
    redesPODSBEipv4[rack] = []
    PODSBEFEipv4[rack] = []
    redesPODSBEFEipv4[rack] = []
    PODSBEBOipv4[rack] = []
    redesPODSBEBOipv4[rack] = []
    PODSBECAipv4[rack] = []
    redesPODSBECAipv4[rack] = []

    PODSBEipv6 = {}
    redesPODSBEipv6 = {}
    PODSBEFEipv6 = {}
    redesPODSBEFEipv6 = {}
    PODSBEBOipv6 = {}
    redesPODSBEBOipv6 = {}
    PODSBECAipv6 = {}
    redesPODSBECAipv6 = {}
    subnetsRackBEipv6 = {}

    PODSBEipv6[rack] = []
    redesPODSBEipv6[rack] = []
    PODSBEFEipv6[rack] = []
    redesPODSBEFEipv6[rack] = []
    PODSBEBOipv6[rack] = []
    redesPODSBEBOipv6[rack] = []
    PODSBECAipv6[rack] = []
    redesPODSBECAipv6[rack] = []
    subnetsRackBEipv6[rack] = []

    try:
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBEipv4 = IPNetwork(get_variable('cidr_be_v4'))
        CIDRBEipv6 = IPNetwork(get_variable('cidr_be_v6'))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável CIDR<BEv4,BEv6>.')

    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::

    # Redes p/ rack => 10.128.0.0/19, 10.128.32.0/19 , ... ,10.143.224.0/19
    subnetsRackBEipv4[rack] = splitnetworkbyrack(CIDRBEipv4, 19, rack)
    subnetsRackBEipv6[rack] = splitnetworkbyrack(CIDRBEipv6, 55, rack)

    # PODS BE => /20
    subnetteste = subnetsRackBEipv4[rack]
    subnetteste_ipv6 = subnetsRackBEipv6[rack]

    PODSBEipv4[rack] = splitnetworkbyrack(subnetteste, 20, 0)
    PODSBEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 57, 0)
    # => 256 redes /28     # Vlan 2 a 129
    redesPODSBEipv4[rack] = list(PODSBEipv4[rack].subnet(28))
    redesPODSBEipv6[rack] = list(PODSBEipv6[rack].subnet(64))
    # PODS BEFE => 10.128.16.0/21
    PODSBEFEipv4[rack] = splitnetworkbyrack(
        splitnetworkbyrack(subnetteste, 20, 1), 21, 0)
    PODSBEFEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 57, 1)
    # => 128 redes /28    # Vlan 130 a 193
    redesPODSBEFEipv4[rack] = list(PODSBEFEipv4[rack].subnet(28))
    redesPODSBEFEipv6[rack] = list(PODSBEFEipv6[rack].subnet(64))
    # PODS BEBO => 10.128.24.0/22
    PODSBEBOipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(
        splitnetworkbyrack(subnetteste, 20, 1), 21, 1), 22, 0)
    PODSBEBOipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 57, 2)
    # => 64 redes /28    # Vlan 194 a 257
    redesPODSBEBOipv4[rack] = list(PODSBEBOipv4[rack].subnet(28))
    redesPODSBEBOipv6[rack] = list(PODSBEBOipv6[rack].subnet(64))
    # PODS BECA => 10.128.28.0/23
    PODSBECAipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(
        splitnetworkbyrack(subnetteste, 20, 1), 21, 1), 22, 1), 23, 0)
    PODSBECAipv6[rack] = splitnetworkbyrack(
        splitnetworkbyrack(subnetteste_ipv6, 57, 3), 58, 0)
    # => 32 redes /28    # Vlan 258 a 289
    redesPODSBECAipv4[rack] = list(PODSBECAipv4[rack].subnet(28))
    redesPODSBECAipv6[rack] = list(PODSBECAipv6[rack].subnet(64))

    redes = dict()
    ipv6 = dict()
    redes['BE_VLAN_MIN'] = int(get_variable('be_vlan_min'))
    redes['BE_VLAN_MAX'] = int(get_variable('be_vlan_max'))
    redes['BE_PREFIX'] = str(redesPODSBEipv4[rack][0].prefixlen)
    redes['BE_REDE'] = str(PODSBEipv4[rack])
    ipv6['BE_PREFIX'] = str(redesPODSBEipv6[rack][0].prefixlen)
    ipv6['BE_REDE'] = str(PODSBEipv6[rack])

    redes['BEFE_VLAN_MIN'] = int(get_variable('befe_vlan_min'))
    redes['BEFE_VLAN_MAX'] = int(get_variable('befe_vlan_max'))
    redes['BEFE_PREFIX'] = str(redesPODSBEFEipv4[rack][0].prefixlen)
    redes['BEFE_REDE'] = str(PODSBEFEipv4[rack])
    ipv6['BEFE_PREFIX'] = str(redesPODSBEFEipv6[rack][0].prefixlen)
    ipv6['BEFE_REDE'] = str(PODSBEFEipv6[rack])

    redes['BEBORDA_VLAN_MIN'] = int(get_variable('beborda_vlan_min'))
    redes['BEBORDA_VLAN_MAX'] = int(get_variable('beborda_vlan_max'))
    redes['BEBORDA_PREFIX'] = str(redesPODSBEBOipv4[rack][0].prefixlen)
    redes['BEBORDA_REDE'] = str(PODSBEBOipv4[rack])
    ipv6['BEBORDA_PREFIX'] = str(redesPODSBEBOipv6[rack][0].prefixlen)
    ipv6['BEBORDA_REDE'] = str(PODSBEBOipv6[rack])

    redes['BECACHOS_VLAN_MIN'] = int(get_variable('becachos_vlan_min'))
    redes['BECACHOS_VLAN_MAX'] = int(get_variable('becachos_vlan_max'))
    redes['BECACHOS_PREFIX'] = str(redesPODSBECAipv4[rack][0].prefixlen)
    redes['BECACHOS_REDE'] = str(PODSBECAipv4[rack])
    ipv6['BECACHOS_PREFIX'] = str(redesPODSBECAipv6[rack][0].prefixlen)
    ipv6['BECACHOS_REDE'] = str(PODSBECAipv6[rack])

    return redes, ipv6


def dic_hosts_cloud(rack):

    subnetsRackBEipv4 = {}
    subnetsRackBEipv4[rack] = []
    redesHostsipv4 = {}
    redesHostsipv4[rack] = []
    redeHostsBEipv4 = {}
    redeHostsBEipv4[rack] = []
    redeHostsFEipv4 = {}
    redeHostsFEipv4[rack] = []
    redeHostsBOipv4 = {}
    redeHostsBOipv4[rack] = []
    redeHostsCAipv4 = {}
    redeHostsCAipv4[rack] = []
    redeHostsFILERipv4 = {}
    redeHostsFILERipv4[rack] = []

    subnetsRackBEipv6 = {}
    subnetsRackBEipv6[rack] = []
    redesHostsipv6 = {}
    redesHostsipv6[rack] = []
    redeHostsBEipv6 = {}
    redeHostsBEipv6[rack] = []
    redeHostsFEipv6 = {}
    redeHostsFEipv6[rack] = []
    redeHostsBOipv6 = {}
    redeHostsBOipv6[rack] = []
    redeHostsCAipv6 = {}
    redeHostsCAipv6[rack] = []
    redeHostsFILERipv6 = {}
    redeHostsFILERipv6[rack] = []

    hosts = dict()
    BE = dict()
    FE = dict()
    BO = dict()
    CA = dict()
    FILER = dict()
    ipv6 = dict()
    BE_ipv6 = dict()
    FE_ipv6 = dict()
    BO_ipv6 = dict()
    CA_ipv6 = dict()
    FILER_ipv6 = dict()

    try:
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBEipv4 = IPNetwork(get_variable('cidr_be_v4'))
        CIDRBEipv6 = IPNetwork(get_variable('cidr_be_v6'))
        hosts['VLAN_MNGT_BE'] = int(get_variable('vlan_mngt_be'))
        hosts['VLAN_MNGT_FE'] = int(get_variable('vlan_mngt_fe'))
        hosts['VLAN_MNGT_BO'] = int(get_variable('vlan_mngt_bo'))
        hosts['VLAN_MNGT_CA'] = int(get_variable('vlan_mngt_ca'))
        hosts['VLAN_MNGT_FILER'] = int(get_variable('vlan_mngt_filer'))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável VLAN_MNGT<BE,FE,BO,CA,FILER> ou CIDR<BEv4,BEv6>.')

    subnetsRackBEipv4[rack] = splitnetworkbyrack(
        CIDRBEipv4, 19, rack)  # 10.128.32.0/19
    subnetteste = subnetsRackBEipv4[rack]  # 10.128.32.0/19

    subnetsRackBEipv6[rack] = splitnetworkbyrack(splitnetworkbyrack(
        splitnetworkbyrack(CIDRBEipv6, 55, rack), 57, 3), 58, 1)
    subnetteste_ipv6 = splitnetworkbyrack(subnetsRackBEipv6[rack], 61, 7)

    # VLANS CLoud
    # ambiente BE - MNGT_NETWORK - RACK_AAXX
    # 10.128.30.0/23
    # vlans MNGT_BE/FE/BO/CA/FILER
    # PODS BE => /20
    # Hosts => 10.128.30.0/23
    redesHostsipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(
        splitnetworkbyrack(splitnetworkbyrack(subnetteste, 20, 1), 21, 1), 22, 1), 23, 1)
    redesHostsipv6[rack] = subnetteste_ipv6
    # Hosts BE => 10.128.30.0/24 => 256 endereços
    redeHostsBEipv4[rack] = splitnetworkbyrack(redesHostsipv4[rack], 24, 0)
    redeHostsBEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 3)
    # Hosts FE => 10.128.31.0/25 => 128 endereços
    redeHostsFEipv4[rack] = splitnetworkbyrack(
        splitnetworkbyrack(redesHostsipv4[rack], 24, 1), 25, 0)
    redeHostsFEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 4)
    # Hosts BO => 10.128.31.128/26 => 64 endereços
    redeHostsBOipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(
        splitnetworkbyrack(redesHostsipv4[rack], 24, 1), 25, 1), 26, 0)
    redeHostsBOipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 5)
    # Hosts CA => 10.128.31.192/27 => 32 endereços
    redeHostsCAipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(
        splitnetworkbyrack(redesHostsipv4[rack], 24, 1), 25, 1), 26, 1), 27, 0)
    redeHostsCAipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 6)
    # Hosts FILER => 10.128.15.224/27 => 32 endereços
    redeHostsFILERipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(
        splitnetworkbyrack(redesHostsipv4[rack], 24, 1), 25, 1), 26, 1), 27, 1)
    redeHostsFILERipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 7)

    hosts['PREFIX'] = str(redesHostsipv4[rack].prefixlen)
    hosts['REDE'] = str(redesHostsipv4[rack])
    BE['REDE_IP'] = str(redeHostsBEipv4[rack].ip)
    BE['REDE_MASK'] = redeHostsBEipv4[rack].prefixlen
    BE['NETMASK'] = str(redeHostsBEipv4[rack].netmask)
    BE['BROADCAST'] = str(redeHostsBEipv4[rack].broadcast)
    hosts['BE'] = BE
    FE['REDE_IP'] = str(redeHostsFEipv4[rack].ip)
    FE['REDE_MASK'] = redeHostsFEipv4[rack].prefixlen
    FE['NETMASK'] = str(redeHostsFEipv4[rack].netmask)
    FE['BROADCAST'] = str(redeHostsFEipv4[rack].broadcast)
    hosts['FE'] = FE
    BO['REDE_IP'] = str(redeHostsBOipv4[rack].ip)
    BO['REDE_MASK'] = redeHostsBOipv4[rack].prefixlen
    BO['NETMASK'] = str(redeHostsBOipv4[rack].netmask)
    BO['BROADCAST'] = str(redeHostsBOipv4[rack].broadcast)
    hosts['BO'] = BO
    CA['REDE_IP'] = str(redeHostsCAipv4[rack].ip)
    CA['REDE_MASK'] = redeHostsCAipv4[rack].prefixlen
    CA['NETMASK'] = str(redeHostsCAipv4[rack].netmask)
    CA['BROADCAST'] = str(redeHostsCAipv4[rack].broadcast)
    hosts['CA'] = CA
    FILER['REDE_IP'] = str(redeHostsFILERipv4[rack].ip)
    FILER['REDE_MASK'] = redeHostsFILERipv4[rack].prefixlen
    FILER['NETMASK'] = str(redeHostsFILERipv4[rack].netmask)
    FILER['BROADCAST'] = str(redeHostsFILERipv4[rack].broadcast)
    hosts['FILER'] = FILER

    ipv6['PREFIX'] = str(redesHostsipv6[rack].prefixlen)
    ipv6['REDE'] = str(redesHostsipv6[rack])
    BE_ipv6['REDE_IP'] = str(redeHostsBEipv6[rack].ip)
    BE_ipv6['REDE_MASK'] = redeHostsBEipv6[rack].prefixlen
    BE_ipv6['NETMASK'] = str(redeHostsBEipv6[rack].netmask)
    BE_ipv6['BROADCAST'] = str(redeHostsBEipv6[rack].broadcast)
    ipv6['BE'] = BE_ipv6
    FE_ipv6['REDE_IP'] = str(redeHostsFEipv6[rack].ip)
    FE_ipv6['REDE_MASK'] = redeHostsFEipv6[rack].prefixlen
    FE_ipv6['NETMASK'] = str(redeHostsFEipv6[rack].netmask)
    FE_ipv6['BROADCAST'] = str(redeHostsFEipv6[rack].broadcast)
    ipv6['FE'] = FE_ipv6
    BO_ipv6['REDE_IP'] = str(redeHostsBOipv6[rack].ip)
    BO_ipv6['REDE_MASK'] = redeHostsBOipv6[rack].prefixlen
    BO_ipv6['NETMASK'] = str(redeHostsBOipv6[rack].netmask)
    BO_ipv6['BROADCAST'] = str(redeHostsBOipv6[rack].broadcast)
    ipv6['BO'] = BO_ipv6
    CA_ipv6['REDE_IP'] = str(redeHostsCAipv6[rack].ip)
    CA_ipv6['REDE_MASK'] = redeHostsCAipv6[rack].prefixlen
    CA_ipv6['NETMASK'] = str(redeHostsCAipv6[rack].netmask)
    CA_ipv6['BROADCAST'] = str(redeHostsCAipv6[rack].broadcast)
    ipv6['CA'] = CA_ipv6
    FILER_ipv6['REDE_IP'] = str(redeHostsFILERipv6[rack].ip)
    FILER_ipv6['REDE_MASK'] = redeHostsFILERipv6[rack].prefixlen
    FILER_ipv6['NETMASK'] = str(redeHostsFILERipv6[rack].netmask)
    FILER_ipv6['BROADCAST'] = str(redeHostsFILERipv6[rack].broadcast)
    ipv6['FILER'] = FILER_ipv6
    return hosts, ipv6


def dic_fe_prod(rack):

    CIDRFEipv4 = {}
    CIDRFEipv4[rack] = []
    CIDRFEipv6 = {}
    CIDRFEipv6[rack] = []

    subnetsRackFEipv4 = {}
    subnetsRackFEipv4[rack] = []
    subnetsRackFEipv6 = {}
    subnetsRackFEipv6[rack] = []

    podsFEipv4 = {}
    podsFEipv4[rack] = []
    podsFEipv6 = {}
    podsFEipv6[rack] = []

    redes = dict()
    ranges = dict()
    ipv6 = dict()

    try:
        # CIDR sala 01 => 172.20.0.0/14
        # Sumário do rack => 172.20.0.0/21
        CIDRFEipv4[0] = IPNetwork(get_variable('cidr_fe_v4'))
        # CIDRFE[1] = IPNetwork('172.20.1.0/14')
        CIDRFEipv6[0] = IPNetwork(get_variable('cidr_fe_v6'))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável VLAN_MNGT<BE,FE,BO,CA,FILER> ou CIDR<FEv4,FEv6>.')

    # Sumário do rack => 172.20.0.0/21
    subnetsRackFEipv4[rack] = splitnetworkbyrack(CIDRFEipv4[0], 21, rack)
    subnetsRackFEipv6[rack] = splitnetworkbyrack(CIDRFEipv6[0], 57, rack)

    podsFEipv4[rack] = splitnetworkbyrack(subnetsRackFEipv4[rack], 28, 0)
    podsFEipv6[rack] = splitnetworkbyrack(subnetsRackFEipv6[rack], 64, 3)

    ranges['MAX'] = int(get_variable('fe_vlan_min'))
    ranges['MIN'] = int(get_variable('fe_vlan_max'))
    redes['PREFIX'] = podsFEipv4[rack].prefixlen
    redes['REDE'] = str(subnetsRackFEipv4[rack])

    ipv6['PREFIX'] = podsFEipv6[rack].prefixlen
    ipv6['REDE'] = str(subnetsRackFEipv6[rack])
    return redes, ranges, ipv6

def autoprovision_coreoob(rack, FILEINCR1, FILEINCR2, FILEINOOB, name_core1, name_core2, name_oob, name_lf1, name_lf2,
                          ip_mgmtoob, int_oob_core1, int_oob_core2, int_core1_oob, int_core2_oob ):

    # gerando dicionarios para substituir paravras chaves do roteiro
    variablestochangecore1 = {}
    variablestochangecore2 = {}
    variablestochangeoob = {}

    # nome dos cores, do console de gerencia dos lf do rack, e do rack
    HOSTNAME_CORE1 = name_core1
    HOSTNAME_CORE2 = name_core2
    HOSTNAME_OOB = name_oob
    HOSTNAME_RACK = HOSTNAME_OOB.split('-')
    HOSTNAME_LF1 = name_lf1
    HOSTNAME_LF2 = name_lf2

    # interfaces de conexão entre os cores e o console
    INT_OOBC1_UPLINK = int_oob_core1
    INT_OOBC2_UPLINK = int_oob_core2
    INTERFACE_CORE1 = int_core1_oob
    INTERFACE_CORE2 = int_core2_oob

    # ip de gerencia do oob
    IP_GERENCIA_OOB = ip_mgmtoob

    try:
        # roteiro para configuracao de core
        fileincore1 = get_variable('path_to_guide') + FILEINCR1
        fileincore2 = get_variable('path_to_guide') + FILEINCR2
        fileinoob = get_variable('path_to_guide') + FILEINOOB
        # valor base para as vlans e portchannels
        BASE_SO = int(get_variable('base_so'))
        # arquivos de saida, OOB-CM-01.cfg e OOB-CM-02.cfg
        fileoutcore1 = get_variable(
            'path_to_add_config') + HOSTNAME_CORE1 + '-ADD-' + HOSTNAME_RACK[2] + '.cfg'
        fileoutcore2 = get_variable(
            'path_to_add_config') + HOSTNAME_CORE2 + '-ADD-' + HOSTNAME_RACK[2] + '.cfg'
        fileoutoob = get_variable('path_to_config') + HOSTNAME_OOB + '.cfg'
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável PATH_TO_<GUIDE, CONFIG> ou BASE_SO.')

    variablestochangeoob['OWN_IP_MGMT'] = IP_GERENCIA_OOB
    variablestochangeoob['INT_OOBC1_UPLINK'] = INT_OOBC1_UPLINK
    variablestochangeoob['INT_OOBC2_UPLINK'] = INT_OOBC2_UPLINK
    variablestochangeoob['INTERFACE_CORE1'] = INTERFACE_CORE1
    variablestochangeoob['INTERFACE_CORE2'] = INTERFACE_CORE2
    variablestochangeoob['HOSTNAME_CORE1'] = HOSTNAME_CORE1
    variablestochangeoob['HOSTNAME_CORE2'] = HOSTNAME_CORE2
    variablestochangeoob['HOSTNAME_OOB'] = HOSTNAME_OOB
    variablestochangeoob['HOSTNAME_LF1'] = HOSTNAME_LF1
    variablestochangeoob['HOSTNAME_LF2'] = HOSTNAME_LF2
    variablestochangeoob['VLAN_SO'] = str(BASE_SO + rack)
    variablestochangeoob['HOSTNAME_RACK'] = HOSTNAME_RACK[2]

    variablestochangecore1['INT_OOB_UPLINK'] = INT_OOBC1_UPLINK
    variablestochangecore1['INTERFACE_CORE'] = INTERFACE_CORE1
    variablestochangecore1['HOSTNAME_RACK'] = HOSTNAME_RACK[2]
    variablestochangecore1['SO_HOSTNAME_OOB'] = 'SO_' + HOSTNAME_RACK[2]
    if (1 + rack) % 2 == 0:
        variablestochangecore1['HSRP_PRIORITY'] = '100'
    else:
        variablestochangecore1['HSRP_PRIORITY'] = '101'

    variablestochangecore2['INT_OOB_UPLINK'] = INT_OOBC2_UPLINK
    variablestochangecore2['INTERFACE_CORE'] = INTERFACE_CORE2
    variablestochangecore2['HOSTNAME_RACK'] = HOSTNAME_RACK[2]
    variablestochangecore2['SO_HOSTNAME_OOB'] = 'SO_' + HOSTNAME_RACK[2]
    if(2 + rack) % 2 == 0:
        variablestochangecore2['HSRP_PRIORITY'] = '100'
    else:
        variablestochangecore2['HSRP_PRIORITY'] = '101'

    variablestochangecore1 = dic_vlan_core(
        variablestochangecore1, rack, HOSTNAME_CORE1, HOSTNAME_RACK[2])
    variablestochangecore2 = dic_vlan_core(
        variablestochangecore2, rack, HOSTNAME_CORE2, HOSTNAME_RACK[2])
    variablestochangeoob = dic_vlan_core(
        variablestochangeoob, rack, HOSTNAME_CORE1, HOSTNAME_RACK[2])

    # gerando arquivos de saida
    replace(fileincore1, fileoutcore1, variablestochangecore1)
    replace(fileincore2, fileoutcore2, variablestochangecore2)
    replace(fileinoob, fileoutoob, variablestochangeoob)

    return True

def autoprovision_splf(rack,FILEINLF1, FILEINLF2,FILEINSP1, FILEINSP2, FILEINSP3, FILEINSP4,name_lf1, name_lf2, name_oob,
                       name_sp1, name_sp2, name_sp3, name_sp4, ip_mgmtlf1, ip_mgmtlf2, int_oob_mgmtlf1, int_oob_mgmtlf2,
                       int_sp1, int_sp2, int_sp3, int_sp4, int_lf1_sp1,int_lf1_sp2,int_lf2_sp3,int_lf2_sp4):

    # STRUCTURE: IPSPINE[rack][spine]: ip a configurar no spine 'spine' relativo à leaf do rack 'rack'
    # STRUCTURE: IPLEAF[rack][spine]: ip a configurar no leaf do rack 'rack' relativo ao spine 'spine'

    CIDREBGP = {}
    CIDRBE = {}
    IPSPINEipv4 = {}
    IPSPINEipv6 = {}
    IPLEAFipv4 = {}
    IPLEAFipv6 = {}
    IPSIBGPipv4 = {}
    IPSIBGPipv6 = {}
    ASLEAF = {}
    #
    VLANBELEAF = {}
    VLANFELEAF = {}
    VLANBORDALEAF = {}
    VLANBORDACACHOSLEAF = {}
    #
    PODSBEipv4 = {}
    redesPODSBEipv4 = {}
    #
    subnetsRackBEipv4 = {}
    #
    PODSBEipv6 = {}
    redesPODSBEipv6 = {}
    PODSBEFEipv6 = {}
    redesPODSBEFEipv6 = {}
    PODSBEBOipv6 = {}
    redesPODSBEBOipv6 = {}
    PODSBECAipv6 = {}
    redesPODSBECAipv6 = {}
    redesHostsipv6 = {}
    redeHostsBEipv6 = {}
    redeHostsFEipv6 = {}
    redeHostsBOipv6 = {}
    redeHostsCAipv6 = {}
    redeHostsFILERipv6 = {}
    subnetsRackBEipv6 = {}
    subnetsRackFEipv4 = {}
    redesPODSFEipv4 = {}
    subnetsRackFEipv6 = {}
    redesPODSFEipv6 = {}
    #
    IPSPINEipv4[rack] = []
    IPSPINEipv6[rack] = []
    IPLEAFipv4[rack] = []
    IPLEAFipv6[rack] = []
    IPSIBGPipv4[rack] = []
    IPSIBGPipv6[rack] = []
    VLANBELEAF[rack] = []
    VLANFELEAF[rack] = []
    VLANBORDALEAF[rack] = []
    VLANBORDACACHOSLEAF[rack] = []
    ASLEAF[rack] = []
    #
    PODSBEipv4[rack] = []
    redesPODSBEipv4[rack] = []
    #
    subnetsRackBEipv4[rack] = []
    #
    PODSBEipv6[rack] = []
    redesPODSBEipv6[rack] = []
    PODSBEFEipv6[rack] = []
    redesPODSBEFEipv6[rack] = []
    PODSBEBOipv6[rack] = []
    redesPODSBEBOipv6[rack] = []
    PODSBECAipv6[rack] = []
    redesPODSBECAipv6[rack] = []
    redesHostsipv6[rack] = []
    redeHostsBEipv6[rack] = []
    redeHostsFEipv6[rack] = []
    redeHostsBOipv6[rack] = []
    redeHostsCAipv6[rack] = []
    redeHostsFILERipv6[rack] = []
    subnetsRackBEipv6[rack] = []
    subnetsRackFEipv4[rack] = []
    redesPODSFEipv4[rack] = []
    subnetsRackFEipv6[rack] = []
    redesPODSFEipv6[rack] = []

    CIDRFEipv4 = {}
    CIDRFEipv6 = {}

    variablestochangespine1 = {}
    variablestochangespine2 = {}
    variablestochangespine3 = {}
    variablestochangespine4 = {}
    variablestochangeleaf1 = {}
    variablestochangeleaf2 = {}

    try:
        fileinleaf1=get_variable("path_to_guide")+FILEINLF1
        fileinleaf2=get_variable("path_to_guide")+FILEINLF2
        fileinspine1=get_variable("path_to_guide")+FILEINSP1
        fileinspine2=get_variable("path_to_guide")+FILEINSP2
        fileinspine3=get_variable("path_to_guide")+FILEINSP3
        fileinspine4=get_variable("path_to_guide")+FILEINSP4
        ###
        BASE_RACK = int(get_variable("base_rack"))
        BASE_AS = int(get_variable("base_as"))
        VLANBE = int(get_variable("vlanbe"))
        VLANFE = int(get_variable("vlanfe"))
        VLANBORDA = int(get_variable("vlanborda"))
        VLANBORDACACHOS = int(get_variable("vlanbordacachos"))
        ###

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável PATH_TO_GUIDE ou BASE_<RACK,AS> ou VLAN<BE,FE,BORDA,CACHOS>.')

    HOSTNAME_LF1 = name_lf1
    HOSTNAME_LF2 = name_lf2
    HOSTNAME_OOB = name_oob

    HOSTNAME_SP1 = name_sp1
    HOSTNAME_SP2 = name_sp2
    HOSTNAME_SP3 = name_sp3
    HOSTNAME_SP4 = name_sp4

    HOSTNAME_RACK = HOSTNAME_OOB.split('-')

    IP_GERENCIA_LF1 = ip_mgmtlf1
    IP_GERENCIA_LF2 = ip_mgmtlf2

    INTERFACE_SP1 = int_sp1
    INTERFACE_SP2 = int_sp2
    INTERFACE_SP3 = int_sp3
    INTERFACE_SP4 = int_sp4
    INTERFACE_OOB_LF1 = int_oob_mgmtlf1
    INTERFACE_OOB_LF2 = int_oob_mgmtlf2

    try:
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBE[0] = IPNetwork(get_variable('cidr_be_v4'))
        CIDREBGP[0] = IPNetwork(get_variable('cidr_be_v6'))
        SPINE1ipv4 = IPNetwork(get_variable('net_spn01'))
        SPINE2ipv4 = IPNetwork(get_variable('net_spn02'))
        SPINE3ipv4 = IPNetwork(get_variable('net_spn03'))
        SPINE4ipv4 = IPNetwork(get_variable('net_spn04'))
        SPINE1ipv6 = IPNetwork(get_variable('net_spn01_v6'))
        SPINE2ipv6 = IPNetwork(get_variable('net_spn02_v6'))
        SPINE3ipv6 = IPNetwork(get_variable('net_spn03_v6'))
        SPINE4ipv6 = IPNetwork(get_variable('net_spn04_v6'))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável CIDR<BE,EBGP> ou <BE,FE,BORDA,CACHOS> ou SPINE<1,2,3,4>ipv6.')

    subSPINE1ipv4 = list(SPINE1ipv4.subnet(31))
    subSPINE2ipv4 = list(SPINE2ipv4.subnet(31))
    subSPINE3ipv4 = list(SPINE3ipv4.subnet(31))
    subSPINE4ipv4 = list(SPINE4ipv4.subnet(31))
    subSPINE1ipv6 = list(SPINE1ipv6.subnet(127))
    subSPINE2ipv6 = list(SPINE2ipv6.subnet(127))
    subSPINE3ipv6 = list(SPINE3ipv6.subnet(127))
    subSPINE4ipv6 = list(SPINE4ipv6.subnet(127))

    try:
        IBGPToRLxLipv4 = IPNetwork(get_variable('ibgptorlxlip_v4'))
        IBGPToRLxLipv6 = IPNetwork(get_variable('ibgptorlxlip_v6'))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável IBGPToRLxL<ipv4,ipv6>.')

    subIBGPToRLxLipv4 = list(IBGPToRLxLipv4.subnet(31))
    subIBGPToRLxLipv6 = list(IBGPToRLxLipv6.subnet(127))

    IPSPINEipv4[rack].append(subSPINE1ipv4[rack][0])
    IPSPINEipv4[rack].append(subSPINE2ipv4[rack][0])
    IPSPINEipv4[rack].append(subSPINE3ipv4[rack][0])
    IPSPINEipv4[rack].append(subSPINE4ipv4[rack][0])
    #
    IPLEAFipv4[rack].append(subSPINE1ipv4[rack][1])
    IPLEAFipv4[rack].append(subSPINE2ipv4[rack][1])
    IPLEAFipv4[rack].append(subSPINE3ipv4[rack][1])
    IPLEAFipv4[rack].append(subSPINE4ipv4[rack][1])
    #
    IPSIBGPipv4[rack].append(subIBGPToRLxLipv4[rack][0])
    IPSIBGPipv4[rack].append(subIBGPToRLxLipv4[rack][1])
    #
    IPSPINEipv6[rack].append(subSPINE1ipv6[rack][0])
    IPSPINEipv6[rack].append(subSPINE2ipv6[rack][0])
    IPSPINEipv6[rack].append(subSPINE3ipv6[rack][0])
    IPSPINEipv6[rack].append(subSPINE4ipv6[rack][0])
    #
    IPLEAFipv6[rack].append(subSPINE1ipv6[rack][1])
    IPLEAFipv6[rack].append(subSPINE2ipv6[rack][1])
    IPLEAFipv6[rack].append(subSPINE3ipv6[rack][1])
    IPLEAFipv6[rack].append(subSPINE4ipv6[rack][1])
    #
    IPSIBGPipv6[rack].append(subIBGPToRLxLipv6[rack][0])
    IPSIBGPipv6[rack].append(subIBGPToRLxLipv6[rack][1])
    #
    VLANBELEAF[rack].append(VLANBE + rack)
    VLANBELEAF[rack].append(VLANBE + rack + BASE_RACK)
    VLANBELEAF[rack].append(VLANBE + rack + 2 * BASE_RACK)
    VLANBELEAF[rack].append(VLANBE + rack + 3 * BASE_RACK)
    #
    VLANFELEAF[rack].append(VLANFE + rack)
    VLANFELEAF[rack].append(VLANFE + rack + BASE_RACK)
    VLANFELEAF[rack].append(VLANFE + rack + 2 * BASE_RACK)
    VLANFELEAF[rack].append(VLANFE + rack + 3 * BASE_RACK)
    #
    VLANBORDALEAF[rack].append(VLANBORDA + rack)
    VLANBORDALEAF[rack].append(VLANBORDA + rack + BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA + rack + 2 * BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA + rack + 3 * BASE_RACK)
    #
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack + BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack + 2 * BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS + rack + 3 * BASE_RACK)
    #
    ASLEAF[rack].append(BASE_AS + rack)

    ##########################################################################
    try:
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBEipv4 = IPNetwork(get_variable('cidr_be_v4'))
        CIDRBEipv6 = IPNetwork(get_variable('cidr_be_v6'))
        # CIDR sala 01 => 172.20.0.0/14
        # Sumário do rack => 172.20.0.0/21
        CIDRFEipv4[0] = IPNetwork(get_variable('cidr_fe_v4'))
        # CIDRFE[1] = IPNetwork('172.20.1.0/14')
        CIDRFEipv6[0] = IPNetwork(get_variable('cidr_fe_v6'))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável CIDR<FE,BE><ipv4,ipv6>.')

    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::
    # Redes p/ rack => 10.128.0.0/19, 10.128.32.0/19 , ... ,10.143.224.0/19
    subnetsRackBEipv4[rack] = splitnetworkbyrack(CIDRBEipv4, 19, rack)
    subnetsRackBEipv6[rack] = splitnetworkbyrack(CIDRBEipv6, 55, rack)

    # PODS BE => /20
    subnetteste = subnetsRackBEipv4[rack]

    #    ::::::::::::::::::::::::::::::::::: FRONTEND
    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::
    # Sumário do rack => 172.20.0.0/21
    subnetsRackFEipv4[rack] = splitnetworkbyrack(CIDRFEipv4[0], 21, rack)
    subnetsRackFEipv6[rack] = splitnetworkbyrack(CIDRFEipv6[0], 57, rack)

    #          ::::::: SUBNETING EACH RACK NETWORK:::::::
    # PODS FE => 128 redes /28 ; 128 redes /64
    redesPODSBEipv4[rack] = list(subnetsRackFEipv4[rack].subnet(28))
    redesPODSBEipv6[rack] = list(subnetsRackFEipv6[rack].subnet(64))

    try:
        variablestochangespine1['ASSPINE'] = get_variable('base_as_spn01')
        variablestochangespine2['ASSPINE'] = get_variable('base_as_spn02')
        variablestochangespine3['ASSPINE'] = get_variable('base_as_spn03')
        variablestochangespine4['ASSPINE'] = get_variable('base_as_spn04')
        variablestochangeleaf1['ASSPINE1'] = get_variable('base_as_spn01')
        variablestochangeleaf1['ASSPINE2'] = get_variable('base_as_spn02')
        variablestochangeleaf1[
            'KICKSTART_SO_LF'] = get_variable('kickstart_so_lf')
        variablestochangeleaf1['IMAGE_SO_LF'] = get_variable('image_so_lf')
        variablestochangeleaf2[
            'KICKSTART_SO_LF'] = get_variable('kickstart_so_lf')
        variablestochangeleaf2['IMAGE_SO_LF'] = get_variable('image_so_lf')
        variablestochangeleaf2['ASSPINE1'] = get_variable('base_as_spn03')
        variablestochangeleaf2['ASSPINE2'] = get_variable('base_as_spn04')
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável ASSPINE<1,2,3,4> ou KICKSTART_SO_LF ou IMAGE_SO_LF.')

    try:
        ID_VLT_LF1 = get_variable('id_vlt_lf1')
        ID_VLT_LF2 = get_variable('id_vlt_lf2')
        PRIORITY_VLT_LF1 = get_variable('priority_vlt_lf1')
        PRIORITY_VLT_LF2 = get_variable('priority_vlt_lf2')
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando as variáveis ID_VLT_LF<1,2> ou PRIORITY_VLT_LF<1,2>')

    variablestochangespine1['IPSPINEIPV4'] = str(IPSPINEipv4[rack][0])
    variablestochangespine1['IPSPINEIPV6'] = str(IPSPINEipv6[rack][0])
    variablestochangespine1['VLANBELEAF'] = str(VLANBELEAF[rack][0])
    variablestochangespine1['VLANFELEAF'] = str(VLANFELEAF[rack][0])
    variablestochangespine1['VLANBORDALEAF'] = str(VLANBORDALEAF[rack][0])
    variablestochangespine1['VLANBORDACACHOSLEAF'] = str(
        VLANBORDACACHOSLEAF[rack][0])
    variablestochangespine1['ASLEAF'] = str(ASLEAF[rack][0])
    variablestochangespine1['IPNEIGHLEAFIPV4'] = str(IPLEAFipv4[rack][0])
    variablestochangespine1['IPNEIGHLEAFIPV6'] = str(IPLEAFipv6[rack][0])
    variablestochangespine1['INTERFACE'] = INTERFACE_SP1
    variablestochangespine1['LEAFNAME'] = HOSTNAME_LF1
    variablestochangespine1['INT_LF_UPLINK'] = int_lf1_sp1
    #
    #
    variablestochangespine2['IPSPINEIPV4'] = str(IPSPINEipv4[rack][1])
    variablestochangespine2['IPSPINEIPV6'] = str(IPSPINEipv6[rack][1])
    variablestochangespine2['VLANBELEAF'] = str(VLANBELEAF[rack][1])
    variablestochangespine2['VLANFELEAF'] = str(VLANFELEAF[rack][1])
    variablestochangespine2['VLANBORDALEAF'] = str(VLANBORDALEAF[rack][1])
    variablestochangespine2['VLANBORDACACHOSLEAF'] = str(
        VLANBORDACACHOSLEAF[rack][1])
    variablestochangespine2['ASLEAF'] = str(ASLEAF[rack][0])
    variablestochangespine2['IPNEIGHLEAFIPV4'] = str(IPLEAFipv4[rack][1])
    variablestochangespine2['IPNEIGHLEAFIPV6'] = str(IPLEAFipv6[rack][1])
    variablestochangespine2['INTERFACE'] = INTERFACE_SP2
    variablestochangespine2['LEAFNAME'] = HOSTNAME_LF1
    variablestochangespine2['INT_LF_UPLINK'] = int_lf1_sp2
    #
    #
    variablestochangespine3['IPSPINEIPV4'] = str(IPSPINEipv4[rack][2])
    variablestochangespine3['IPSPINEIPV6'] = str(IPSPINEipv6[rack][2])
    variablestochangespine3['VLANBELEAF'] = str(VLANBELEAF[rack][2])
    variablestochangespine3['VLANFELEAF'] = str(VLANFELEAF[rack][2])
    variablestochangespine3['VLANBORDALEAF'] = str(VLANBORDALEAF[rack][2])
    variablestochangespine3['VLANBORDACACHOSLEAF'] = str(
        VLANBORDACACHOSLEAF[rack][2])
    variablestochangespine3['ASLEAF'] = str(ASLEAF[rack][0])
    variablestochangespine3['IPNEIGHLEAFIPV4'] = str(IPLEAFipv4[rack][2])
    variablestochangespine3['IPNEIGHLEAFIPV6'] = str(IPLEAFipv6[rack][2])
    variablestochangespine3['INTERFACE'] = INTERFACE_SP3
    variablestochangespine3['LEAFNAME'] = HOSTNAME_LF2
    variablestochangespine3['INT_LF_UPLINK'] = int_lf2_sp3
    #
    #
    variablestochangespine4['IPSPINEIPV4'] = str(IPSPINEipv4[rack][3])
    variablestochangespine4['IPSPINEIPV6'] = str(IPSPINEipv6[rack][3])
    variablestochangespine4['VLANBELEAF'] = str(VLANBELEAF[rack][3])
    variablestochangespine4['VLANFELEAF'] = str(VLANFELEAF[rack][3])
    variablestochangespine4['VLANBORDALEAF'] = str(VLANBORDALEAF[rack][3])
    variablestochangespine4['VLANBORDACACHOSLEAF'] = str(
        VLANBORDACACHOSLEAF[rack][3])
    variablestochangespine4['ASLEAF'] = str(ASLEAF[rack][0])
    variablestochangespine4['IPNEIGHLEAFIPV4'] = str(IPLEAFipv4[rack][3])
    variablestochangespine4['IPNEIGHLEAFIPV6'] = str(IPLEAFipv6[rack][3])
    variablestochangespine4['INTERFACE'] = INTERFACE_SP4
    variablestochangespine4['LEAFNAME'] = HOSTNAME_LF2
    variablestochangespine4['INT_LF_UPLINK'] = int_lf2_sp4
    #
    #
    variablestochangeleaf1['IPLEAFSP1IPV4'] = str(IPLEAFipv4[rack][0])
    variablestochangeleaf1['IPLEAFSP2IPV4'] = str(IPLEAFipv4[rack][1])
    variablestochangeleaf1['IPIBGPIPV4'] = str(IPSIBGPipv4[rack][0])
    variablestochangeleaf1['IPLEAFSP1IPV6'] = str(IPLEAFipv6[rack][0])
    variablestochangeleaf1['IPLEAFSP2IPV6'] = str(IPLEAFipv6[rack][1])
    variablestochangeleaf1['IPIBGPIPV6'] = str(IPSIBGPipv6[rack][0])
    variablestochangeleaf1['VLANBELEAFSP1'] = str(VLANBELEAF[rack][0])
    variablestochangeleaf1['VLANBELEAFSP2'] = str(VLANBELEAF[rack][1])
    variablestochangeleaf1['VLANFELEAFSP1'] = str(VLANFELEAF[rack][0])
    variablestochangeleaf1['VLANFELEAFSP2'] = str(VLANFELEAF[rack][1])
    variablestochangeleaf1['VLANBORDALEAFSP1'] = str(VLANBORDALEAF[rack][0])
    variablestochangeleaf1['VLANBORDALEAFSP2'] = str(VLANBORDALEAF[rack][1])
    variablestochangeleaf1['VLANBORDACACHOSLEAFSP1'] = str(
        VLANBORDACACHOSLEAF[rack][0])
    variablestochangeleaf1['VLANBORDACACHOSLEAFSP2'] = str(
        VLANBORDACACHOSLEAF[rack][1])
    variablestochangeleaf1['ASLEAF'] = str(ASLEAF[rack][0])
    variablestochangeleaf1['IPNEIGHSPINE1IPV4'] = str(IPSPINEipv4[rack][0])
    variablestochangeleaf1['IPNEIGHSPINE2IPV4'] = str(IPSPINEipv4[rack][1])
    variablestochangeleaf1['IPNEIGHIBGPIPV4'] = str(IPSIBGPipv4[rack][1])
    variablestochangeleaf1['IPNEIGHSPINE1IPV6'] = str(IPSPINEipv6[rack][0])
    variablestochangeleaf1['IPNEIGHSPINE2IPV6'] = str(IPSPINEipv6[rack][1])
    variablestochangeleaf1['IPNEIGHIBGPIPV6'] = str(IPSIBGPipv6[rack][1])
    variablestochangeleaf1['LF_HOSTNAME'] = HOSTNAME_LF1
    variablestochangeleaf1['NET_HOST_BE_IPV4'] = str(subnetsRackBEipv4[rack])
    variablestochangeleaf1['NET_HOST_FE_IPV4'] = str(subnetsRackFEipv4[rack])
    variablestochangeleaf1['NET_SPINE1_LF_IPV4'] = str(subSPINE1ipv4[rack])
    variablestochangeleaf1['NET_SPINE2_LF_IPV4'] = str(subSPINE2ipv4[rack])
    variablestochangeleaf1['NET_LF_LF_IPV4'] = str(subIBGPToRLxLipv4[rack])
    variablestochangeleaf1['NET_HOST_BE_IPV6'] = str(subnetsRackBEipv6[rack])
    variablestochangeleaf1['NET_HOST_FE_IPV6'] = str(subnetsRackFEipv6[rack])
    variablestochangeleaf1['NET_SPINE1_LF_IPV6'] = str(subSPINE1ipv6[rack])
    variablestochangeleaf1['NET_SPINE2_LF_IPV6'] = str(subSPINE2ipv6[rack])
    variablestochangeleaf1['NET_LF_LF_IPV6'] = str(subIBGPToRLxLipv6[rack])
    variablestochangeleaf1['ID_LEAF'] = '1'
    variablestochangeleaf1['OWN_IP_MGMT'] = IP_GERENCIA_LF1
    variablestochangeleaf1['LFNEIGH_IP_MGMT'] = IP_GERENCIA_LF2
    variablestochangeleaf1['LFNEIGH_HOSTNAME'] = HOSTNAME_LF2
    variablestochangeleaf1['SP1_HOSTNAME'] = HOSTNAME_SP1
    variablestochangeleaf1['SP2_HOSTNAME'] = HOSTNAME_SP2
    variablestochangeleaf1['INTERFACE_SP1'] = INTERFACE_SP1
    variablestochangeleaf1['INTERFACE_SP2'] = INTERFACE_SP2
    variablestochangeleaf1['HOSTNAME_OOB'] = HOSTNAME_OOB
    variablestochangeleaf1['INTERFACE_OOB'] = INTERFACE_OOB_LF1
    variablestochangeleaf1['ID_VLT'] = ID_VLT_LF1
    variablestochangeleaf1['PRIORITY_VLT'] = PRIORITY_VLT_LF1
    #
    #
    variablestochangeleaf2['IPLEAFSP1IPV4'] = str(IPLEAFipv4[rack][2])
    variablestochangeleaf2['IPLEAFSP2IPV4'] = str(IPLEAFipv4[rack][3])
    variablestochangeleaf2['IPIBGPIPV4'] = str(IPSIBGPipv4[rack][1])
    variablestochangeleaf2['IPLEAFSP1IPV6'] = str(IPLEAFipv6[rack][2])
    variablestochangeleaf2['IPLEAFSP2IPV6'] = str(IPLEAFipv6[rack][3])
    variablestochangeleaf2['IPIBGPIPV6'] = str(IPSIBGPipv6[rack][1])
    variablestochangeleaf2['VLANBELEAFSP1'] = str(VLANBELEAF[rack][2])
    variablestochangeleaf2['VLANBELEAFSP2'] = str(VLANBELEAF[rack][3])
    variablestochangeleaf2['VLANFELEAFSP1'] = str(VLANFELEAF[rack][2])
    variablestochangeleaf2['VLANFELEAFSP2'] = str(VLANFELEAF[rack][3])
    variablestochangeleaf2['VLANBORDALEAFSP1'] = str(VLANBORDALEAF[rack][2])
    variablestochangeleaf2['VLANBORDALEAFSP2'] = str(VLANBORDALEAF[rack][3])
    variablestochangeleaf2['VLANBORDACACHOSLEAFSP1'] = str(
        VLANBORDACACHOSLEAF[rack][2])
    variablestochangeleaf2['VLANBORDACACHOSLEAFSP2'] = str(
        VLANBORDACACHOSLEAF[rack][3])
    variablestochangeleaf2['ASLEAF'] = str(ASLEAF[rack][0])
    variablestochangeleaf2['IPNEIGHSPINE1IPV4'] = str(IPSPINEipv4[rack][2])
    variablestochangeleaf2['IPNEIGHSPINE2IPV4'] = str(IPSPINEipv4[rack][3])
    variablestochangeleaf2['IPNEIGHIBGPIPV4'] = str(IPSIBGPipv4[rack][0])
    variablestochangeleaf2['IPNEIGHSPINE1IPV6'] = str(IPSPINEipv6[rack][2])
    variablestochangeleaf2['IPNEIGHSPINE2IPV6'] = str(IPSPINEipv6[rack][3])
    variablestochangeleaf2['IPNEIGHIBGPIPV6'] = str(IPSIBGPipv6[rack][0])
    variablestochangeleaf2['LF_HOSTNAME'] = HOSTNAME_LF2
    variablestochangeleaf2['NET_HOST_BE_IPV4'] = str(subnetsRackBEipv4[rack])
    variablestochangeleaf2['NET_HOST_FE_IPV4'] = str(subnetsRackFEipv4[rack])
    variablestochangeleaf2['NET_SPINE1_LF_IPV4'] = str(subSPINE3ipv4[rack])
    variablestochangeleaf2['NET_SPINE2_LF_IPV4'] = str(subSPINE4ipv4[rack])
    variablestochangeleaf2['NET_LF_LF_IPV4'] = str(subIBGPToRLxLipv4[rack])
    variablestochangeleaf2['NET_HOST_BE_IPV6'] = str(subnetsRackBEipv6[rack])
    variablestochangeleaf2['NET_HOST_FE_IPV6'] = str(subnetsRackFEipv6[rack])
    variablestochangeleaf2['NET_SPINE1_LF_IPV6'] = str(subSPINE3ipv6[rack])
    variablestochangeleaf2['NET_SPINE2_LF_IPV6'] = str(subSPINE4ipv6[rack])
    variablestochangeleaf2['NET_LF_LF_IPV6'] = str(subIBGPToRLxLipv6[rack])
    variablestochangeleaf2['ID_LEAF'] = '2'
    variablestochangeleaf2['OWN_IP_MGMT'] = IP_GERENCIA_LF2
    variablestochangeleaf2['LFNEIGH_IP_MGMT'] = IP_GERENCIA_LF1
    variablestochangeleaf2['LFNEIGH_HOSTNAME'] = HOSTNAME_LF1
    variablestochangeleaf2['SP1_HOSTNAME'] = HOSTNAME_SP3
    variablestochangeleaf2['SP2_HOSTNAME'] = HOSTNAME_SP4
    variablestochangeleaf2['INTERFACE_SP1'] = INTERFACE_SP3
    variablestochangeleaf2['INTERFACE_SP2'] = INTERFACE_SP4
    variablestochangeleaf2['HOSTNAME_OOB'] = HOSTNAME_OOB
    variablestochangeleaf2['INTERFACE_OOB'] = INTERFACE_OOB_LF2
    variablestochangeleaf2['ID_VLT'] = ID_VLT_LF2
    variablestochangeleaf2['PRIORITY_VLT'] = PRIORITY_VLT_LF2

    try:
        fileoutspine1 = get_variable(
            'path_to_add_config') + HOSTNAME_SP1 + '-ADD-' + HOSTNAME_RACK[2] + '.cfg'
        fileoutspine2 = get_variable(
            'path_to_add_config') + HOSTNAME_SP2 + '-ADD-' + HOSTNAME_RACK[2] + '.cfg'
        fileoutspine3 = get_variable(
            'path_to_add_config') + HOSTNAME_SP3 + '-ADD-' + HOSTNAME_RACK[2] + '.cfg'
        fileoutspine4 = get_variable(
            'path_to_add_config') + HOSTNAME_SP4 + '-ADD-' + HOSTNAME_RACK[2] + '.cfg'
        fileoutleaf1 = get_variable('path_to_config') + HOSTNAME_LF1 + '.cfg'
        fileoutleaf2 = get_variable('path_to_config') + HOSTNAME_LF2 + '.cfg'
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável PATH_TO_CONFIG ou PATH_TO_ADD_CONFIG.')

    replace(fileinspine1, fileoutspine1, variablestochangespine1)
    replace(fileinspine2, fileoutspine2, variablestochangespine2)
    replace(fileinspine3, fileoutspine3, variablestochangespine3)
    replace(fileinspine4, fileoutspine4, variablestochangespine4)
    replace(fileinleaf1, fileoutleaf1, variablestochangeleaf1)
    replace(fileinleaf2, fileoutleaf2, variablestochangeleaf2)

    return True
