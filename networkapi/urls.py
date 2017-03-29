# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse

from networkapi.check.CheckAction import CheckAction
# from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

api_prefix = r'^api/'

urlpatterns = patterns(
    '',
    # new API URL patterns are all prefixed with '/api/'
    url(api_prefix, include('networkapi.api_deploy.urls')),
    url(api_prefix, include('networkapi.api_environment.urls')),
    url(api_prefix, include('networkapi.api_environment_vip.urls')),
    url(api_prefix, include('networkapi.api_equipment.urls')),
    url(api_prefix, include('networkapi.api_healthcheck.urls')),
    url(api_prefix, include('networkapi.api_interface.urls')),
    url(api_prefix, include('networkapi.api_ip.urls')),
    url(api_prefix, include('networkapi.api_network.urls')),
    url(api_prefix, include('networkapi.api_ogp.urls')),
    url(api_prefix, include('networkapi.api_pools.urls')),
    url(api_prefix, include('networkapi.api_rack.urls')),
    url(api_prefix, include('networkapi.api_rest.urls')),
    url(api_prefix, include('networkapi.api_vip_request.urls')),
    url(api_prefix, include('networkapi.api_vlan.urls')),
    url(api_prefix, include('networkapi.api_vrf.urls')),
    url(api_prefix, include('networkapi.snippets.urls')),
    url(api_prefix, include('networkapi.system.urls')),

    # app healthchecks
    url(r'^check$', CheckAction().check, name='check'),
    url(r'^healthcheck$', lambda _: HttpResponse('WORKING')),

    # equipamento
    url(r'^equipamento/', include('networkapi.equipamento.urls')),
    url(r'^equipment/', include('networkapi.equipamento.urls_equipment')),
    url(r'^equipamentoacesso/',
        include('networkapi.equipamento.urls_equipamentoacesso')),
    url(r'^equipamentogrupo/', include('networkapi.equipamento.urls_equipamentogrupo')),
    url(r'^equipmenttype/', include('networkapi.equipamento.urls_equipmenttype')),
    url(r'^equipamentoambiente/',
        include('networkapi.equipamento.urls_equipamentoambiente')),
    url(r'^equipmentscript/', include('networkapi.equipamento.urls_equipmentscript')),
    url(r'^equipamentoroteiro/',
        include('networkapi.equipamento.urls_equipamentoroteiro')),
    url(r'^brand/', include('networkapi.equipamento.urls_brand')),
    url(r'^model/', include('networkapi.equipamento.urls_model')),

    # ambiente
    url(r'^ambiente/', include('networkapi.ambiente.urls')),
    url(r'^environment/', include('networkapi.ambiente.urls_environment')),
    url(r'^divisiondc/', include('networkapi.ambiente.urls_divisiondc')),
    url(r'^groupl3/', include('networkapi.ambiente.urls_groupl3')),
    url(r'^logicalenvironment/',
        include('networkapi.ambiente.urls_logicalenvironment')),
    url(r'^ipconfig/', include('networkapi.ambiente.urls_ipconfig')),

    # rules
    url(r'^rule/', include('networkapi.blockrules.urls')),

    # vlan
    url(r'^vlan/', include('networkapi.vlan.urls')),
    url(r'^net_type/', include('networkapi.vlan.urls_net_type')),

    # ip
    url(r'^ip/', include('networkapi.ip.urls')),
    url(r'^ipv4/', include('networkapi.ip.urls_ipv4')),
    url(r'^ipv6/', include('networkapi.ip.urls_ipv6')),
    url(r'^network/', include('networkapi.ip.urls_network')),
    url(r'^ip4/', include('networkapi.ip.urls_ip4')),

    # scripts
    url(r'^script/', include('networkapi.roteiro.urls')),
    url(r'^scripttype/', include('networkapi.roteiro.urls_scripttype')),

    # healthcheckexpect
    url(r'^healthcheckexpect/', include('networkapi.healthcheckexpect.urls')),

    # vips
    url(r'^vip/', include('networkapi.requisicaovips.urls')),
    url(r'^requestvip/', include('networkapi.requisicaovips.urls_requestvip')),
    url(r'^real/', include('networkapi.requisicaovips.urls_real')),
    url(r'^environment-vip/', include('networkapi.requisicaovips.urls_environment-vip')),
    url(r'^environmentvip/', include('networkapi.requisicaovips.urls_environmentvip')),
    url(r'^optionvip/', include('networkapi.requisicaovips.urls_optionvip')),

    # grupovirtual
    url(r'^grupovirtual/', include('networkapi.grupovirtual.urls')),

    # interface
    url(r'^interface/', include('networkapi.interface.urls')),
    url(r'^int/', include('networkapi.interface.urls_int')),
    url(r'^interfacetype/', include('networkapi.interface.urls_interfacetype')),
    url(r'^channel/', include('networkapi.interface.urls_channel')),

    # usuario
    url(r'^usuario/', include('networkapi.usuario.urls')),
    url(r'^user/', include('networkapi.usuario.urls_user')),
    url(r'^authenticate/', include('networkapi.usuario.urls_authenticate')),
    url(r'^user-change-pass/', include('networkapi.usuario.urls_user-change-pass')),
    url(r'^usergroup/', include('networkapi.usuario.urls_usergroup')),

    # tipoacesso
    url(r'^tipoacesso/', include('networkapi.tipoacesso.urls')),

    # grupos
    url(r'^ugroup/', include('networkapi.grupo.urls')),
    url(r'^egroup/', include('networkapi.grupo.urls_egroup')),
    url(r'^egrupo/', include('networkapi.grupo.urls_egrupo')),
    url(r'^perms/', include('networkapi.grupo.urls_perms')),
    url(r'^aperms/', include('networkapi.grupo.urls_aperms')),
    url(r'^direitosgrupoequipamento/',
        include('networkapi.grupo.urls_direitosgrupoequipamento')),

    # filter
    url(r'^filter/', include('networkapi.filter.urls')),

    # rack
    url(r'^rack/', include('networkapi.rack.urls')),

    # eventlog
    url(r'^eventlog/', include('networkapi.eventlog.urls')),

    # django admin
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
