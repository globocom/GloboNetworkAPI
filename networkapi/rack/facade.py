# -*- coding:utf-8 -*-

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
from networkapi.equipamento.models import Equipamento
from networkapi.rack.models import Rack
from networkapi.rack import exceptions
from django.core.exceptions import ObjectDoesNotExist

log = logging.getLogger(__name__)

def save_rack(user, rack_dict):

    rack = Rack()

    rack.mac_sw1 = rack_dict.get('sw1_mac')
    rack.mac_sw2 = rack_dict.get('sw2_mac')
    rack.mac_ilo = rack_dict.get('sw3_mac')
    id_sw1 = rack_dict.get('sw1_id')
    id_sw2 = rack_dict.get('sw2_id')
    id_sw3 = rack_dict.get('sw3_id')

    if not rack_dict.get('name'):
        raise exceptions.InvalidInputException("O nome do Rack não foi informado.")
    else:
        rack.nome = rack_dict.get('name')
    if not rack_dict.get('number'):
        raise exceptions.InvalidInputException("O número do Rack não foi informado.")
    else:
        rack.numero = rack_dict.get('number')
    try:
        Rack.objects.get(numero__iexact=rack.numero)
        raise exceptions.RackNumberDuplicatedValueError()
    except ObjectDoesNotExist:
        pass
    try:
        Rack.objects.get(nome__iexact=rack.nome)
        raise exceptions.RackNameDuplicatedError()
    except ObjectDoesNotExist:
        pass

    if id_sw1 is not None:
        rack.id_sw1 = Equipamento(id=int(id_sw1))
    if id_sw2 is not None:
        rack.id_sw2 = Equipamento(id=int(id_sw2))
    if id_sw3 is not None:
        rack.id_ilo = Equipamento(id=int(id_sw3))

    rack.save(user)
    return rack