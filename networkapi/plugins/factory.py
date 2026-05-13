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
import re
from networkapi.equipamento.models import Equipamento, EquipamentoAcesso

from networkapi.plugins.SDN.ODL.Generic import ODLPlugin

log = logging.getLogger(__name__)


class PluginFactory(object):

    @classmethod
    def plugin_exists(cls, **kwargs):

        try:
            cls.get_plugin(kwargs)
            return True
        except NotImplementedError:
            return False

    @classmethod
    def get_plugin(cls, **kwargs):
        if 'tipo_acesso' in kwargs and kwargs.get('tipo_acesso') == 'netconf':
            if 'bgp' in kwargs:
                bgp = kwargs.get('bgp')
                if bgp:
                    from .Netconf.BGP.Cli import Generic
                    return Generic

            from .Netconf.plugin import GenericNetconf
            return GenericNetconf
        if 'modelo' in kwargs:
            modelo = kwargs.get('modelo')

            # TODO create a table in networkapi to specify wich plugin
            # to load for each equipment configuration
            if re.search('NEXUS', modelo.upper(), re.DOTALL):
                # if 'bgp' in kwargs:
                #     from .BGP.NXAPI.Generic import NxApiPlugin
                #     return NxApiPlugin
                # else:
                #     from .Cisco.NXOS.plugin import NXOS
                #     return NXOS
                from .Cisco.NXOS.plugin import NXOS
                return NXOS
            if re.search('WS-|C65', modelo.upper(), re.DOTALL):
                from .Cisco.IOS.plugin import IOS
                return IOS
            if re.search('ACE30', modelo.upper(), re.DOTALL):
                from .Cisco.ACE.plugin import ACE
                return ACE
            if re.search('C9500', modelo.upper(), re.DOTALL):
                from .Cisco.IOS.plugin import IOS
                return IOS

        if 'marca' in kwargs:
            marca = kwargs.get('marca')
            # if re.search('HUAWEI', marca.upper(), re.DOTALL):
            #     from .Netconf.plugin import GenericNetconf
            #     return GenericNetconf
            if re.search('F5', marca.upper(), re.DOTALL):
                from .F5.Generic import Generic
                return Generic
            if re.search('BROCADE', marca.upper(), re.DOTALL) \
               or re.search('FOUNDRY', marca.upper(), re.DOTALL):
                from .Brocade.Generic import Generic
                return Generic
            if re.search('DELL', marca.upper(), re.DOTALL):
                from .Dell.FTOS.plugin import FTOS
                return FTOS
            if re.search('OPENDAYLIGHT', marca.upper(), re.DOTALL):
                return ODLPlugin
            if re.search('FUSIS', marca.upper(), re.DOTALL):
                from .SDN.FUSIS.Generic import Generic
                return Generic
            if re.search('HP', marca.upper(), re.DOTALL):
                from .HP.plugin import HPE
                return HPE
            if re.search('MELLANOX', marca.upper(), re.DOTALL):
                if re.search('SH2200', modelo.upper(), re.DOTALL):
                    from .Mellanox.SH2200.plugin import SH2200
                    return SH2200
            if re.search('CUMULUS', marca.upper(), re.DOTALL):
                if re.search('CUMULUS', modelo.upper(), re.DOTALL):
                    from .Cumulus.plugin import Cumulus
                    return Cumulus
            if re.search('JUNIPER', marca.upper(), re.DOTALL):
                if re.search('QFX', modelo.upper(), re.DOTALL):
                    if 'bgp' in kwargs:
                        bgp = kwargs.get('bgp')
                        if bgp:
                            from .Juniper.JUNOS.BGP.Cli import Generic
                            return Generic
                    from .Juniper.JUNOS.plugin import JUNOS
                    return JUNOS
        raise NotImplementedError('plugin not implemented')

    @classmethod
    def factory(cls, equipment, **kwargs):

        marca = equipment.modelo.marca.nome
        modelo = equipment.modelo.nome

        # Check is balanceador
        equipment_type = ''
        if equipment.tipo_equipamento:
            equipment_type = equipment.tipo_equipamento.tipo_equipamento or ''
        is_load_balancer = 'BALANCEADOR' in equipment_type.upper()

        # Count access number
        access_list = EquipamentoAcesso.search(None, equipment)
        access_count = access_list.count()

        access_type = None
        
        # If unique access, get it
        if access_count == 1:
            access_type = access_list.uniqueResult()
        elif access_count > 1:

            # If more than one access, check if is LB and get ssh access, otherwise get netconf access.
            if is_load_balancer:
                ssh_access = EquipamentoAcesso.search(None, equipment, 'ssh')
                if ssh_access.count() > 0:
                    access_type = ssh_access.uniqueResult()
            else:
                netconf_access = EquipamentoAcesso.search(
                    None, equipment, 'netconf'
                )
                if netconf_access.count() > 0:
                    access_type = netconf_access.uniqueResult()

            # If not LB or not netconf access, get the remaining access
            if access_type is None:
                access_type = access_list.uniqueResult()
        
        log.debug(
            'Equipment %s has %s access and the selected access was %s',
            equipment.id,
            access_count,
            access_type.tipo_acesso.protocolo if access_type else 'None'
        )
        if access_type is None:
            return 'Equipment has no Access.'

        plugin_class = cls.get_plugin(modelo=modelo, marca=marca, tipo_acesso=access_type.tipo_acesso.protocolo, **kwargs)

        if type(plugin_class) == type(ODLPlugin):
            version = 'BERYLLIUM'
            if modelo.upper().find("BORON") > -1:
                version = "BORON"
            if modelo.upper().find("CARBON") > -1:
                version = "CARBON"
            if modelo.upper().find("NITROGEN") > -1:
                version = "NITROGEN"

            env_id = kwargs.get("env_id")
            return plugin_class(
                equipment=equipment,
                environment=env_id,
                version=version
            )

        return plugin_class(equipment=equipment)
