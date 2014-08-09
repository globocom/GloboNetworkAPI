# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.db.models import Q
from networkapi.usuario.models import Usuario
from networkapi.test import BasicTestCase, me, CodeError, ConsultationTest, me, RemoveTest, AttrTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, valid_get_all, valid_get_filtered, string_generator
from networkapi.test.assertions import assert_response_error
import hashlib
import httplib
from networkapi.test import xml2dict


class UserConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/usuario/fixtures/initial_data.yaml']
    XML_KEY = "user"
    ID_VALID = 1
    ID_REMOVE_VALID = 7
    ID_ALTER_VALID = 6
    OBJ = Usuario

    UGROUP_ID_VALID = 1

    # Urls
    URL_SAVE = "/user/"
    URL_ALTER = "/user/%s/"
    URL_REMOVE = "/user/%s/"
    URL_GET_BY_ID = "/user/get/%s/"
    URL_GET_ALL = "/user/all/"
    URL_GET_BY_GROUP = "/user/group/%s/"
    URL_GET_BY_GROUP_OUT = "/user/out/group/%s/"
    URL_AUTHENTICATE = "/authenticate/"
    URL_LIST_WITH_USER_GROUP = "/usuario/get/"
    URL_CHANGE_PASS = "/user-change-pass/"

    def mock_valid(self):
        mock = {}
        mock['user'] = 'mau'
        mock['email'] = 'teste@teste.com'
        mock['name'] = 'TESTE'
        mock['active'] = '0'
        mock['password'] = '12345678'
        return mock

    def mock_alter_valid(self):
        mock = {}
        mock['user'] = 'TES'
        mock['email'] = 'teste@teste.com'
        mock['name'] = 'TESTE'
        mock['active'] = '0'
        mock['password'] = '25d55ad283aa400af464c76d713c07ad'
        return mock

    def user_login_valid(self):
        u_dict = {}
        u_dict['username'] = 'TEST'
        u_dict['password'] = '12345678'
        u_dict['is_ldap_user'] = 'False'
        return u_dict

    def user_ldap_login_valid(self):
        u_dict = {}
        u_dict['username'] = 'USER_LDAP'
        u_dict['password'] = string_generator(10)
        u_dict['is_ldap_user'] = 'True'
        return u_dict

    def user_change_pass_valid(self):
        u_dict = {}
        u_dict['user_id'] = '8'
        u_dict['password'] = '12457801'
        return u_dict

    def valid_attr(self, mock, obj):
        assert mock["user"] == obj["user"]
        assert mock["email"] == obj["email"]
        assert mock["name"] == obj["nome"]
        assert bool(mock["active"]) == bool(obj["ativo"])
        assert mock["password"] == obj["pwd"]


class UserConsultationTest(UserConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.USER_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "usuario")
        valid_get_all(content, self.OBJ)

    def test_get_all_inactive(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response, httplib.UNAUTHORIZED)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_valid(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        valid_content(response, 'usuario')

    def test_get_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_get_by_id_negative(self):
        self.get_by_id_negative()

    def test_get_by_id_letter(self):
        self.get_by_id_letter()

    def test_get_by_id_zero(self):
        self.get_by_id_zero()

    def test_get_by_id_empty(self):
        self.get_by_id_empty()


class UserTest(UserConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, "usuario")

        response = self.get_by_id(content["id"])
        valid_response(response)
        user = valid_content(response, "usuario")

        assert bool(user["ativo"])

        mock['password'] = hashlib.md5(mock['password']).hexdigest()
        self.valid_attr(mock, user)

    def test_alter_valid(self):
        mock = self.mock_alter_valid()
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_by_id(self.ID_ALTER_VALID)
        valid_response(response)
        user = valid_content(response, "usuario")
        self.valid_attr(mock, user)


class UserRemoveTest(UserConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.USER_NOT_FOUND

    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID,
            CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID,
            CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_group_related(self):
        response = self.remove(self.ID_VALID)
        self._attr_invalid(response, CodeError.USER_GROUP_RELATED)

    def test_remove_by_id_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_by_id_negative(self):
        self.remove_negative()

    def test_remove_by_id_letter(self):
        self.remove_letter()

    def test_remove_by_id_zero(self):
        self.remove_zero()

    def test_remove_by_id_empty(self):
        self.remove_empty()


class UserAttrNameTest(UserConfigTest, AttrTest):

    KEY_ATTR = "name"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(201)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class UserAttrUserTest(UserConfigTest, AttrTest):

    KEY_ATTR = "user"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(46)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        user = valid_content(response, "usuario")

        mock = self.mock_valid()
        mock["user"] = user["nome"]
        self.process_save_attr_invalid(mock, CodeError.USER_DUPLICATE)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(46)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)

    def test_alter_unique(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        user = valid_content(response, "usuario")

        mock = self.mock_valid()
        mock["user"] = user["nome"]
        self.process_alter_attr_invalid(
            self.ID_ALTER_VALID,
            mock,
            CodeError.USER_DUPLICATE)


class UserAttrPwdTest(UserConfigTest, AttrTest):

    KEY_ATTR = "password"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(46)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(46)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class UserAttrEmailTest(UserConfigTest, AttrTest):

    KEY_ATTR = "email"

    def test_save_invalid(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'test@a.com.com@test'
        self.process_save_attr_invalid(mock)

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(301)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(301)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class UserAttrActiveTest(UserConfigTest, AttrTest):

    KEY_ATTR = "active"

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)


@me
class UserAttrUserLdapTest(UserConfigTest, AttrTest):

    KEY_ATTR = "user_ldap"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(46)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(46)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)


class UserByGroupConsultationTest(UserConfigTest, ConsultationTest):

    def test_get_by_group_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP %
            self.UGROUP_ID_VALID)
        valid_response(response)
        content = valid_content(response, "users")

        query = Q(grupos=self.UGROUP_ID_VALID)
        valid_get_filtered(content, Usuario, query)

    def test_get_by_group_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_GROUP %
            self.UGROUP_ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_group_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_GROUP %
            self.UGROUP_ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_group_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP %
            self.ID_NONEXISTENT)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=CodeError.USER_GROUP_NOT_FOUND)

    def test_get_by_group_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP %
            self.NEGATIVE_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_get_by_group_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP %
            self.LETTER_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_get_by_group_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP %
            self.ZERO_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_get_by_group_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP %
            self.EMPTY_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)


class UserByGroupOutConsultationTest(UserConfigTest, ConsultationTest):

    def test_get_by_group_out_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP_OUT %
            self.UGROUP_ID_VALID)
        valid_response(response)
        content = valid_content(response, "users")

        query = Q(grupos=self.UGROUP_ID_VALID)
        valid_get_filtered(content, Usuario, ~query)

    def test_get_by_group_out_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_GROUP_OUT %
            self.UGROUP_ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_group_out_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_GROUP_OUT %
            self.UGROUP_ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_group_out_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP_OUT %
            self.ID_NONEXISTENT)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=CodeError.USER_GROUP_NOT_FOUND)

    def test_get_by_group_out_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP_OUT %
            self.NEGATIVE_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_get_by_group_out_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP_OUT %
            self.LETTER_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_get_by_group_out_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP_OUT %
            self.ZERO_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_get_by_group_out_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_GROUP_OUT %
            self.EMPTY_ATTR)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)


class UserAuthenticateTest(UserConfigTest, ConsultationTest):

    def test_authenticate_valid(self):
        mock = self.user_login_valid()
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, "user")

    def test_authenticate_ldap_valid(self):
        mock = self.user_ldap_login_valid()
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, "user")

    def test_authenticate_ldap_nonexistent(self):
        mock = self.user_ldap_login_valid()
        mock['username'] = string_generator(10)
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response)
        assert xml2dict(response.content) is None

    def test_authenticate_wrong_username(self):
        mock = self.user_login_valid()
        mock['username'] = string_generator(10)
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response)
        assert xml2dict(response.content) is None

    def test_authenticate_wrong_password(self):
        mock = self.user_login_valid()
        mock['password'] = string_generator(10)
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response)
        assert xml2dict(response.content) is None

    def test_authenticate_empty_username(self):
        mock = self.user_login_valid()
        mock['username'] = ''
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_authenticate_none_username(self):
        mock = self.user_login_valid()
        mock['username'] = None
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_authenticate_empty_password(self):
        mock = self.user_login_valid()
        mock['password'] = ''
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_authenticate_none_password(self):
        mock = self.user_login_valid()
        mock['password'] = None
        response = self.client_autenticado().postXML(
            self.URL_AUTHENTICATE, {
                self.XML_KEY: mock})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)


class UserWithGroupConsultationTest(UserConfigTest, ConsultationTest):

    def test_get_all_with_group(self):
        response = self.client_autenticado().get(self.URL_LIST_WITH_USER_GROUP)
        valid_response(response)
        content = valid_content(response, "usuario")
        valid_get_all(content, self.OBJ)

    def test_get_all_with_group_inactive(self):
        response = self.client_no_active().get(self.URL_LIST_WITH_USER_GROUP)
        valid_response(response, httplib.UNAUTHORIZED)

    def test_get_all_with_group_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_LIST_WITH_USER_GROUP)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_with_group_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_LIST_WITH_USER_GROUP)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class UserChangePasswordTest(UserConfigTest, AttrTest):

    def test_change_pass_valid(self):
        data = self.user_change_pass_valid()
        response = self.client_autenticado().postXML(
            self.URL_CHANGE_PASS, {
                self.XML_KEY: data})
        valid_response(response)
        assert xml2dict(response.content) is None

    def test_change_pass_inactive(self):
        data = self.user_change_pass_valid()
        response = self.client_no_active().postXML(
            self.URL_CHANGE_PASS, {
                self.XML_KEY: data})
        valid_response(response, httplib.UNAUTHORIZED)

    def test_change_pass_no_permission(self):
        data = self.user_change_pass_valid()
        response = self.client_no_permission().postXML(
            self.URL_CHANGE_PASS, {
                self.XML_KEY: data})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_change_pass_empty_pass(self):
        data = self.user_change_pass_valid()
        data['password'] = ''
        response = self.client_autenticado().postXML(
            self.URL_CHANGE_PASS, {
                self.XML_KEY: data})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_change_pass_none_pass(self):
        data = self.user_change_pass_valid()
        data['password'] = None
        response = self.client_autenticado().postXML(
            self.URL_CHANGE_PASS, {
                self.XML_KEY: data})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_change_pass_minsize(self):
        data = self.user_change_pass_valid()
        data['password'] = string_generator(2)
        response = self.client_autenticado().postXML(
            self.URL_CHANGE_PASS, {
                self.XML_KEY: data})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)

    def test_change_pass_maxsize(self):
        data = self.user_change_pass_valid()
        data['password'] = string_generator(46)
        response = self.client_autenticado().postXML(
            self.URL_CHANGE_PASS, {
                self.XML_KEY: data})
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        self._attr_invalid(response)
