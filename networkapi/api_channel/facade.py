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


from django.forms.models import model_to_dict

from networkapi.interface.models import PortChannel
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.interface.models import Interface
from networkapi.interface.models import TipoInterface

from networkapi.api_interface.exceptions import InterfaceException
from networkapi.api_interface.exceptions import InvalidKeyException
from networkapi.api_interface.exceptions import InterfaceTemplateException
from networkapi.api_interface import facade as api_interface_facade

from networkapi.api_deploy.facade import deploy_config_in_equipment_synchronous


class ChannelV3(object):
    """ Facade class that implements business rules for interfaces channels """

    def __init__(self, user=None):
        """ Contructor of Port Channels V3 implementation """
        self.user = user
        self.id = 42
        self.channel = None

    def create(self, data):
        pass

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

    def update(self):
        pass

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
