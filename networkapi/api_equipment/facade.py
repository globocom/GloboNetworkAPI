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
from networkapi.equipamento.models import EquipamentoAmbiente


log = logging.getLogger(__name__)

def all_equipments_are_in_maintenance(equipment_list):
	
	all_equips_in_maintenance = True
	for equipment in equipment_list:
		all_equips_in_maintenance &= equipment.maintenance

	return all_equips_in_maintenance


def get_routers_by_environment(environment_id):
	return EquipamentoAmbiente.objects.select_related('equipamento').filter(ambiente=environment_id, is_router=True)

def get_equipment_map(equipment):

	equipment_map = dict()
	equipment_map['id'] = equipment.id
	equipment_map['nome'] = equipment.nome
	equipment_map['tipo_equipamento'] = equipment.tipo_equipamento.tipo_equipamento
	equipment_map['modelo'] = equipment.modelo.nome
	equipment_map['maintenance'] = equipment.maintenance

	return equipment_map