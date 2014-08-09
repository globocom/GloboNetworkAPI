# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.requisicaovips.models import OptionVip
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib
from networkapi.test.assertions import assert_response_error


class OptionVipConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/requisicaovips/fixtures/initial_data.yaml']
    XML_KEY = "option_vip"
    ID_VALID = 1
    ID_ALTER_VALID = 2
    ID_REMOVE_VALID = 3

    ID_OPTION_VIP_FOR_ASSOCIATION = 4
    ID_OPTION_VIP_FOR_DISSOCIATION = 5

    OBJ = OptionVip

    ID_ENV_VIP_VALID = 1
    ID_ENV_VIP_FOR_ASSOCIATION = 1
    ID_ENV_VIP_FOR_DISSOCIATION = 1

    # Urls
    URL_SAVE = "/optionvip/"
    URL_ALTER = "/optionvip/%s/"
    URL_REMOVE = "/optionvip/%s/"
    URL_GET_BY_ID = "/optionvip/%s/"
    URL_GET_ALL = "/optionvip/all/"
    URL_GET_BY_ENV_VIP = "/optionvip/environmentvip/%s/"
    URL_ASSOCIATE = "/optionvip/%s/environmentvip/%s/"
    URL_DISSOCIATE = "/optionvip/%s/environmentvip/%s/"
    URL_GET_TIMEOUT = "/environment-vip/get/timeout/%s/"
    URL_GET_CACHE_GROUP = "/environment-vip/get/grupo-cache/%s/"
    URL_GET_BALANCING = "/environment-vip/get/balanceamento/%s/"
    URL_GET_PERSISTENCE = "/environment-vip/get/persistencia/%s/"
#    URL_GET_CACHE_GROUP = "/environment-vip/get/cache_group/%s/"
#    URL_GET_BALANCING = "/environment-vip/get/balancing/%s/"
#    URL_GET_PERSISTENCE = "/environment-vip/get/persistence/%s/"

    def mock_valid(self):
        mock = {}
        mock['tipo_opcao'] = "mock"
        mock['nome_opcao_txt'] = "mock"
#        mock['option_type'] = "mock"
#        mock['option_name_txt'] = "mock"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["tipo_opcao"] == obj["tipo_opcao"]
        assert mock["nome_opcao_txt"] == obj["nome_opcao_txt"]
#        assert mock["option_type"] == obj["option_type"]
#        assert mock["option_name_txt"] == obj["option_name_txt"]

    def get_type_by_env_vip(self, id_env_vip, client_type=CLIENT_TYPES.TEST, type_url=None):
        client = self.switch(client_type)
        if type_url is None:
            response = client.get(self.URL_GET_BY_ENV_VIP % id_env_vip)
        else:
            response = client.get(type_url % id_env_vip)
        return response

    def get_by_env_vip(self, id_env_vip, client_type=CLIENT_TYPES.TEST):
        return self.get_type_by_env_vip(id_env_vip, client_type)

    def get_timeout_by_env_vip(self, id_env_vip, client_type=CLIENT_TYPES.TEST):
        return self.get_type_by_env_vip(id_env_vip, client_type, self.URL_GET_TIMEOUT)

    def get_group_cache_by_env_vip(self, id_env_vip, client_type=CLIENT_TYPES.TEST):
        return self.get_type_by_env_vip(id_env_vip, client_type, self.URL_GET_CACHE_GROUP)

    def get_balancing_by_env_vip(self, id_env_vip, client_type=CLIENT_TYPES.TEST):
        return self.get_type_by_env_vip(id_env_vip, client_type, self.URL_GET_BALANCING)

    def get_persistence_by_env_vip(self, id_env_vip, client_type=CLIENT_TYPES.TEST):
        return self.get_type_by_env_vip(id_env_vip, client_type, self.URL_GET_PERSISTENCE)


class OptionVipConsultationTest(OptionVipConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.OPTION_VIP_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
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
        valid_content(response, self.XML_KEY)

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


class OptionVipGetByEnvVipTest(OptionVipConfigTest, ConsultationTest):

    # Get by environment vip

    def test_get_by_env_vip_valid(self):
        response = self.get_by_env_vip(self.ID_ENV_VIP_VALID)
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        assert len(content) == len(self.OBJ.objects.select_related().filter(
            optionvipenvironmentvip__environment=self.ID_ENV_VIP_VALID))

    def test_get_by_env_vip_no_permission(self):
        response = self.get_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_env_vip_no_read_permission(self):
        response = self.get_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_env_vip_nonexistent(self):
        response = self.get_by_env_vip(self.ID_NONEXISTENT)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=CodeError.ENV_VIP_NOT_FOUND)

    def test_get_by_env_vip_negative(self):
        response = self.get_by_env_vip(self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_env_vip_letter(self):
        response = self.get_by_env_vip(self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_env_vip_zero(self):
        response = self.get_by_env_vip(self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_env_vip_empty(self):
        response = self.get_by_env_vip(self.EMPTY_ATTR)
        self._attr_invalid(response)


class OptionVipGetTimeoutByEnvVipTest(OptionVipConfigTest, ConsultationTest):

    # Get timeout option vips by environment vip

    def test_get_timeout_by_env_vip_valid(self):
        response = self.get_timeout_by_env_vip(self.ID_ENV_VIP_VALID)
        valid_response(response)
        content = valid_content(response, 'timeout_opt')
        assert len(content) == len(self.OBJ.objects.select_related().filter(
            tipo_opcao__icontains='timeout', optionvipenvironmentvip__environment=self.ID_ENV_VIP_VALID))

    def test_get_timeout_by_env_vip_no_permission(self):
        response = self.get_timeout_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_timeout_by_env_vip_no_read_permission(self):
        response = self.get_timeout_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_timeout_by_env_vip_nonexistent(self):
        response = self.get_timeout_by_env_vip(self.ID_NONEXISTENT)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=CodeError.ENV_VIP_NOT_FOUND)

    def test_get_timeout_by_env_vip_negative(self):
        response = self.get_timeout_by_env_vip(self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_timeout_by_env_vip_letter(self):
        response = self.get_timeout_by_env_vip(self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_timeout_by_env_vip_zero(self):
        response = self.get_timeout_by_env_vip(self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_timeout_by_env_vip_empty(self):
        response = self.get_timeout_by_env_vip(self.EMPTY_ATTR)
        self._attr_invalid(response)


class OptionVipGetGroupCacheByEnvVipTest(OptionVipConfigTest, ConsultationTest):

    # Get cache group option vips by environment vip

    def test_get_group_cache_by_env_vip_valid(self):
        response = self.get_group_cache_by_env_vip(self.ID_ENV_VIP_VALID)
        valid_response(response)
        content = valid_content(response, 'grupocache_opt')
        assert len(content) == len(self.OBJ.objects.select_related().filter(
            tipo_opcao__icontains='cache', optionvipenvironmentvip__environment=self.ID_ENV_VIP_VALID))

    def test_get_group_cache_by_env_vip_no_permission(self):
        response = self.get_group_cache_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_group_cache_by_env_vip_no_read_permission(self):
        response = self.get_group_cache_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_group_cache_by_env_vip_nonexistent(self):
        response = self.get_group_cache_by_env_vip(self.ID_NONEXISTENT)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=CodeError.ENV_VIP_NOT_FOUND)

    def test_get_group_cache_by_env_vip_negative(self):
        response = self.get_group_cache_by_env_vip(self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_group_cache_by_env_vip_letter(self):
        response = self.get_group_cache_by_env_vip(self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_group_cache_by_env_vip_zero(self):
        response = self.get_group_cache_by_env_vip(self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_group_cache_by_env_vip_empty(self):
        response = self.get_group_cache_by_env_vip(self.EMPTY_ATTR)
        self._attr_invalid(response)


class OptionVipGetBalancingByEnvVipTest(OptionVipConfigTest, ConsultationTest):

    # Get balancing option vips by environment vip

    def test_get_balancing_by_env_vip_valid(self):
        response = self.get_balancing_by_env_vip(self.ID_ENV_VIP_VALID)
        valid_response(response)
        content = valid_content(response, 'balanceamento_opt')
        assert len(content) == len(self.OBJ.objects.select_related().filter(
            tipo_opcao__icontains='balanceamento', optionvipenvironmentvip__environment=self.ID_ENV_VIP_VALID))

    def test_get_balancing_by_env_vip_no_permission(self):
        response = self.get_balancing_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_balancing_by_env_vip_no_read_permission(self):
        response = self.get_balancing_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_balancing_by_env_vip_nonexistent(self):
        response = self.get_balancing_by_env_vip(self.ID_NONEXISTENT)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=CodeError.ENV_VIP_NOT_FOUND)

    def test_get_balancing_by_env_vip_negative(self):
        response = self.get_balancing_by_env_vip(self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_balancing_by_env_vip_letter(self):
        response = self.get_balancing_by_env_vip(self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_balancing_by_env_vip_zero(self):
        response = self.get_balancing_by_env_vip(self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_balancing_by_env_vip_empty(self):
        response = self.get_balancing_by_env_vip(self.EMPTY_ATTR)
        self._attr_invalid(response)


class OptionVipGetPersistenceByEnvVipTest(OptionVipConfigTest, ConsultationTest):

    # Get persistence option vips by environment vip

    def test_get_persistence_by_env_vip_valid(self):
        response = self.get_persistence_by_env_vip(self.ID_ENV_VIP_VALID)
        valid_response(response)
        content = valid_content(response, 'persistencia_opt')
        assert len(content) == len(self.OBJ.objects.select_related().filter(
            tipo_opcao__icontains='persistencia', optionvipenvironmentvip__environment=self.ID_ENV_VIP_VALID))

    def test_get_persistence_by_env_vip_no_permission(self):
        response = self.get_persistence_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_persistence_by_env_vip_no_read_permission(self):
        response = self.get_persistence_by_env_vip(
            self.ID_ENV_VIP_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_persistence_by_env_vip_nonexistent(self):
        response = self.get_persistence_by_env_vip(self.ID_NONEXISTENT)
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=CodeError.ENV_VIP_NOT_FOUND)

    def test_get_persistence_by_env_vip_negative(self):
        response = self.get_persistence_by_env_vip(self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_persistence_by_env_vip_letter(self):
        response = self.get_persistence_by_env_vip(self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_persistence_by_env_vip_zero(self):
        response = self.get_persistence_by_env_vip(self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_persistence_by_env_vip_empty(self):
        response = self.get_persistence_by_env_vip(self.EMPTY_ATTR)
        self._attr_invalid(response)


class OptionVipTest(OptionVipConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, self.XML_KEY)

        response = self.get_by_id(content["id"])
        valid_response(response)
        ovip = valid_content(response, self.XML_KEY)

        self.valid_attr(mock, ovip)

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
        mock["tipo_opcao"] = "OptionVipAlter"
#        mock['option_type'] = "OptionVipAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_by_id(self.ID_ALTER_VALID)
        valid_response(response)
        ovip = valid_content(response, self.XML_KEY)

        self.valid_attr(mock, ovip)

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


class OptionVipRemoveTest(OptionVipConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.OPTION_VIP_NOT_FOUND

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


class OptionVipAttrOptionTypeTest(OptionVipConfigTest, AttrTest):

    KEY_ATTR = "tipo_opcao"
#    KEY_ATTR = "option_type"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(0)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(0)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class OptionVipAttrOptionNameTxtTest(OptionVipConfigTest, AttrTest):

    KEY_ATTR = "nome_opcao_txt"
#    KEY_ATTR = "option_name_txt"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(0)
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(0)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class OptionVipAssociateTest(OptionVipConfigTest, AttrTest):

    # Association between option vip and environment vip

    def test_associate_valid(self):
        response = self.client_autenticado().put(self.URL_ASSOCIATE % (
            self.ID_OPTION_VIP_FOR_ASSOCIATION, self.ID_ENV_VIP_FOR_ASSOCIATION))
        valid_response(response)
        valid_content(response, "opcoesvip_ambiente_xref")

        # Dissociate so it does not require cleaning db manually
        response = self.client_autenticado().delete(self.URL_DISSOCIATE %
                                                    (self.ID_OPTION_VIP_FOR_ASSOCIATION, self.ID_ENV_VIP_FOR_ASSOCIATION))
        valid_response(response)

    def test_associate_no_permission(self):
        response = self.client_no_permission().put(self.URL_ASSOCIATE % (
            self.ID_OPTION_VIP_FOR_ASSOCIATION, self.ID_ENV_VIP_FOR_ASSOCIATION))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_associate_no__write_permission(self):
        response = self.client_no_write_permission().put(self.URL_ASSOCIATE % (
            self.ID_OPTION_VIP_FOR_ASSOCIATION, self.ID_ENV_VIP_FOR_ASSOCIATION))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_associate_option_vip_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_NONEXISTENT, self.ID_ENV_VIP_FOR_ASSOCIATION))
        self._not_found(response, CodeError.OPTION_VIP_NOT_FOUND)

    def test_associate_option_vip_negative(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.NEGATIVE_ATTR, self.ID_ENV_VIP_FOR_ASSOCIATION))
        self._attr_invalid(response)

    def test_associate_option_vip_letter(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.LETTER_ATTR, self.ID_ENV_VIP_FOR_ASSOCIATION))
        self._attr_invalid(response)

    def test_associate_option_vip_zero(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ZERO_ATTR, self.ID_ENV_VIP_FOR_ASSOCIATION))
        self._attr_invalid(response)

    def test_associate_option_vip_empty(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.EMPTY_ATTR, self.ID_ENV_VIP_FOR_ASSOCIATION))
        self._attr_invalid(response)

    def test_associate_option_vip_none(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.NONE_ATTR, self.ID_ENV_VIP_FOR_ASSOCIATION))
        self._attr_invalid(response)

    def test_associate_env_vip_nonexistent(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_OPTION_VIP_FOR_ASSOCIATION, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_associate_env_vip_negative(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_OPTION_VIP_FOR_ASSOCIATION, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_associate_env_vip_letter(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_OPTION_VIP_FOR_ASSOCIATION, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_associate_env_vip_zero(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_OPTION_VIP_FOR_ASSOCIATION, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_associate_env_vip_empty(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_OPTION_VIP_FOR_ASSOCIATION, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_associate_env_vip_none(self):
        response = self.client_autenticado().put(
            self.URL_ASSOCIATE % (self.ID_OPTION_VIP_FOR_ASSOCIATION, self.NONE_ATTR))
        self._attr_invalid(response)


class OptionVipDissociateTest(OptionVipConfigTest, AttrTest):

    # Dissociation between option vip and environment vip

    def test_dissociate_valid(self):
        response = self.client_autenticado().delete(self.URL_DISSOCIATE % (
            self.ID_OPTION_VIP_FOR_DISSOCIATION, self.ID_ENV_VIP_FOR_DISSOCIATION))
        valid_response(response)

    def test_dissociate_no_permission(self):
        response = self.client_no_permission().delete(self.URL_DISSOCIATE % (
            self.ID_OPTION_VIP_FOR_DISSOCIATION, self.ID_ENV_VIP_FOR_DISSOCIATION))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_dissociate_no__write_permission(self):
        response = self.client_no_write_permission().delete(self.URL_DISSOCIATE % (
            self.ID_OPTION_VIP_FOR_DISSOCIATION, self.ID_ENV_VIP_FOR_DISSOCIATION))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_dissociate_option_vip_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_NONEXISTENT, self.ID_ENV_VIP_FOR_DISSOCIATION))
        self._not_found(response, CodeError.OPTION_VIP_NOT_FOUND)

    def test_dissociate_option_vip_negative(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.NEGATIVE_ATTR, self.ID_ENV_VIP_FOR_DISSOCIATION))
        self._attr_invalid(response)

    def test_dissociate_option_vip_letter(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.LETTER_ATTR, self.ID_ENV_VIP_FOR_DISSOCIATION))
        self._attr_invalid(response)

    def test_dissociate_option_vip_zero(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ZERO_ATTR, self.ID_ENV_VIP_FOR_DISSOCIATION))
        self._attr_invalid(response)

    def test_dissociate_option_vip_empty(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.EMPTY_ATTR, self.ID_ENV_VIP_FOR_DISSOCIATION))
        self._attr_invalid(response)

    def test_dissociate_option_vip_none(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.NONE_ATTR, self.ID_ENV_VIP_FOR_DISSOCIATION))
        self._attr_invalid(response)

    def test_dissociate_env_vip_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_OPTION_VIP_FOR_DISSOCIATION, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.ENV_VIP_NOT_FOUND)

    def test_dissociate_env_vip_negative(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_OPTION_VIP_FOR_DISSOCIATION, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_dissociate_env_vip_letter(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_OPTION_VIP_FOR_DISSOCIATION, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_dissociate_env_vip_zero(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_OPTION_VIP_FOR_DISSOCIATION, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_dissociate_env_vip_empty(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_OPTION_VIP_FOR_DISSOCIATION, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_dissociate_env_vip_none(self):
        response = self.client_autenticado().delete(
            self.URL_DISSOCIATE % (self.ID_OPTION_VIP_FOR_DISSOCIATION, self.NONE_ATTR))
        self._attr_invalid(response)
