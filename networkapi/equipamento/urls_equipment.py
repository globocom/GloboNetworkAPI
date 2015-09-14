from __future__ import absolute_import

from django.conf.urls import patterns, include, url

from networkapi.equipamento.resource.EquipmentGetAllResource import EquipmentGetAllResource
from networkapi.equipamento.resource.EquipmentGetByGroupEquipmentResource import EquipmentGetByGroupEquipmentResource
from networkapi.equipamento.resource.EquipmentGetIpsByAmbiente import EquipmentGetIpsByAmbiente

equipment_get_all_resource = EquipmentGetAllResource()
equipment_get_by_group_resource = EquipmentGetByGroupEquipmentResource()
equipment_get_ips_resource = EquipmentGetIpsByAmbiente()

urlpatterns = patterns('',
   url(r'^all/$', equipment_get_all_resource.handle_request,
       name='equipment.get.all'),
   url(r'^group/(?P<id_egroup>[^/]+)/$', equipment_get_by_group_resource.handle_request,
       name='equipment.get.by.group'),
   url(r'^getipsbyambiente/(?P<equip_name>[^/]+)/(?P<id_ambiente>[^/]+)/$',equipment_get_ips_resource.handle_request,
       name='equipment.get.by.ambiente')
)