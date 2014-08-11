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


from networkapi.usuario.models import UsuarioGrupo
from networkapi.test import BasicTestCase, CodeError, AttrTest, me
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class UserGroupConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/usuario/fixtures/initial_data.yaml']
    XML_KEY = "user_group"
    ID_VALID = 1
    ID_USER_ASSOCIATE = 9
    ID_USER_DISSOCIATE = 10
    ID_GROUP_ASSOCIATE = 6
    ID_GROUP_DISSOCIATE = 7

    OBJ = UsuarioGrupo

    # Urls
    URL_SAVE = ""
    URL_ALTER = ""
    URL_REMOVE = ""
    URL_GET_BY_ID = ""
    URL_GET_ALL = ""
    URL_ASSOCIATE = "/usergroup/user/%s/ugroup/%s/associate/"
    URL_DISSOCIATE = "/usergroup/user/%s/ugroup/%s/dissociate/"


class UserGroupAssociateTest(UserGroupConfigTest, AttrTest):

    def test_associate_valid(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.ID_GROUP_ASSOCIATE))
        valid_response(response)
        valid_content(response, "user_group")

    def test_associate_no_permission(self):
        response = self.client_no_permission().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.ID_GROUP_ASSOCIATE))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_associate_no_write_permission(self):
        response = self.client_no_write_permission().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.ID_GROUP_ASSOCIATE))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_associate_duplicate(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_VALID, self.ID_VALID))
        self._attr_invalid(response, CodeError.USER_GROUP_DUPLICATE)

    def test_associate_user_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_NONEXISTENT, self.ID_GROUP_ASSOCIATE))
        self._not_found(response, CodeError.USER_NOT_FOUND)

    def test_associate_user_negative(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.NEGATIVE_ATTR, self.ID_GROUP_ASSOCIATE))
        self._attr_invalid(response)

    def test_associate_user_letter(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.LETTER_ATTR, self.ID_GROUP_ASSOCIATE))
        self._attr_invalid(response)

    def test_associate_user_zero(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ZERO_ATTR, self.ID_GROUP_ASSOCIATE))
        self._attr_invalid(response)

    def test_associate_user_empty(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.EMPTY_ATTR, self.ID_GROUP_ASSOCIATE))
        self._attr_invalid(response)

    def test_associate_user_none(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.NONE_ATTR, self.ID_GROUP_ASSOCIATE))
        self._attr_invalid(response)

    def test_associate_group_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.UGROUP_NOT_FOUND)

    def test_associate_group_negative(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_associate_group_letter(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_associate_group_zero(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_associate_group_empty(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_associate_group_none(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_USER_ASSOCIATE, self.NONE_ATTR))
        self._attr_invalid(response)


class UserGroupDissociateTest(UserGroupConfigTest, AttrTest):

    def test_dissociate_valid(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.ID_GROUP_DISSOCIATE))
        valid_response(response)

    def test_dissociate_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.ID_GROUP_DISSOCIATE))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_dissociate_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.ID_GROUP_DISSOCIATE))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_dissociate_no_associate(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_ASSOCIATE, self.ID_GROUP_DISSOCIATE))
        self._attr_invalid(response, CodeError.USER_GROUP_NO_ASSOCIATE)

    def test_dissociate_user_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_NONEXISTENT, self.ID_GROUP_DISSOCIATE))
        self._not_found(response, CodeError.USER_NOT_FOUND)

    def test_dissociate_user_negative(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.NEGATIVE_ATTR, self.ID_GROUP_DISSOCIATE))
        self._attr_invalid(response)

    def test_dissociate_user_letter(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.LETTER_ATTR, self.ID_GROUP_DISSOCIATE))
        self._attr_invalid(response)

    def test_dissociate_user_zero(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ZERO_ATTR, self.ID_GROUP_DISSOCIATE))
        self._attr_invalid(response)

    def test_dissociate_user_empty(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.EMPTY_ATTR, self.ID_GROUP_DISSOCIATE))
        self._attr_invalid(response)

    def test_dissociate_user_none(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.NONE_ATTR, self.ID_GROUP_DISSOCIATE))
        self._attr_invalid(response)

    def test_dissociate_group_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.UGROUP_NOT_FOUND)

    def test_dissociate_group_negative(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_dissociate_group_letter(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_dissociate_group_zero(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_dissociate_group_empty(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_dissociate_group_none(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_USER_DISSOCIATE, self.NONE_ATTR))
        self._attr_invalid(response)
