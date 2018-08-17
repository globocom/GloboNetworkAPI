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

from django.forms.models import model_to_dict

from networkapi.interface.models import PortChannel
from networkapi.interface.models import EnvironmentInterface
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.interface.models import InvalidValueError
from networkapi.interface.models import TipoInterface
from networkapi.ambiente.models import Ambiente

from networkapi.api_interface.exceptions import InterfaceException
from networkapi.api_interface.exceptions import InvalidKeyException
from networkapi.api_interface.exceptions import InterfaceTemplateException
from networkapi.api_interface import facade as api_interface_facade

from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util import is_valid_int_greater_zero_param

log = logging.getLogger(__name__)


class ChannelV3(object):
    """ Facade class that implements business rules for interfaces channels """

    def __init__(self, user=None):
        """ Contructor of Port Channels V3 implementation """
        self.user = user
        self.channel = None

    def create(self, data):
        """ Creates a new Port Channel """

        log.info("Create Channel")

        try:
            log.debug(data)
            interfaces = data.get('interfaces')
            nome = data.get('name')
            lacp = data.get('lacp')
            int_type = data.get('int_type')
            vlan_nativa = data.get('vlan')
            envs_vlans = data.get('envs_vlans')

            api_interface_facade.verificar_vlan_nativa(vlan_nativa)

            # Checks if Port Channel name already exists on equipment
            api_interface_facade.check_channel_name_on_equipment(nome, interfaces)

            self.channel = PortChannel()
            self.channel.nome = str(nome)
            self.channel.lacp = convert_string_or_int_to_boolean(lacp)
            self.channel.create()

            ifaces_on_channel = []
            for interface in interfaces:

                iface = Interface.objects.get(id=interface)
                type_obj = TipoInterface.objects.get(tipo=int_type)

                if iface.channel:
                    raise InterfaceError('Interface %s is already a Channel' % iface.interface)

                if iface.equipamento.id not in ifaces_on_channel:
                    ifaces_on_channel.append(int(iface.equipamento.id))

                    if len(ifaces_on_channel) > 2:
                        raise InterfaceError('More than one equipment selected')

                iface.channel = self.channel
                iface.int_type = type_obj
                iface.vlan_nativa = vlan_nativa
                iface.save()

                log.debug("interface updated %s" % iface.id)

                if 'trunk' in int_type.lower():
                    self._create_ifaces_on_trunks(iface, envs_vlans)

        except Exception as err:
            log.error(str(err))
            raise Exception({"error": str(err)})

        return {'channels': self.channel.id}

    def _update_interfaces_from_a_channel(self, iface, vlan_nativa, ifaces_on_channel, int_type):
        log.info("_update_interfaces_from_a_channel")

        if iface.channel:
            raise InterfaceError('Interface %s is already a Channel' % iface.interface)

        if not iface.equipamento.id in ifaces_on_channel:
            ifaces_on_channel.append(int(iface.equipamento.id))

            if len(ifaces_on_channel) > 2:
                raise InterfaceError('More than one equipment selected')

        interface_obj = dict(native_vlan=vlan_nativa,
                             type=int_type,
                             channel=self.channel,
                             interface=iface.interface,
                             equipment=iface.equipamento,
                             description=iface.descricao,
                             protected=iface.protegida,
                             front_interface=iface.ligacao_front,
                             back_interface=iface.ligacao_back)

        iface.update_V3(interface_obj)

    def _create_ifaces_on_trunks(self, sw_router, envs_vlans):

        interface_list = EnvironmentInterface.objects.all().filter(
            interface=sw_router.id)

        for int_env in interface_list:
            int_env.delete()

        if type(envs_vlans) is not list:
            envs_vlans = [envs_vlans]

        for i in envs_vlans:

            environment = Ambiente.get_by_pk(int(i.get('env')))
            env_iface = EnvironmentInterface()
            env_iface.interface = sw_router
            env_iface.ambiente = environment

            range_vlans = i.get('vlans')
            if range_vlans:
                api_interface_facade.verificar_vlan_range(
                    environment, range_vlans)

                env_iface.vlans = range_vlans

            env_iface.create()


    def retrieve(self, channel_name):
        """ Tries to retrieve a Port Channel based on its name """

        channel = {}
        try:
            channel = PortChannel.get_by_name(channel_name)

            # Copied from old implementation. We really need to iterate?
            for ch in channel:
                channel = model_to_dict(ch)

        except InterfaceNotFoundError as err:
            return None
        except:
            channel = model_to_dict(channel)

        # We could do it on the model implementation. But because we need
        # compatibility with older version of the API this verification is
        # made here. Returning None means that no channel were found.
        if len(channel) == 0:
            return None

        return {"channel": channel}

    def update(self, data):

        try:
            id_channel = data.get('id_channel')
            nome = data.get('nome')

            if not is_valid_int_greater_zero_param(nome):
                raise InvalidValueError(
                    None, 'Channel number', 'must be integer.')

            lacp = data.get('lacp')
            int_type = data.get('int_type')
            vlan_nativa = data.get('vlan')
            envs_vlans = data.get('envs')
            ids_interface = data.get('ids_interface')

            if ids_interface is None:
                raise InterfaceError('No interfaces selected')

            if type(ids_interface) == list:
                interfaces_list = ids_interface
            else:
                interfaces_list = str(ids_interface).split('-')

            api_interface_facade.verificar_vlan_nativa(vlan_nativa)

            # verifica se o nome do port channel já existe no equipamento
            self.channel = PortChannel.get_by_pk(int(id_channel))

            if not nome == self.channel.nome:
                api_interface_facade.verificar_nome_channel(
                    nome, interfaces_list)

            # buscar interfaces do channel
            interfaces = Interface.objects.all().filter(channel__id=id_channel)
            ids_list = []
            for i in interfaces:
                ids_list.append(i.id)

            self._dissociate_interfaces_from_channel(ids_list, ids_interface)

            # update channel
            self.channel.nome = str(nome)
            self.channel.lacp = convert_string_or_int_to_boolean(lacp)
            self.channel.save()

            int_type = TipoInterface.get_by_name(str(int_type))

            self._update_interfaces_from_http_put(
                ids_interface, int_type, vlan_nativa, envs_vlans)

        except Exception as err:
            return {"error": str(err)}

        return {"port_channel": self.channel}

    def _dissociate_interfaces_from_channel(self, ids_list, ids_interface):

        ids_list = [int(y) for y in ids_list]

        if type(ids_interface) is list:

            ids_interface = [int(x) for x in ids_interface]
            dissociate = set(ids_list) - set(ids_interface)
            for item in dissociate:
                item = Interface.get_by_pk(int(item))
                item.channel = None
                item.save()
        else:
            if ids_interface is not None:
                ids_interface = int(ids_interface)

                if ids_interface is not None:
                    for item in ids_list:
                        item = Interface.get_by_pk(int(item))
                        item.channel = None
                        item.save()
                else:
                    for item in ids_list:
                        if not item == ids_interface:
                            item = Interface.get_by_pk(int(item))
                            item.channel = None
                            item.save()

    def _update_interfaces_from_http_put(self, ids_interface, int_type,
            vlan_nativa, envs_vlans):

        # update interfaces
        if type(ids_interface) is not list:
            i = ids_interface
            ids_interface = []
            ids_interface.append(i)

        ifaces_on_channel = []
        for iface_id in ids_interface:

            iface = Interface.get_by_pk(int(iface_id))

            self._update_interfaces_from_a_channel(iface, vlan_nativa,
                ifaces_on_channel, int_type)

            interface_sw = Interface.get_by_pk(int(iface))
            interface_server = Interface.get_by_pk(
                interface_sw.ligacao_front.id)

            front = None
            if interface_server.ligacao_front.id is not None:
                front = interface_server.ligacao_front.id

            back = None
            if interface_server.ligacao_back.id is not None:
                back = interface_server.ligacao_back.id

            Interface.update(
                user,
                interface_server.id,
                interface=interface_server.interface,
                protegida=interface_server.protegida,
                descricao=interface_server.descricao,
                ligacao_front_id=front,
                ligacao_back_id=back,
                tipo=int_type,
                vlan_nativa=int(vlan_nativa)
            )


    def delete(self, channel_id):
        """ tries to delete a channel and update equipments interfaces """

        try:
            interface = Interface.get_by_pk(int(channel_id))

            try:
                interface.channel.id
                channel = interface.channel
            except AtributeError:
                channel = interface.ligacao_front.channel

            try:
                interfaces = Interface.objects.all().filter(
                    channel__id=channel.id)
            except Exception as err:
                return {"error": str(err)}


            iface_type = TipoInterface.get_by_name('access')
            equip_dict = self._get_equipment_dict(interfaces)

            self._update_equipments(equip_dict, iface_type, self.user, channel)
            channel.delete(self.user)

            return {"channel": channel.id}

        except (InterfaceException, InvalidKeyException,
                InterfaceTemplateException) as err:
            return {"error": str(err)}

    def _get_equipment_dict(self, interfaces):
        """ Filters all equipments from a list of interfaces """

        equip_dict = {}
        for equip_id in [i.equipamento.id for i in interfaces]:

            equip_dict[str(equip_id)] = interfaces.filter(
                    equipamento__id=equip_id)

        return equip_dict

    def _update_equipments(self, equip_dict, iface_type, user, channel):
        """ Updates data on models instances of each equipment interface """

        for equip_id, ifaces in equip_dict.items():
            for iface in ifaces:
                try:
                    front = iface.ligacao_front.id
                except:
                    front = None

                try:
                    back = iface.ligacao_back.id
                except:
                    back = None

                iface.update(
                    self.user,
                    iface.id,
                    interface=iface.interface,
                    protegida=iface.protegida,
                    descricao=iface.descricao,
                    ligacao_front_id=front,
                    ligacao_back_id=back,
                    tipo=iface_type,
                    vlan_nativa='1'
                 )

            api_interface_facade.delete_channel(
                self.user, equip_id, ifaces, channel)

    def retrieve_by_id(self, channel_id):
        """ Tries to retrieve a Port Channel based on its id """

        channel = {}
        try:
            channel = PortChannel.get_by_pk(channel_id)

            # Copied from old implementation. We really need to iterate?
            for ch in channel:
                channel = model_to_dict(ch)

        except InterfaceNotFoundError as err:
            return None
        except:
            channel = model_to_dict(channel)

        return {"channel": channel}