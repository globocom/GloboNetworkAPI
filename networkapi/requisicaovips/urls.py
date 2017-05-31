# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.requisicaovips.resource.CreateVipResource import CreateVipResource
from networkapi.requisicaovips.resource.DsrL3toVipAllResource import DsrL3toVipAllResource
from networkapi.requisicaovips.resource.DsrL3toVipResource import DsrL3toVipResource
from networkapi.requisicaovips.resource.RemoveVipResource import RemoveVipResource
from networkapi.requisicaovips.resource.RequestAllVipsIPv4Resource import RequestAllVipsIPv4Resource
from networkapi.requisicaovips.resource.RequestAllVipsIPv6Resource import RequestAllVipsIPv6Resource
from networkapi.requisicaovips.resource.RequestAllVipsResource import RequestAllVipsResource
from networkapi.requisicaovips.resource.RequestHealthcheckResource import RequestHealthcheckResource
from networkapi.requisicaovips.resource.RequestMaxconResource import RequestMaxconResource
from networkapi.requisicaovips.resource.RequestPersistenceResource import RequestPersistenceResource
from networkapi.requisicaovips.resource.RequestPriorityResource import RequestPriorityResource
from networkapi.requisicaovips.resource.RequestVipL7ApplyResource import RequestVipL7ApplyResource
from networkapi.requisicaovips.resource.RequestVipL7Resource import RequestVipL7Resource
from networkapi.requisicaovips.resource.RequestVipL7RollbackResource import RequestVipL7RollbackResource
from networkapi.requisicaovips.resource.RequestVipL7ValidateResource import RequestVipL7ValidateResource
from networkapi.requisicaovips.resource.RequestVipRealEditResource import RequestVipRealEditResource
from networkapi.requisicaovips.resource.RequestVipRealValidResource import RequestVipRealValidResource
from networkapi.requisicaovips.resource.RequestVipRuleResource import RequestVipRuleResource
from networkapi.requisicaovips.resource.RequestVipsRealResource import RequestVipsRealResource
from networkapi.requisicaovips.resource.RequestVipValidateResource import RequestVipValidateResource
from networkapi.requisicaovips.resource.RequisicaoVipDeleteResource import RequisicaoVipDeleteResource
from networkapi.requisicaovips.resource.RequisicaoVipsResource import RequisicaoVipsResource

vip_l7_resource = RequestVipL7Resource()
vip_l7_validate_resource = RequestVipL7ValidateResource()
vip_l7_apply_resource = RequestVipL7ApplyResource()
vip_l7_rollback_resource = RequestVipL7RollbackResource()
vip_add_block_resource = RequestVipRuleResource()
vip_request_resource = RequisicaoVipsResource()
vip_delete_resource = RequisicaoVipDeleteResource()
vip_validate_resource = RequestVipValidateResource()
vip_create_resource = CreateVipResource()
vip_remove_resource = RemoveVipResource()
vip_list_all_resource = RequestAllVipsResource()
vip_list_all_ipv4_resource = RequestAllVipsIPv4Resource()
vip_list_all_ipv6_resource = RequestAllVipsIPv6Resource()
vip_healthcheck_resource = RequestHealthcheckResource()
vip_persistence_resource = RequestPersistenceResource()
vip_maxcon = RequestMaxconResource()
vip_priority = RequestPriorityResource()
vip_real = RequestVipsRealResource()
vip_real_edit = RequestVipRealEditResource()
vip_real_valid = RequestVipRealValidResource()
dsrl3tovip = DsrL3toVipResource()
drsl3_all = DsrL3toVipAllResource()

urlpatterns = patterns(
    '',
    url(r'^$', vip_request_resource.handle_request,
        name='vip.insert'),
    url(r'^all/$', vip_list_all_resource.handle_request,
        name='vip.list_all'),
    url(r'^ipv4/all/$', vip_list_all_ipv4_resource.handle_request,
        name='vip.ipv4.all'),
    url(r'^ipv6/all/$', vip_list_all_ipv6_resource.handle_request,
        name='vip.ipv6.all'),
    url(r'^create/$', vip_create_resource.handle_request,
        name='vip.create'),
    url(r'^(?P<id_vip>\d+)/criar/$', vip_create_resource.handle_request,
        name='vip.create.by.pk'),
    url(r'^remove/$', vip_remove_resource.handle_request,
        name='vip.remove'),
    url(r'^real/$', vip_real.handle_request,
        name='vip.real'),
    # url(r'^(?P<id_vip>[^/]+)/filter/$', vip_l7_resource.handle_request,
    #     name='vip.get.l7.by.pk'),
    url(r'^(?P<id_vip>[^/]+)/$', vip_request_resource.handle_request,
        name='vip.get.update.by.pk'),
    url(r'^(?P<id_vip>[^/]+)/(?P<operacao>maxcon)/(?P<maxcon>[^/]+)/$', vip_maxcon.handle_request,
        name='vip.update.maxcon.by.pk'),
    url(r'^(?P<id_vip>[^/]+)/(?P<operacao>healthcheck)/$', vip_healthcheck_resource.handle_request,
        name='vip.update.healthcheck.by.pk'),
    url(r'^(?P<id_vip>[^/]+)/(?P<operacao>persistence)/$', vip_persistence_resource.handle_request,
        name='vip.update.persistence.by.pk'),
    url(r'^(?P<id_vip>[^/]+)/(?P<operacao>priority)/$', vip_priority.handle_request,
        name='vip.update.priority.by.pk'),
    url(r'^delete/(?P<id_vip>[^/]+)/$', vip_delete_resource.handle_request,
        name='vip.delete.by.pk'),
    url(r'^validate/(?P<id_vip>[^/]+)/$', vip_validate_resource.handle_request,
        name='vip.validate.by.pk'),
    url(r'^real/edit/$', vip_real_edit.handle_request,
        name='vip.real.edit'),
    # url(r'^real/valid/$', vip_real_valid.handle_request,
    #     name='vip.real.valid'),
    # url(r'^l7/(?P<id_vip>[^/]+)/$', vip_l7_resource.handle_request,
    #     name='vip.get.l7.by.pk'),
    # url(r'^l7/(?P<id_vip>[^/]+)/validate/$', vip_l7_validate_resource.handle_request,
    #     name='vip.l7.validate.by.pk'),
    # url(r'^l7/(?P<id_vip>[^/]+)/apply/$',vip_l7_apply_resource.handle_request,
    #      name='vip.l7.apply.by.pk'),
    # url(r'^l7/(?P<id_vip>[^/]+)/rollback/$', vip_l7_rollback_resource.handle_request,
    #     name='vip.l7.rollback.by.pk'),
    url(r'^add_block/(?P<id_vip>\d+)/(?P<id_block>\d+)/(?P<override>\d+)[/]?$', vip_add_block_resource.handle_request,
        name='vip.add.block'),
    # url(r'^dsrl3/all/$', drsl3_all.handle_request,
    #     name='dsrl3.vip.all'),
    # url(r'^dsrl3/(?P<id_dsrl3_vip>[^/]+)/$', dsrl3tovip.handle_request,
    #     name='dsrl3.vip.search')
)
