# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.healthcheckexpect.models import HealthcheckExpect
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class HealthcheckConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/healthcheckexpect/fixtures/initial_data.yaml']
    XML_KEY = "healthcheck"
    XML_RETURN = "healthcheck_expect"

    OBJ = HealthcheckExpect

    ID_VALID = 1
    ID_ENVIRONMENT_VALID = 1

    EXPECT_STRING_VALID = "stringValida"

    # Urls
    URL_SAVE = "/healthcheckexpect/add/"
    URL_SAVE_EXPECT_STRING = "/healthcheckexpect/add/expect_string/"
    URL_GET_BY_ID = "/healthcheckexpect/get/%s/"
    URL_GET_BY_ENV_ID = "/healthcheckexpect/ambiente/%s/"
    URL_GET_ALL = "/healthcheckexpect/distinct/busca/"

    def mock_valid(self):
        mock = {}
        mock['id_ambiente'] = 2
        mock['expect_string'] = "NewExpect"
        mock['match_list'] = "NewMatchList"
        return mock

    def mock_expect_string_valid(self):
        mock = {}
        mock['expect_string'] = "NewExpectSimple"
        return mock


class HealthcheckConsultationTest(HealthcheckConfigTest, ConsultationTest):

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_RETURN, True)
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class HealthcheckConsultationHealthcheckTest(HealthcheckConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.HEALTHCHECKEXPECT_NOT_FOUND

    def test_get_by_healthcheck(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_RETURN, True)

    def test_get_by_healthcheck_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ID %
            self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_healthcheck_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ID %
            self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_healthcheck_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_healthcheck_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_healthcheck_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_healthcheck_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_healthcheck_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ID %
            self.EMPTY_ATTR)
        self._attr_invalid(response)


class HealthcheckConsultationEnvironmentTest(HealthcheckConfigTest, AttrTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENVIRONMENT_NOT_FOUND

    def test_get_by_environment(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID %
            self.ID_ENVIRONMENT_VALID)
        valid_response(response)
        valid_content(response, self.XML_RETURN, True)

    def test_get_by_environment_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ENV_ID %
            self.ID_ENVIRONMENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_ENV_ID %
            self.ID_ENVIRONMENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID %
            self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_environment_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID %
            self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID %
            self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID %
            self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV_ID %
            self.EMPTY_ATTR)
        self._attr_invalid(response)


class HealthcheckTest(HealthcheckConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_RETURN)

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_expect_string_valid(self):
        mock = self.mock_expect_string_valid()
        response = self.client_autenticado().postXML(
            self.URL_SAVE_EXPECT_STRING, {
                self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_RETURN)

    def test_save_expect_string_no_permission(self):
        mock = self.mock_expect_string_valid()
        response = self.client_no_permission().postXML(
            self.URL_SAVE_EXPECT_STRING, {
                self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_expect_string_no_write_permission(self):
        mock = self.mock_expect_string_valid()
        response = self.client_no_write_permission().postXML(
            self.URL_SAVE_EXPECT_STRING, {
                self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class HealthcheckAttrAmbientTest(HealthcheckConfigTest, AttrTest):

    KEY_ATTR = "id_ambiente"
    CODE_ERROR_NOT_FOUND = CodeError.ENVIRONMENT_NOT_FOUND

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


class HealthcheckAttrExpectStringTest(HealthcheckConfigTest, AttrTest):

    KEY_ATTR = "expect_string"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_save_expect_string_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        response = self.client_autenticado().postXML(
            self.URL_SAVE_EXPECT_STRING, {
                self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_expect_string_empty(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_EXPECT_STRING, {
                self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_expect_string_none(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        response = self.client_autenticado().postXML(
            self.URL_SAVE_EXPECT_STRING, {
                self.XML_KEY: mock})
        self._attr_invalid(response)


class HealthcheckAttrMatchListTest(HealthcheckConfigTest, AttrTest):

    KEY_ATTR = "match_list"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()
