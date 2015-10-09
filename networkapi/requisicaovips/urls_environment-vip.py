# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from networkapi.ambiente.resource.EnvironmentVipGetAmbienteP44TxtResource import EnvironmentVipGetAmbienteP44TxtResource
from networkapi.ambiente.resource.EnvironmentVipGetClienteTxtResource import EnvironmentVipGetClienteTxtResource
from networkapi.ambiente.resource.EnvironmentVipGetFinalityResource import EnvironmentVipGetFinalityResource
from networkapi.requisicaovips.resource.OptionVipGetBalanceamentoByEVipResource import OptionVipGetBalanceamentoByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetGrupoCacheByEVipResource import OptionVipGetGrupoCacheByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetHealthcheckByEVipResource import OptionVipGetHealthcheckByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetPersistenciaByEVipResource import OptionVipGetPersistenciaByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetTimeoutByEVipResource import OptionVipGetTimeoutByEVipResource
from networkapi.requisicaovips.resource.RequestVipGetRulesByEVipResource import RequestVipGetRulesByEVipResource
from networkapi.requisicaovips.resource.OptionVipGetTrafficReturnByEVipResource import OptionVipGetTrafficReturnByEVipResource


opt_vip_timeout = OptionVipGetTimeoutByEVipResource()
opt_vip_grupocache = OptionVipGetGrupoCacheByEVipResource()
opt_vip_persistencia = OptionVipGetPersistenciaByEVipResource()
opt_vip_balanceamento = OptionVipGetBalanceamentoByEVipResource()
opt_vip_healthcheck = OptionVipGetHealthcheckByEVipResource()
opt_vip_trafficreturn = OptionVipGetTrafficReturnByEVipResource()
environment_vip_finality = EnvironmentVipGetFinalityResource()
environment_vip_cliente_txt = EnvironmentVipGetClienteTxtResource()
environment_vip_ambientep44_txt = EnvironmentVipGetAmbienteP44TxtResource()
environment_vip_rules = RequestVipGetRulesByEVipResource()

urlpatterns = patterns('',
    url(r'^get/finality/$', environment_vip_finality.handle_request,
        name='environemnt-vip.get.finality'),
    url(r'^get/cliente_txt/$', environment_vip_cliente_txt.handle_request,
        name='environemnt-vip.get.cliente_txt'),
    url(r'^get/ambiente_p44_txt/$', environment_vip_ambientep44_txt.handle_request,
        name='environemnt-vip.get.ambientep44_txt'),
    url(r'^get/timeout/(?P<id_evip>[^/]+)/$', opt_vip_timeout.handle_request,
        name='option-vip.get.timeout'),
    url(r'^get/grupo-cache/(?P<id_evip>[^/]+)/$', opt_vip_grupocache.handle_request,
        name='option-vip.get.grupocache'),
    url(r'^get/persistencia/(?P<id_evip>[^/]+)/$', opt_vip_persistencia.handle_request,
        name='option-vip.get.persistencia'),
    url(r'^get/balanceamento/(?P<id_evip>[^/]+)/$', opt_vip_balanceamento.handle_request,
        name='option-vip.get.balanceamento'),
    url(r'^get/rules/(?P<id_evip>[^/]+)(?:/(?P<id_vip>[^/]+))?/$', environment_vip_rules.handle_request,
        name='environment-vip.get.rules'),
    url(r'^get/healthcheck/(?P<id_evip>[^/]+)/$', opt_vip_healthcheck.handle_request,
        name='environment-vip.get.healthcheck'),
    url(r'^get/trafficreturn/(?P<id_evip>[^/]+)/$', opt_vip_trafficreturn.handle_request,
        name='environment-vip.get.trafficreturn')

)