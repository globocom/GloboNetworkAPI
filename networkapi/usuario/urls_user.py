# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns
from django.conf.urls import url

from networkapi.usuario.resource.UserAddResource import UserAddResource
from networkapi.usuario.resource.UserAlterRemoveResource import UserAlterRemoveResource
from networkapi.usuario.resource.UserGetAllResource import UserGetAllResource
from networkapi.usuario.resource.UserGetByGroupUserOutGroup import UserGetByGroupUserOutGroup
from networkapi.usuario.resource.UserGetByGroupUserResource import UserGetByGroupUserResource
from networkapi.usuario.resource.UserGetByIdResource import UserGetByIdResource
from networkapi.usuario.resource.UserGetByLdapResource import UserGetByLdapResource

user_add_resource = UserAddResource()
user_alter_remove_resource = UserAlterRemoveResource()
user_get_by_pk_resource = UserGetByIdResource()
user_get_all_resource = UserGetAllResource()
user_get_by_ldap_resource = UserGetByLdapResource()
user_get_by_group_resource = UserGetByGroupUserResource()
user_get_by_group_out_group_resource = UserGetByGroupUserOutGroup()

urlpatterns = patterns(
    '',
    url(r'^$', user_add_resource.handle_request,
        name='user.add'),
    url(r'^all/$', user_get_all_resource.handle_request,
        name='user.get.all'),
    url(r'^(?P<id_user>[^/]+)/$', user_alter_remove_resource.handle_request,
        name='user.update.remove.by.pk'),
    url(r'^get/(?P<id_user>[^/]+)/$', user_get_by_pk_resource.handle_request,
        name='user.get.by.id'),
    url(r'^group/(?P<id_ugroup>[^/]+)/$', user_get_by_group_resource.handle_request,
        name='user.get.by.group'),
    url(r'^out/group/(?P<id_ugroup>[^/]+)/$', user_get_by_group_out_group_resource.handle_request,
        name='user.get.by.group.out.group'),
    url(r'^get/ldap/(?P<user_name>[^/]+)/$', user_get_by_ldap_resource.handle_request,
        name='user.get.ldap')
)
