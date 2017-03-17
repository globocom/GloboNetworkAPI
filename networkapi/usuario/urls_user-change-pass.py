# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.usuario.resource.UsuarioChangePassResource import UsuarioChangePassResource

user_change_pass_resource = UsuarioChangePassResource()

urlpatterns = patterns(
    '',
    url(r'^$', user_change_pass_resource.handle_request,
        name='user.change.pass')
)
