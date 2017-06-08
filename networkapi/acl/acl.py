# -*- coding: utf-8 -*-
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
import logging
import os
from time import strftime

from networkapi.acl.Enum import Enum
from networkapi.acl.Enum import NETWORK_TYPES
from networkapi.acl.file import File
from networkapi.acl.file import FileError
from networkapi.cvs import Cvs
from networkapi.cvs import CVSCommandError
from networkapi.settings import PATH_ACL

logger = logging.getLogger(__name__)

EXTENTION_FILE = '.txt'

PATH_ACL_TEMPLATES = '/templates/'

PATH_TYPES = Enum(['ACL', 'TEMPLATE'])

DIVISON_DC = Enum(['FE', 'BE', 'DEV_QA_FE', 'DEV_QA',
                   'BORDA', 'BE_POP_SP', 'FE_POP_SP', 'BORDA_POP_SP'])

ENVIRONMENT_LOGICAL = Enum(
    ['APLICATIVOS', 'PORTAL', 'HOMOLOGACAO', 'PRODUCAO', 'BORDA'])

TEMPLATES = Enum(
    ['BE', 'BEHO', 'FE_APLICATIVOS', 'FE_DEV_QA', 'FE_PORTAL', 'FE_STAGING'])

PREFIX_TEMPLATES = 'ACL_PADRAO_'


def hexa(x):
    return hex(x)[2:]


def mkdir_divison_dc(divison_dc, user, acl_path=None):
    """Creates the directory division dc in cvs

    @param divison_dc: division dc to be created
    @param user: user

    @raise CVSCommandError: Failed to execute
    """
    try:

        divison_dc = str(divison_dc).upper()

        os.chdir(PATH_ACL)

        if divison_dc == DIVISON_DC.BORDA:
            divison_dc = 'Borda'

        directory = divison_dc

        if acl_path:
            directory = acl_path

        Cvs.synchronization()

        # Set path - Ipv4 - Ipv6
        list_path = []
        list_path.append('%s%s/' % (PATH_ACL, 'v4'))
        list_path.append('%s%s/' % (PATH_ACL, 'v6'))

        for path in list_path:

            os.chdir(path)

            folders = directory.split('/')

            for folder in folders:
                if folder:
                    if not os.path.exists(folder):
                        os.mkdir(folder)
                        Cvs.add(folder)
                        Cvs.commit(
                            folder, 'Criação do diretório de divisão dc %s/%s pelo usuário: %s' % (path, folder, user.user))
                        logger.info(
                            '%s criou no CVS o diretório: %s/%s' % (user.user, path, folder))
                        Cvs.synchronization()

                    path = '%s/%s' % (path, folder)
                    os.chdir(path)

    except Exception, e:
        logger.error('Erro quando o usuário %s tentou criar o diretório: %s no Cvs' % (
            user.user, dir))
        logger.error(e)
        raise CVSCommandError(e)


def script_template(environment_logical, divison_dc, group_l3, template_name):
    """Validates that can use a script to create the ACL.

    @param environment_logical: environment logical
    @param divison_dc: divison dc
    @param group_l3: group l3
    @param template_name: Template name
    """
    script = False

    if template_name:
        script = True
    else:
        if divison_dc == DIVISON_DC.FE:

            if environment_logical == ENVIRONMENT_LOGICAL.APLICATIVOS or environment_logical == ENVIRONMENT_LOGICAL.PORTAL or environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

                if group_l3 == 'CORE/DENSIDADE':

                    script = True

        elif divison_dc == DIVISON_DC.BE:

            if environment_logical == ENVIRONMENT_LOGICAL.PRODUCAO or environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

                if group_l3 == 'CORE/DENSIDADE':

                    script = True

    return script


def chdir(type_path, network, path=None):
    """Change the current working directory to path.

    @param type_path: type path
    @param network: v4 or v6
    @param path: path

    @raise CVSCommandError:  Failed to execute command
    """
    try:

        if type_path == PATH_TYPES.ACL:
            path = '%s%s/%s' % (PATH_ACL, network, path)

        elif type_path == PATH_TYPES.TEMPLATE:
            path = '%s%s/%s' % (PATH_ACL, network, PATH_ACL_TEMPLATES)

        os.chdir(path)

    except Exception, e:
        logger.error(e)
        raise Exception(e)


def check_name_file(acl_file_name, extention=True):
    """Validates the filename do acl has point and space and adds extension

    @param acl_file_name: name is validaded
    @param extention: True case add extention
    """
    acl = ''
    for caracter in acl_file_name:
        if ((caracter == '.') or (caracter == ' ')):
            pass
        else:
            acl += caracter

    if extention is True:
        acl = acl + EXTENTION_FILE

    return acl


def check_name_file_bkp(acl_file_name):
    """Validates the filename do acl has point and space and adds extension and suffix bkp

    @param acl_file_name: name is validaded
    """
    acl = ''
    for caracter in acl_file_name:
        if ((caracter == '.') or (caracter == ' ')):
            pass
        else:
            acl += caracter

    return acl + '_bkp_' + strftime('%Y%m%d%H%M%S') + EXTENTION_FILE


def path_acl(environment_logical, divison_dc, acl_path=None):
    """Creates the path depending on the parameters of environment

    @param environment_logical: environment logical
    @param divison_dc: divison dc
    """
    path = divison_dc

    if environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

        if divison_dc == DIVISON_DC.FE:
            path = DIVISON_DC.DEV_QA_FE

        else:
            path = DIVISON_DC.DEV_QA

    elif environment_logical == ENVIRONMENT_LOGICAL.PRODUCAO:

        if divison_dc == replace_to_correct(DIVISON_DC.BE_POP_SP):
            path = replace_to_correct(DIVISON_DC.BE_POP_SP)

        elif divison_dc == replace_to_correct(DIVISON_DC.FE_POP_SP):
            path = replace_to_correct(DIVISON_DC.FE_POP_SP)

    elif environment_logical == ENVIRONMENT_LOGICAL.BORDA:

        if divison_dc == replace_to_correct(DIVISON_DC.BORDA_POP_SP):
            path = replace_to_correct(DIVISON_DC.BORDA_POP_SP)
        else:
            path = divison_dc

    if path == DIVISON_DC.BORDA:
        path = 'Borda'

    if acl_path:
        path = acl_path

    return path


def replace_to_correct(value):
    return value.replace('_', '-')


def createAclCvs(acl_name, environment, network, user):
    """Create the file acl.

    @param acl_name: acl name
    @param environment: Environment
    @param network: v4 or v6
    @param user: user

    @raise CVSCommandError:  Failed to execute command
    """
    try:

        acl = check_name_file(acl_name)

        path = path_acl(environment['nome_ambiente_logico'], environment['nome_divisao'],
                        environment['acl_path'])

        mkdir_divison_dc(
            environment['nome_divisao'], user, environment['acl_path'])

        chdir(PATH_TYPES.ACL, network, path)

        Cvs.synchronization()

        File.create(acl)

        Cvs.add(acl)

        Cvs.commit(acl, 'Criação do Arquivo %s pelo usuário: %s' %
                   (acl, user.user))

        logger.info('%s criou no CVS o arquivo: %s' %
                    (user.user, (path + acl)))

    except (CVSCommandError, FileError, Exception), e:
        logger.error('Erro quando o usuário %s tentou criar o arquivo: %s no Cvs' % (
            user.user, (path + acl)))
        logger.error(e)
        raise CVSCommandError(e)


def scriptAclCvs(acl_name, vlan, environment, network, user, template_name):
    """Generates the acl based on a template

    @param acl_name: acl name
    @param vlan: Vvlan
    @param environment: Environment
    @param network: v4 or v6
    @param user: user
    @param temple_name: Template Name

    @raise CVSCommandError:  Failed to execute command
    """
    try:

        acl = check_name_file(acl_name)
        acl_name = check_name_file(acl_name, extention=False)

        if template_name:

            path_env = environment['acl_path'] if environment[
                'acl_path'] else environment['nome_divisao']

            chdir(PATH_TYPES.ACL, network, path_env)

            Cvs.synchronization()

            arquivo = open('./%s' % acl, 'w')

            chdir(PATH_TYPES.TEMPLATE, network)

            Cvs.synchronization()

            file_template = open(template_name, 'r')

            content_template = file_template.read()

            nova_acl = replace_template(
                acl_name, vlan, content_template, network)

            chdir(PATH_TYPES.ACL, network, path_env)

            arquivo.write('%s' % nova_acl)
            arquivo.close()
            file_template.close()

            Cvs.commit(acl, '%s gerou Script para a acl %s' % (user.user, acl))

            logger.info('%s alterou no CVS o arquivo: %s' % (user.user, acl))

        else:
            if ((environment['nome_divisao'] == 'BE') and (environment['nome_ambiente_logico'] == 'PRODUCAO') and (environment['nome_grupo_l3'] == 'CORE/DENSIDADE')):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.BE

                chdir(PATH_TYPES.ACL, network, path_env)

                Cvs.synchronization()

                arquivo = open('./%s' % acl, 'w')

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.BE + EXTENTION_FILE, 'r')

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write('%s' % nova_acl)
                arquivo.close()
                file_template.close()

                Cvs.commit(acl, '%s gerou Script para a acl %s' %
                           (user.user, acl))

                logger.info('%s alterou no CVS o arquivo: %s' %
                            (user.user, acl))

            if ((environment['nome_divisao'] == DIVISON_DC.FE) and (environment['nome_ambiente_logico'] == ENVIRONMENT_LOGICAL.HOMOLOGACAO) and (environment['nome_grupo_l3'] == 'CORE/DENSIDADE')):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.DEV_QA_FE

                chdir(PATH_TYPES.ACL, network, path_env)

                Cvs.synchronization()

                arquivo = open('./%s' % acl, 'w')

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.FE_DEV_QA + EXTENTION_FILE, 'r')

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write('%s' % nova_acl)
                arquivo.close()
                file_template.close()

                Cvs.commit(acl, '%s gerou Script para a acl %s' %
                           (user.user, acl))

                logger.info('%s alterou no CVS o arquivo: %s' %
                            (user.user, acl))

            if ((environment['nome_divisao'] == DIVISON_DC.FE) and (environment['nome_ambiente_logico'] == ENVIRONMENT_LOGICAL.PORTAL) and (environment['nome_grupo_l3'] == 'CORE/DENSIDADE')):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.FE

                chdir(PATH_TYPES.ACL, network, path_env)

                Cvs.synchronization()

                arquivo = open('./%s' % acl, 'w')

                chdir(PATH_TYPES.TEMPLATE, network)

                if 'staging' in acl.lower():
                    file_template = open(
                        PREFIX_TEMPLATES + TEMPLATES.FE_STAGING + EXTENTION_FILE, 'r')
                else:
                    file_template = open(
                        PREFIX_TEMPLATES + TEMPLATES.FE_PORTAL + EXTENTION_FILE, 'r')

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write('%s' % nova_acl)
                arquivo.close()
                file_template.close()

                Cvs.commit(acl, '%s gerou Script para a acl %s' %
                           (user.user, acl))

                logger.info('%s alterou no CVS o arquivo: %s' %
                            (user.user, acl))

            if ((environment['nome_divisao'] == DIVISON_DC.FE) and (environment['nome_ambiente_logico'] == ENVIRONMENT_LOGICAL.APLICATIVOS) and (environment['nome_grupo_l3'] == 'CORE/DENSIDADE')):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.FE

                chdir(PATH_TYPES.ACL, network, path_env)

                Cvs.synchronization()

                arquivo = open('./%s' % acl, 'w')

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.FE_APLICATIVOS + EXTENTION_FILE, 'r')

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write('%s' % nova_acl)
                arquivo.close()
                file_template.close()

                Cvs.commit(acl, '%s gerou Script para a acl %s' %
                           (user.user, acl))

                logger.info('%s alterou no CVS o arquivo: %s' %
                            (user.user, acl))

            if ((environment['nome_divisao'] == DIVISON_DC.BE) and (environment['nome_ambiente_logico'] == ENVIRONMENT_LOGICAL.HOMOLOGACAO) and (environment['nome_grupo_l3'] == 'CORE/DENSIDADE')):

                path_env = environment['acl_path'] if environment[
                    'acl_path'] else DIVISON_DC.DEV_QA

                chdir(PATH_TYPES.ACL, network, path_env)

                Cvs.synchronization()

                arquivo = open('./%s' % acl, 'w')

                chdir(PATH_TYPES.TEMPLATE, network)

                file_template = open(
                    PREFIX_TEMPLATES + TEMPLATES.BEHO + EXTENTION_FILE, 'r')

                content_template = file_template.read()

                nova_acl = replace_template(
                    acl_name, vlan, content_template, network)

                chdir(PATH_TYPES.ACL, network, path_env)

                arquivo.write('%s' % nova_acl)
                arquivo.close()
                file_template.close()

                Cvs.commit(acl, '%s gerou Script para a acl %s' %
                           (user.user, acl))

                logger.info('%s alterou no CVS o arquivo: %s' %
                            (user.user, acl))

    except (CVSCommandError, FileError, Exception), e:
        logger.error(
            'Erro quando o usuário %s tentou gerar o arquivo: %s no Cvs' % (user.user, acl))
        logger.error(e)
        raise CVSCommandError(e)


def checkAclCvs(acl_file_name, environment, network, user):
    """Validates if the file is created acl.

    @param acl_file_name: acl name
    @param environment: Environment
    @param network: v4 or v6
    @param user: user

    @raise CVSCommandError:  Failed to execute command

    @return: True case created
    """
    try:

        acl = check_name_file(acl_file_name)

        path = path_acl(environment['nome_ambiente_logico'], environment['nome_divisao'],
                        environment['acl_path'])

        mkdir_divison_dc(
            environment['nome_divisao'], user, environment['acl_path'])

        chdir(PATH_TYPES.ACL, network, path)

        Cvs.synchronization()

        File.read(acl)

        return True

    except FileError, e:
        return False

    except (CVSCommandError, Exception), e:
        logger.error(
            'Erro quando o usuário %s tentou sincronizar no Cvs' % (user.user))
        logger.error(e)
        raise CVSCommandError(e)


def replace_template(acl_name, vlan, content_template, network):

    network, block, wmasc, special_1, special_2 = parse_template(vlan, network)

    acl = content_template.replace('%ACL', acl_name)
    acl = acl.replace('%NUMERO', '%s' % (vlan['num_vlan']))

    if network is not None and block is not None and wmasc is not None and special_1 is not None and special_2 is not None:

        acl = acl.replace('%REDE', network)
        acl = acl.replace('%BLOCO', block)
        acl = acl.replace('%WMASC', wmasc)
        acl = acl.replace('%ESPECIAL1', special_1)
        acl = acl.replace('%ESPECIAL2', special_2)

    return acl


def parse_template(vlan, network):

    try:

        net = None
        block = None
        wmasc = None
        special_1 = None
        special_2 = None

        if vlan['redeipv4'] is not None and vlan['redeipv4'] != '' and vlan['redeipv4'] and network == NETWORK_TYPES.v4:
            network = vlan['redeipv4'][0]

            net = '%s.%s.%s.%s' % (
                network['oct1'], network['oct2'], network['oct3'], network['oct4'])

            wmasc_1 = int(network['mask_oct1']) ^ 255
            wmasc_2 = int(network['mask_oct2']) ^ 255
            wmasc_3 = int(network['mask_oct3']) ^ 255
            wmasc_4 = int(network['mask_oct4']) ^ 255

            wmasc = '%s.%s.%s.%s' % (wmasc_1, wmasc_2, wmasc_3, wmasc_4)

            ipEsp_1 = int(network['oct1']) | wmasc_1
            ipEsp_2 = int(network['oct2']) | wmasc_2
            ipEsp_3 = int(network['oct3']) | wmasc_3
            ipEsp_4 = int(network['oct4']) | wmasc_4

            special_1 = '%s.%s.%s.%s' % (
                ipEsp_1, ipEsp_2, ipEsp_3, (ipEsp_4 - 1))
            special_2 = '%s.%s.%s.%s' % (
                ipEsp_1, ipEsp_2, ipEsp_3, (ipEsp_4 - 2))

            block = '%s' % (network['block'])

        elif vlan['redeipv6'] is not None and vlan['redeipv6'] != '' and vlan['redeipv6'] and network == NETWORK_TYPES.v6:
            network = vlan['redeipv6'][0]

            net = '%s:%s:%s:%s:%s:%s:%s:%s' % (network['block1'], network['block2'], network['block3'], network[
                                               'block4'], network['block5'], network['block6'], network['block7'], network['block8'])

            wmasc_1 = mask_ipv6(network['mask1'])
            wmasc_2 = mask_ipv6(network['mask2'])
            wmasc_3 = mask_ipv6(network['mask3'])
            wmasc_4 = mask_ipv6(network['mask4'])
            wmasc_5 = mask_ipv6(network['mask5'])
            wmasc_6 = mask_ipv6(network['mask6'])
            wmasc_7 = mask_ipv6(network['mask7'])
            wmasc_8 = mask_ipv6(network['mask8'])

            wmasc = '%s:%s:%s:%s:%s:%s:%s:%s' % (
                wmasc_1, wmasc_2, wmasc_3, wmasc_4, wmasc_5, wmasc_6, wmasc_7, wmasc_8)

            ipEsp_1 = block_ipv6(network['block1'], wmasc_1)
            ipEsp_2 = block_ipv6(network['block2'], wmasc_2)
            ipEsp_3 = block_ipv6(network['block3'], wmasc_3)
            ipEsp_4 = block_ipv6(network['block4'], wmasc_4)
            ipEsp_5 = block_ipv6(network['block5'], wmasc_5)
            ipEsp_6 = block_ipv6(network['block6'], wmasc_6)
            ipEsp_7 = block_ipv6(network['block7'], wmasc_7)
            ipEsp_8 = block_ipv6(network['block8'], wmasc_8)

            sp1 = hexa(int(ipEsp_8, 16) - 1)
            sp2 = hexa(int(ipEsp_8, 16) - 2)

            special_1 = '%s:%s:%s:%s:%s:%s:%s:%s' % (
                ipEsp_1, ipEsp_2, ipEsp_3, ipEsp_4, ipEsp_5, ipEsp_6, ipEsp_7, sp1)
            special_2 = '%s:%s:%s:%s:%s:%s:%s:%s' % (
                ipEsp_1, ipEsp_2, ipEsp_3, ipEsp_4, ipEsp_5, ipEsp_6, ipEsp_7, sp2)

            block = '%s' % (network['block'])

        return net, block, wmasc, special_1, special_2

    except Exception, e:
        logger.error(
            'Erro quando realizava parse das variaveis da rede para o replace no template.')
        raise Exception(e)


def mask_ipv6(param):
    param = hexa(int(param, 16) ^ int('ffff', 16))
    if param == '0':
        param = '0000'

    return param


def block_ipv6(param, wmasc):
    param = hexa(int(param, 16) | int(wmasc, 16))
    if param == '0':
        param = '0000'

    return param


def acl_key(network):
    """Convert the key of value acl.

    @param network: v4 or v6.

    @return value of key.

    @raise ValueError: Parameter null or blank
    """
    if network is None:
        raise ValueError('Parameter null or blank')

    if network == NETWORK_TYPES.v4:
        return 'acl_file_name'

    else:
        return 'acl_file_name_v6'
