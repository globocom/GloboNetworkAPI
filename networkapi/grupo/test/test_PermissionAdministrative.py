# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.grupo.models import PermissaoAdministrativa
from networkapi.test import BasicTestCase, me, CodeError, ConsultationTest, RemoveTest, AttrTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, is_valid_attr, valid_get_all
import httplib


class PermissionAdministrativeConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/grupo/fixtures/initial_data.yaml']
    XML_KEY = "administrative_permission"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 4
    OBJ = PermissaoAdministrativa

    ID_UGROUP_VALID = 1

    # Urls
    URL_SAVE = "/aperms/"
    URL_ALTER = "/aperms/%s/"
    URL_REMOVE = "/aperms/%s/"
    URL_GET_BY_ID = "/aperms/get/%s/"
    URL_GET_ALL = "/aperms/all/"
    URL_LIST_BY_GROUP = "/aperms/group/%s/"

    def mock_valid(self):
        mock = {}
        mock['id_permission'] = 1
        mock['id_group'] = 2
        mock['read'] = '0'
        mock['write'] = '0'
        return mock

    def mock_alter_valid(self):
        mock = {}
        mock['id_permission'] = 1
        mock['id_group'] = 5
        mock['read'] = '0'
        mock['write'] = '0'
        return mock

    def valid_attr(self, mock, obj):
        assert mock["id_permission"] == int(obj["permission"])
        assert mock["id_group"] == int(obj["ugrupo"])
        assert bool(mock["read"]) == bool(obj["leitura"])
        assert bool(mock["write"]) == bool(obj["escrita"])


class PermissionAdministrativeConsultationTest(PermissionAdministrativeConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.PERMISSION_ADMINISTRATIVE_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "perms")
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_valid(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        valid_content(response, "perm")

    def test_get_by_id_no_permission(self):
        response = self.get_by_id(self.ID_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.get_by_id(
            self.ID_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

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


class PermissionAdministrativeTest(PermissionAdministrativeConfigTest, AttrTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, "perm")

        response = self.get_by_id(content["id"])
        valid_response(response)
        perm = valid_content(response, "perm")

        self.valid_attr(mock, perm)

    def test_save_duplicate(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        perm = valid_content(response, "perm")

        mock = self.mock_valid()
        mock["id_permission"] = perm["permission"]
        mock["id_group"] = perm["ugrupo"]

        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(
            response, CodeError.PERMISSION_ADMINISTRATIVE_DUPLICATE)

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_alter_valid()
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_by_id(self.ID_ALTER_VALID)
        valid_response(response)
        perm = valid_content(response, "perm")

        self.valid_attr(mock, perm)

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class PermissionAdministrativeRemoveTest(PermissionAdministrativeConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.PERMISSION_ADMINISTRATIVE_NOT_FOUND

    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_negative(self):
        self.remove_negative()

    def test_remove_letter(self):
        self.remove_letter()

    def test_remove_zero(self):
        self.remove_zero()

    def test_remove_empty(self):
        self.remove_empty()


class PermissionAdministrativeAttrPermissionTest(PermissionAdministrativeConfigTest, AttrTest):

    KEY_ATTR = "id_permission"
    CODE_ERROR_NOT_FOUND = CodeError.PERMISSION_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_nonexistent(self):
        self.alter_attr_nonexistent(self.ID_ALTER_VALID)

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ID_ALTER_VALID)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class PermissionAdministrativeAttrGroupTest(PermissionAdministrativeConfigTest, AttrTest):

    KEY_ATTR = "id_group"
    CODE_ERROR_NOT_FOUND = CodeError.UGROUP_NOT_FOUND

    def test_save_nonexistent(self):
        self.save_attr_nonexistent()

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_nonexistent(self):
        self.alter_attr_nonexistent(self.ID_ALTER_VALID)

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ID_ALTER_VALID)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class PermissionAdministrativeAttrReadTest(PermissionAdministrativeConfigTest, AttrTest):

    KEY_ATTR = "read"

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class PermissionAdministrativeAttrWriteTest(PermissionAdministrativeConfigTest, AttrTest):

    KEY_ATTR = "write"

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


@me
class PermissionAdministrativeGetByUGroupTest(PermissionAdministrativeConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.UGROUP_NOT_FOUND

    def test_get_by_ugroup_valid(self):
        response = self.client_autenticado().get(
            self.URL_LIST_BY_GROUP % self.ID_UGROUP_VALID)
        valid_response(response)
        valid_content(response)

    def test_get_by_ugroup_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_LIST_BY_GROUP % self.ID_UGROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ugroup_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_LIST_BY_GROUP % self.ID_UGROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_ugroup_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_LIST_BY_GROUP % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_ugroup_negative(self):
        response = self.client_autenticado().get(
            self.URL_LIST_BY_GROUP % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_ugroup_letter(self):
        response = self.client_autenticado().get(
            self.URL_LIST_BY_GROUP % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_ugroup_zero(self):
        response = self.client_autenticado().get(
            self.URL_LIST_BY_GROUP % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_ugroup_empty(self):
        response = self.client_autenticado().get(
            self.URL_LIST_BY_GROUP % self.EMPTY_ATTR)
        self._attr_invalid(response)
