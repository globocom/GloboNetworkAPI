# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.grupo.resource.GrupoResource import DireitoGrupoEquipamentoResource

access_right_resource = DireitoGrupoEquipamentoResource()

urlpatterns = patterns(
    '',
    url(r'^$', access_right_resource.handle_request,
        name='access_right.search.insert'),
    # url(r'^ugrupo/(?P<id_grupo_usuario>[^/]+)/$', access_right_resource.handle_request,
    #     name='access_right.search.by.ugroup'),
    url(r'^egrupo/(?P<id_grupo_equipamento>[^/]+)/$', access_right_resource.handle_request,
        name='access_right.search.by.egroup'),
    url(r'^(?P<id_direito>[^/]+)/$', access_right_resource.handle_request,
        name='access_right.search.update.remove.by.pk'),
)
