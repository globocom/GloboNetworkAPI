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

from django.conf.urls.defaults import *
from django.http import HttpResponse

from networkapi.interface.resource.InterfaceTypeGetAllResource import InterfaceTypeGetAllResource
from networkapi.interface.resource.InterfaceChannelResource import InterfaceChannelResource

from networkapi.eventlog.resource.EventLogFindResource import EventLogFindResource
from networkapi.eventlog.resource.EventLogChoiceResource import EventLogChoiceResource

from networkapi.check.CheckAction import CheckAction

from networkapi.rack.resource.RackAddResource import RackAddResource
from networkapi.rack.resource.RackFindResource import RackFindResource
from networkapi.rack.resource.RackEditResource import RackEditResource
from networkapi.rack.resource.RackDeleteResource import RackDeleteResource
from networkapi.rack.resource.RackConfigResource import RackConfigResource
from networkapi.rack.resource.RackAplicarConfigResource import RackAplicarConfigResource
from networkapi.rack.resource.RackListAllResource import RackListAllResource
from networkapi.rack.resource.RackEnvironmentResource import RackEnvironmentResource
from networkapi.rack.resource.RackGetByEquipResource import RackGetByEquipResource
check_action = CheckAction()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

rack_add_resource = RackAddResource()
find_rack_resource = RackFindResource()
edit_rack_resource = RackEditResource()
delete_rack_resource = RackDeleteResource()
gerar_config_rack_resource = RackConfigResource()
aplicar_config_rack_resource = RackAplicarConfigResource()
list_all_racks_resource = RackListAllResource()
list_rack_environment_resource = RackEnvironmentResource()
get_rack_by_equip_resource = RackGetByEquipResource()

interface_type_get_all_resource = InterfaceTypeGetAllResource()

interface_channel_resource = InterfaceChannelResource()

eventlog_find_resource = EventLogFindResource()
eventlog_choice_resource = EventLogChoiceResource()

api_prefix = r'^api/'

urlpatterns = patterns('',
    url(api_prefix, include('networkapi.api_deploy.urls')),
    url(api_prefix, include('networkapi.api_healthcheck.urls')),
    url(api_prefix, include('networkapi.api_interface.urls')),
    url(api_prefix, include('networkapi.api_network.urls')),
    url(api_prefix, include('networkapi.api_pools.urls')),
    url(api_prefix, include('networkapi.api_vip_request.urls')),
    url(api_prefix, include('networkapi.api_vlan.urls')),
    url(api_prefix, include('networkapi.snippets.urls')),
)

urlpatterns += patterns('',
   #networkapi app healthcheck
   url(r'^check$', check_action.check, name='check'),

   #equipamento
   url(r'^equipamento/', include('networkapi.equipamento.urls')),
   url(r'^equipment/', include('networkapi.equipamento.urls_equipment')),
   url(r'^equipamentoacesso/', include('networkapi.equipamento.urls_equipamentoacesso')),
   url(r'^equipamentogrupo/', include('networkapi.equipamento.urls_equipamentogrupo')),
   url(r'^equipmenttype/', include('networkapi.equipamento.urls_equipmenttype')),
   url(r'^equipamentoambiente/', include('networkapi.equipamento.urls_equipamentoambiente')),
   url(r'^equipmentscript/', include('networkapi.equipamento.urls_equipmentscript')),
   url(r'^equipamentoroteiro/', include('networkapi.equipamento.urls_equipamentoroteiro')),
   url(r'^brand/', include('networkapi.equipamento.urls_brand')),
   url(r'^model/', include('networkapi.equipamento.urls_model')),

   #ambiente
   url(r'^ambiente/', include('networkapi.ambiente.urls')),
   url(r'^environment/', include('networkapi.ambiente.urls_environment')),
   url(r'^divisiondc/', include('networkapi.ambiente.urls_divisiondc')),
   url(r'^groupl3/', include('networkapi.ambiente.urls_groupl3')),
   url(r'^logicalenvironment/', include('networkapi.ambiente.urls_logicalenvironment')),
   url(r'^ipconfig/', include('networkapi.ambiente.urls_ipconfig')),

   #rules
   url(r'^rule/', include('networkapi.blockrules.urls')),

   #vlan
   url(r'^vlan/', include('networkapi.vlan.urls')),
   url(r'^net_type/', include('networkapi.vlan.urls_net_type')),

   #ip
   url(r'^ip/', include('networkapi.ip.urls')),
   url(r'^ipv4/', include('networkapi.ip.urls_ipv4')),
   url(r'^ipv6/', include('networkapi.ip.urls_ipv6')),
   url(r'^network/', include('networkapi.ip.urls_network')),
   url(r'^ip4/', include('networkapi.ip.urls_ip4')),

   #scripts
   url(r'^script/', include('networkapi.roteiro.urls')),
   url(r'^scripttype/', include('networkapi.roteiro.urls_scripttype')),

   #healthcheckexpect
   url(r'^healthcheckexpect/', include('networkapi.healthcheckexpect.urls')),

   #vips
   url(r'^vip/', include('networkapi.requisicaovips.urls')),
   url(r'^requestvip/', include('networkapi.requisicaovips.urls_requestvip')),
   url(r'^real/', include('networkapi.requisicaovips.urls_real')),
   url(r'^environment-vip/', include('networkapi.requisicaovips.urls_environment-vip')),
   url(r'^environmentvip/', include('networkapi.requisicaovips.urls_environmentvip')),
   url(r'^optionvip/', include('networkapi.requisicaovips.urls_optionvip')),

   #grupovirtual
   url(r'^grupovirtual/', include('networkapi.grupovirtual.urls')),

   #interface
   url(r'^interface/', include('networkapi.interface.urls')),
   url(r'^int/', include('networkapi.interface.urls_int')),

   #usuario
   url(r'^usuario/', include('networkapi.usuario.urls')),
   url(r'^user/', include('networkapi.usuario.urls_user')),
   url(r'^authenticate/', include('networkapi.usuario.urls_authenticate')),
   url(r'^user-change-pass/', include('networkapi.usuario.urls_user-change-pass')),
   url(r'^usergroup/', include('networkapi.usuario.urls_usergroup')),

   #tipoacesso
   url(r'^tipoacesso/', include('networkapi.tipoacesso.urls')),

   #grupos
   url(r'^ugroup/', include('networkapi.grupo.urls')),
   url(r'^egroup/', include('networkapi.grupo.urls_egroup')),
   url(r'^egrupo/', include('networkapi.grupo.urls_egrupo')),
   url(r'^perms/', include('networkapi.grupo.urls_perms')),
   url(r'^aperms/', include('networkapi.grupo.urls_aperms')),
   url(r'^direitosgrupoequipamento/', include('networkapi.grupo.urls_direitosgrupoequipamento')),

   #filter
   url(r'^filter/', include('networkapi.filter.urls')),
)

urlpatterns += patterns('',
   url(r'^eventlog/find/$', eventlog_find_resource.handle_request,
       name='eventlog.find'),
   url(r'^eventlog/choices/$', eventlog_choice_resource.handle_request,
       name='eventlog.choices'),
   url(r'^eventlog/version/$', eventlog_find_resource.handle_request,
       name='eventlog.version'),
   url(r'^healthcheck$',lambda _: HttpResponse("WORKING")),
   url(r'^rack/insert[/]?$', rack_add_resource.handle_request,
       name='rack.add'),
   url(r'^rack/list[/]?$', list_all_racks_resource.handle_request,
       name='list.rack'),
   url(r'^rack/find/(?P<rack_name>[^/]+)/$', find_rack_resource.handle_request,
       name='find.rack'),
   url(r'^rack/edit[/]?$', edit_rack_resource.handle_request,
       name='edit.rack'),
   url(r'^rack/(?P<id_rack>[^/]+)/$', delete_rack_resource.handle_request,
       name='delete.rack'),
   url(r'^rack/gerar-configuracao/(?P<id_rack>[^/]+)/$', gerar_config_rack_resource.handle_request,
       name='config.rack'),
   url(r'^rack/aplicar-config/(?P<id_rack>[^/]+)/$', aplicar_config_rack_resource.handle_request,
       name='aplicar.rack'),
   url(r'^rack/get-by-equip/(?P<equip_id>[^/]+)/$', get_rack_by_equip_resource.handle_request,
       name='rack.get.equip.id'),
   url(r'^interfacetype/get-type[/]?$', interface_type_get_all_resource.handle_request,
       name='interfacetype.get'),
   url(r'^rack/list-rack-environment/(?P<rack_id>[^/]+)/$', list_rack_environment_resource.handle_request,
       name='interfacetype.get'),
   url(r'^channel/editar[/]?$', interface_channel_resource.handle_request,
       name='channel.edit'),
   url(r'^channel/inserir[/]?$', interface_channel_resource.handle_request,
       name='channel.add'),
   url(r'^channel/delete/(?P<channel_name>[^/]+)/$', interface_channel_resource.handle_request,
       name='channel.delete'),
   url(r'^channel/get-by-name[/]?$', interface_channel_resource.handle_request,
       name='channel.get'),
)

urlpatterns += patterns('networkapi.test_form.views',
    url('^test-vip[/]?$', 'test_form',
        name='test_form_vip',)
)