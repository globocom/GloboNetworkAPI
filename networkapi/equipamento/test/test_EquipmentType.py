# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.equipamento.models import TipoEquipamento
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class EquipmentTypeConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/ambiente/fixtures/initial_data.yaml']
    XML_KEY = "equipment_type"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    OBJ = TipoEquipamento

    # Urls
    URL_SAVE = "/equipmenttype/"
    URL_ALTER = ""
    URL_REMOVE = ""
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/equipmenttype/all/"

    def mock_valid(self):
        mock = {}
        mock['name'] = "mock"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["name"] == obj["nome"]


class EquipmentTypeConsultationTest(EquipmentTypeConfigTest, ConsultationTest):

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "equipment_type")
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentTypeTest(EquipmentTypeConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        equipment_type = valid_content(response, "equipment_type")

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "equipment_type")

        for etype in content:
            if etype["id"] == equipment_type["id"]:
                self.valid_attr(mock, etype)
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
