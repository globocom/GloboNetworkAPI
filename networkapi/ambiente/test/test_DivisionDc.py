# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.ambiente.models import DivisaoDc
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class DivisionDcConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/ambiente/fixtures/initial_data.yaml']
    XML_KEY = "division_dc"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    OBJ = DivisaoDc

    # Urls
    URL_SAVE = "/divisiondc/"
    URL_ALTER = "/divisiondc/%s/"
    URL_REMOVE = "/divisiondc/%s/"
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/divisiondc/all/"

    def mock_valid(self):
        mock = {}
        mock['name'] = "mock"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["name"] == obj["nome"]


class DivisionDcConsultationTest(DivisionDcConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.DIVISION_DC_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "division_dc")
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class DivisionDcTest(DivisionDcConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        divisiondc = valid_content(response, "division_dc")

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "division_dc")

        for ddc in content:
            if ddc["id"] == divisiondc["id"]:
                self.valid_attr(mock, ddc)
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
        mock["name"] = "DivisionDcAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "division_dc")

        for divisiondc in content:
            if divisiondc["id"] == self.ID_ALTER_VALID:
                self.valid_attr(mock, divisiondc)
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


class DivisionDcRemoveTest(DivisionDcConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.DIVISION_DC_NOT_FOUND

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


class DivisionDcAttrNameTest(DivisionDcConfigTest, AttrTest):

    KEY_ATTR = "name"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(81)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(1)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "division_dc")

        divisiondc = content[0]

        mock = self.mock_valid()
        mock["name"] = divisiondc["nome"]

        self.process_save_attr_invalid(mock, CodeError.DIVISION_DC_DUPLICATE)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(81)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(1)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "division_dc")

        divisiondc = content[0]

        mock = self.mock_valid()
        mock["name"] = divisiondc["nome"]
        self.process_alter_attr_invalid(
            self.ID_ALTER_VALID,
            mock,
            CodeError.DIVISION_DC_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)
