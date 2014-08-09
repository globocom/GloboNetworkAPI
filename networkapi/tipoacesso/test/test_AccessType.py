# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.tipoacesso.models import TipoAcesso
from networkapi.test import BasicTestCase, me, CodeError, ConsultationTest, me, RemoveTest, AttrTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class AccessTypeConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/tipoacesso/fixtures/initial_data.yaml']
    XML_KEY = "tipo_acesso"
    ID_VALID = 1
    ID_ALTER_VALID = 6
    ID_REMOVE_VALID = 7
    OBJ = TipoAcesso

    # Urls
    URL_SAVE = "/tipoacesso/"
    URL_ALTER = "/tipoacesso/%s/"
    URL_REMOVE = "/tipoacesso/%s/"
    URL_GET_ALL = "/tipoacesso/"

    def mock_valid(self):
        mock = {}
        mock['protocolo'] = 'mock-proto'
        return mock

    def valid_attr(self, mock, obj):
        assert mock["protocolo"] == obj["protocolo"]


class AccessTypeConsultationTest(AccessTypeConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ACCESS_TYPE_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
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


class AccessTypeTest(AccessTypeConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, self.XML_KEY)

        tpa = TipoAcesso.get_by_pk(content["id"])
        self.valid_attr(mock, model_to_dict(tpa))

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
        mock["protocolo"] = "protocolo-alter-valido"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        tpa = TipoAcesso.get_by_pk(self.ID_ALTER_VALID)
        self.valid_attr(mock, model_to_dict(tpa))

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


class AccessTypeRemoveTest(AccessTypeConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.ACCESS_TYPE_NOT_FOUND

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


@me
class AccessTypeAttrProtocoloTest(AccessTypeConfigTest, AttrTest):

    KEY_ATTR = "protocolo"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(46)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        tpa = model_to_dict(TipoAcesso.get_by_pk(self.ID_VALID))

        mock = self.mock_valid()
        mock[self.KEY_ATTR] = tpa[self.KEY_ATTR]
        self.process_save_attr_invalid(mock, CodeError.ACCESS_TYPE_DUPLICATE)

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

    def test_alter_unique(self):
        tpa = model_to_dict(TipoAcesso.get_by_pk(self.ID_VALID))

        mock = self.mock_valid()
        mock[self.KEY_ATTR] = tpa[self.KEY_ATTR]
        self.process_alter_attr_invalid(
            self.ID_ALTER_VALID, mock, CodeError.ACCESS_TYPE_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)
