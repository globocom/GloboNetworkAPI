# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.roteiro.models import TipoRoteiro
from networkapi.test import BasicTestCase, CodeError, ConsultationTest, me, RemoveTest, AttrTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class ScriptTypeConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/roteiro/fixtures/initial_data.yaml']
    XML_KEY = "script_type"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    OBJ = TipoRoteiro

    # Urls
    URL_SAVE = "/scripttype/"
    URL_ALTER = "/scripttype/%s/"
    URL_REMOVE = "/scripttype/%s/"
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/scripttype/all/"

    def mock_valid(self):
        mock = {}
        mock['type'] = 'type'
        mock['description'] = 'description'
        return mock

    def valid_attr(self, mock, obj):
        assert mock["type"] == obj["tipo"]
        assert mock["description"] == obj["descricao"]


class ScriptTypeConsultationTest(ScriptTypeConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.SCRIPT_TYPE_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script_type")
        valid_get_all(content, self.OBJ)

    def test_get_all_inactive(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response, httplib.UNAUTHORIZED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class ScriptTypeTest(ScriptTypeConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        script_type = valid_content(response, "script_type")

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script_type")

        for script in content:
            if script["id"] == script_type["id"]:
                self.valid_attr(mock, script)
                break

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
        mock = self.mock_valid()
        mock["type"] = "ScriptTypeAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script_type")

        for script in content:
            if script["id"] == self.ID_ALTER_VALID:
                self.valid_attr(mock, script)
                break

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {
                self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {
                self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class ScriptTypeRemoveTest(ScriptTypeConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.SCRIPT_TYPE_NOT_FOUND

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

    def test_remove_script_related(self):
        response = self.remove(self.ID_VALID)
        self._attr_invalid(response, CodeError.SCRIPT_TYPE_RELATED)

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


class ScriptTypeAttrTypeTest(ScriptTypeConfigTest, AttrTest):

    KEY_ATTR = "type"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(41)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script_type")
        script = content[0]
        mock = self.mock_valid()
        mock["type"] = script["tipo"]
        self.process_save_attr_invalid(mock, CodeError.SCRIPT_TYPE_DUPLICATE)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(41)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "script_type")
        script = content[0]
        mock = self.mock_valid()
        mock["type"] = script["tipo"]
        self.process_alter_attr_invalid(
            self.ID_ALTER_VALID,
            mock,
            CodeError.SCRIPT_TYPE_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class ScriptTypeAttrDescriptionTest(ScriptTypeConfigTest, AttrTest):

    KEY_ATTR = "description"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
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
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)
