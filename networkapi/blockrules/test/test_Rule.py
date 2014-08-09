# -*- coding:utf-8 -*-

from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, string_generator
import httplib
from networkapi.blockrules.models import Rule


class RuleConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/blockrules/fixtures/initial_data.yaml']
    XML_KEY = 'map'
    ID_ENV_WITH_RULE = '100'
    ID_ENV_WITHOUT_RULE = '101'
    ID_ENV_INVALID = '999'
    ID_VALID_RULE = '1'
    ID_INVALID_RULE = '999'
    ID_UPDATE_VALID = '2'
    ID_REMOVE_VALID = '3'
    ID_VALID_BLOCK = '1'
    ID_INVALID_BLOCK = '5'
    ID_ENV_TO_INSERT = '101'
    ID_NONEXISTENT = '12312'
    OBJ = Rule

    NAME_MAX_LENGTH = 80

    # Urls
    URL_GET_BY_ID = "/rule/get_by_id/%s/"
    URL_GET_BY_ENV = "/rule/all/%s/"
    URL_SAVE = "/rule/save/"
    URL_ALTER = "/rule/update/"
    URL_REMOVE = "/rule/delete/%s/"

    def mock_valid(self):
        mock = {}
        mock["name"] = "NAME"
        mock["id_env"] = self.ID_ENV_TO_INSERT
        mock["contents"] = ['conteúdo1', 'conteúdo2', 'conteúdo3']
        mock["blocks_id"] = [0, 0, 0]
        return mock

    def mock_valid_alter(self):
        mock = {}
        mock["name"] = "NAME ALTER"
        mock["id_rule"] = self.ID_UPDATE_VALID
        mock["id_env"] = self.ID_ENV_TO_INSERT
        mock["contents"] = ['conteúdo111', 'conteúdo222', 'conteúdo333']
        mock["blocks_id"] = [0, 0, 0]
        return mock

    def alter_attr_invalid(self, attr, code_error=None):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = attr
        response = self.client_autenticado().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        self._attr_invalid(response, code_error)


class RuleConsultationTest(RuleConfigTest, ConsultationTest):

    def test_get_by_environment(self):

        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV % self.ID_ENV_WITH_RULE)
        valid_response(response)
        valid_content(response, 'rules', True)

    def test_get_by_environment_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_ENV % self.ID_ENV_WITH_RULE)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_environment_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_none(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV % self.NONE_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_environment_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_ENV % self.EMPTY_ATTR)
        self._attr_invalid(response)


class RuleTest(RuleConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_update_valid(self):
        mock = self.mock_valid_alter()
        response = self.client_autenticado().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response)

    def test_update_no_permission(self):
        mock = self.mock_valid_alter()
        response = self.client_no_permission().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_update_no_write_permission(self):
        mock = self.mock_valid_alter()
        response = self.client_no_write_permission().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class RuleAttrIdEnvTest(RuleConfigTest, AttrTest):

    KEY_ATTR = "id_env"
    CODE_ERROR_ENVIRONMENT_NOT_FOUND = CodeError.ENVIRONMENT_NOT_FOUND

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_save_letter(self):
        self.save_attr_letter()

    def test_save_negative(self):
        self.save_attr_negative()

    def test_save_zero(self):
        self.save_attr_zero()

    def test_save_nonexistent(self):
        mock = self._attr_nonexistent()
        response = self.save({self.XML_KEY: mock})
        self._not_found(response, self.CODE_ERROR_ENVIRONMENT_NOT_FOUND)

    def test_update_empty(self):
        self.alter_attr_invalid(self.EMPTY_ATTR)

    def test_update_none(self):
        self.alter_attr_invalid(self.NONE_ATTR)

    def test_update_letter(self):
        self.alter_attr_invalid(self.LETTER_ATTR)

    def test_update_negative(self):
        self.alter_attr_invalid(self.NEGATIVE_ATTR)

    def test_update_zero(self):
        self.alter_attr_invalid(self.ZERO_ATTR)

    def test_update_nonexistent(self):
        mock = self._attr_nonexistent()
        response = self.save({self.XML_KEY: mock})
        self._not_found(response, self.CODE_ERROR_ENVIRONMENT_NOT_FOUND)


class RuleAttrNameTest(RuleConfigTest, AttrTest):

    KEY_ATTR = "name"

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_save_max_length(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(self.NAME_MAX_LENGTH + 1)
        self.process_save_attr_invalid(mock)

    def test_update_empty(self):
        self.alter_attr_invalid(self.EMPTY_ATTR)

    def test_update_none(self):
        self.alter_attr_invalid(self.NONE_ATTR)

    def test_update_max_length(self):
        self.alter_attr_invalid(string_generator(self.NAME_MAX_LENGTH + 1))


class RuleAttrBlocksTest(RuleConfigTest, AttrTest):

    KEY_ATTR = "blocks_id"

    def test_save_invalid_order(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = [1, 3, 2]
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_save_empty(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = [1, '', 2]
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_update_invalid_order(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = [1, 3, 2]
        response = self.client_autenticado().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_update_empty(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = [1, '', 2]
        response = self.client_autenticado().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        self._attr_invalid(response)


class RuleAttrContentsTest(RuleConfigTest, AttrTest):

    KEY_ATTR = "contents"

    def test_save_empty(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = ['content', '', 'content2']
        response = self.save({self.XML_KEY: mock})
        self._attr_invalid(response)

    def test_update_empty(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = ['content', '', 'content2']
        response = self.client_autenticado().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        self._attr_invalid(response)


class RuleAttrRuleIdTest(RuleConfigTest, AttrTest):

    KEY_ATTR = "id_rule"

    def test_alter_empty(self):
        self.alter_attr_invalid([self.EMPTY_ATTR, ])

    def test_alter_none(self):
        self.alter_attr_invalid([self.NONE_ATTR, ])

    def test_alter_letter(self):
        self.alter_attr_invalid([self.LETTER_ATTR, ])

    def test_alter_negative(self):
        self.alter_attr_invalid([self.NEGATIVE_ATTR, ])

    def test_alter_zero(self):
        self.alter_attr_invalid([self.ZERO_ATTR, ])

    def test_alter_nonexistent(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = [self.ID_INVALID_RULE, ]
        response = self.client_autenticado().putXML(
            self.URL_ALTER, {self.XML_KEY: mock})
        self._not_found(response, CodeError.RULE_NOT_FIND)


class RuleRemoveTest(RuleConfigTest, RemoveTest):

    def test_remove_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE % self.ID_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE % self.ID_REMOVE_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_rule_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.ID_NONEXISTENT)
        self._not_found(response, CodeError.RULE_NOT_FIND)

    def test_remove_rule_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_remove_rule_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_remove_rule_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_remove_rule_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.EMPTY_ATTR)
        self._attr_invalid(response)

    def test_remove_rule_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % self.NONE_ATTR)
        self._attr_invalid(response)
