# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.db.models import Q
from networkapi.ambiente.models import EnvironmentVip
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.test.utils import xml2dict
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, valid_get_filtered, string_generator
import httplib


class EnvironmentVipConfigTest(BasicTestCase):

    # Constants
    fixtures = [
        'networkapi/ambiente/fixtures/initial_data.yaml',
        'networkapi/requisicaovips/fixtures/initial_data.yaml']
    XML_KEY = "environment_vip"
    ID_VALID = 1
    ID_ALTER_VALID = 2
    ID_REMOVE_VALID = 3

    OBJ = EnvironmentVip

    ID_VALID_VIPS_ASSOCIATION = 1

    # Urls
    URL_SAVE = "/environmentvip/"
    URL_ALTER = "/environmentvip/%s/"
    URL_REMOVE = "/environmentvip/%s/"
    URL_SEARCH = "/environmentvip/search/"
    URL_GET_ALL = "/environmentvip/all/"
    URL_GET_VIPS_FROM_ENV_VIP = "/environmentvip/%s/vip/all/"
    URL_GET_FINALITY = "/environment-vip/get/finality/"
    URL_GET_CLIENT_BY_FINALITY = "/environment-vip/get/cliente_txt/"
    URL_GET_P44_BY_CLIENT_FINALITY = "/environment-vip/get/ambiente_p44_txt/"

    # Strings for search
    FINALITY_VALID = 'Finality_TXT'
    FINALITY_INEXISTENT = 'Finality_TXT_INEXISTENT'
    CLIENT_VALID = 'Client_TXT'
    CLIENT_INEXISTENT = 'Client_TXT_INEXISTENT'
    P44_ENV_VALID = 'PQuaQua_Environment_TXT'
    P44_ENV_INEXISTENT = 'PQuaQua_Environment_TXT_INEXISTENT'

    def mock_valid(self):
        mock = {}
        mock['finalidade_txt'] = "mock_finality"
        mock['cliente_txt'] = "mock_client"
        mock['ambiente_p44_txt'] = "mock_p_quaqua_environment"
#        mock['finality_txt'] = "mock_finality"
#        mock['client_txt'] = "mock_client"
#        mock['p44_environment_txt'] = "mock_pquaqua_environment"
        return mock

    def valid_attr(self, mock, obj):
        assert mock['finalidade_txt'] == obj['finalidade_txt']
        assert mock['cliente_txt'] == obj['cliente_txt']
        assert mock['ambiente_p44_txt'] == obj['ambiente_p44_txt']
#        assert mock['finality_txt'] == obj['finality_txt']
#        assert mock['client_txt'] == obj['client_txt']
#        assert mock['p44_environment_txt'] == obj['p44_environment_txt']

    def search(
            self,
            client=CLIENT_TYPES.TEST,
            id_env_vip=None,
            finality=None,
            client_txt=None,
            p44_env=None):

        client_api = self.switch(client)
        dict_ = dict()

        if id_env_vip is not None:
            dict_['id_environment_vip'] = id_env_vip
        if finality is not None:
            dict_['finalidade_txt'] = finality
        if client_txt is not None:
            dict_['cliente_txt'] = client_txt
        if p44_env is not None:
            dict_['ambiente_p44_txt'] = p44_env

        response = client_api.postXML(
            self.URL_SEARCH, {
                'environment_vip': dict_})
        return response

    def get_client_by_finality(self, client=CLIENT_TYPES.TEST, finality=None):

        client_api = self.switch(client)
        dict_ = dict()

        if finality is not None:
            dict_['finalidade_txt'] = finality

        response = client_api.postXML(
            self.URL_GET_CLIENT_BY_FINALITY, {
                'vip': dict_})
        return response

    def get_p44_by_client_finality(
            self,
            client=CLIENT_TYPES.TEST,
            finality=None,
            client_txt=None):

        client_api = self.switch(client)
        dict_ = dict()

        if finality is not None:
            dict_['finalidade_txt'] = finality
        if client_txt is not None:
            dict_['cliente_txt'] = client_txt

        response = client_api.postXML(
            self.URL_GET_P44_BY_CLIENT_FINALITY, {
                'vip': dict_})
        return response


class EnvironmentVipAllConsultationTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

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


class EnvironmentVipByIdConsultationTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

    def test_get_by_id_valid(self):
        response = self.search(id_env_vip=self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_id_no_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_PERMISSION,
            id_env_vip=self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_READ_PERMISSION,
            id_env_vip=self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_nonexistent(self):
        response = self.search(id_env_vip=self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_id_negative(self):
        response = self.search(id_env_vip=self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_id_letter(self):
        response = self.search(id_env_vip=self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_id_zero(self):
        response = self.search(id_env_vip=self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_id_empty(self):
        response = self.search(id_env_vip=self.EMPTY_ATTR)
        self._attr_invalid(response, code_error=287)


class EnvironmentVipAllFinalityConsultationTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    def test_get_all_finality(self):
        response = self.client_autenticado().get(self.URL_GET_FINALITY)
        valid_response(response)
        valid_content(response, 'finalidade')

    def test_get_all_finality_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_FINALITY)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_finality_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_FINALITY)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EnvironmentVipGetClientByFinalityConsultationTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    def test_get_client_by_finality_valid(self):
        response = self.get_client_by_finality(finality=self.FINALITY_VALID)
        valid_response(response)
        valid_content(response, 'cliente_txt')

    def test_get_client_by_finality_no_permission(self):
        response = self.get_client_by_finality(
            client=CLIENT_TYPES.NO_PERMISSION,
            finality=self.FINALITY_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_client_by_finality_no_read_permission(self):
        response = self.get_client_by_finality(
            client=CLIENT_TYPES.NO_READ_PERMISSION,
            finality=self.FINALITY_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_client_by_finality_nonexistent(self):
        response = self.get_client_by_finality(
            finality=self.FINALITY_INEXISTENT)
        valid_response(response)
        assert xml2dict(response.content)['cliente_txt'] is None

    def test_get_client_by_finality_negative(self):
        response = self.get_client_by_finality(finality=self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_client_by_finality_empty(self):
        response = self.get_client_by_finality(finality=self.EMPTY_ATTR)
        self._attr_invalid(response)


class EnvironmentVipGetP44ByClientFinalityConsultationTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    def test_get_p44_by_client_finality_valid(self):
        response = self.get_p44_by_client_finality(
            finality=self.FINALITY_VALID,
            client_txt=self.CLIENT_VALID)
        valid_response(response)
        valid_content(response, 'ambiente_p44')

    def test_get_p44_by_client_finality_no_permission(self):
        response = self.get_p44_by_client_finality(
            client=CLIENT_TYPES.NO_PERMISSION,
            finality=self.FINALITY_VALID,
            client_txt=self.CLIENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_p44_by_client_finality_no_read_permission(self):
        response = self.get_p44_by_client_finality(
            client=CLIENT_TYPES.NO_READ_PERMISSION,
            finality=self.FINALITY_VALID,
            client_txt=self.CLIENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_p44_by_client_finality_nonexistent(self):
        response = self.get_p44_by_client_finality(
            finality=self.FINALITY_INEXISTENT,
            client_txt=self.CLIENT_VALID)
        valid_response(response)
        assert xml2dict(response.content)['ambiente_p44'] is None

    def test_get_p44_by_client_nonexistent_finality(self):
        response = self.get_p44_by_client_finality(
            finality=self.FINALITY_VALID,
            client_txt=self.CLIENT_INEXISTENT)
        valid_response(response)
        assert xml2dict(response.content)['ambiente_p44'] is None

    def test_get_p44_by_client_finality_negative(self):
        response = self.get_p44_by_client_finality(
            finality=self.NEGATIVE_ATTR,
            client_txt=self.CLIENT_VALID)
        self._attr_invalid(response)

    def test_get_p44_by_client_negative_finality(self):
        response = self.get_p44_by_client_finality(
            finality=self.FINALITY_VALID,
            client_txt=self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_p44_by_client_finality_empty(self):
        response = self.get_p44_by_client_finality(
            finality=self.EMPTY_ATTR,
            client_txt=self.CLIENT_VALID)
        self._attr_invalid(response)

    def test_get_p44_by_client_empty_finality(self):
        response = self.get_p44_by_client_finality(
            finality=self.FINALITY_VALID,
            client_txt=self.EMPTY_ATTR)
        self._attr_invalid(response)


class EnvironmentVipGetVipsByEnvIdConsultationTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

    @me
    def test_get_vips_by_env_id_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.ID_VALID_VIPS_ASSOCIATION)
        valid_response(response)
        content = valid_content(response)
        query = Q(
            ip__networkipv4__ambient_vip__id=self.ID_VALID_VIPS_ASSOCIATION) | Q(
            ipv6__networkipv6__ambient_vip__id=self.ID_VALID_VIPS_ASSOCIATION)
        valid_get_filtered(content, RequisicaoVips, query)

    def test_get_vips_by_env_id_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.ID_VALID_VIPS_ASSOCIATION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_vips_by_env_id_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.ID_VALID_VIPS_ASSOCIATION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_vips_by_env_id_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_vips_by_env_id_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_vips_by_env_id_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_vips_by_env_id_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_vips_by_env_id_empty(self):
        response = self.client_autenticado().get(
            self.URL_GET_VIPS_FROM_ENV_VIP %
            self.EMPTY_ATTR)
        self._attr_invalid(response)


class EnvironmentVipSearchByFinalityTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

    def test_get_by_finality_valid(self):
        response = self.search(finality=self.FINALITY_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_finality_no_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_PERMISSION,
            finality=self.FINALITY_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_finality_no_read_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_READ_PERMISSION,
            finality=self.FINALITY_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_finality_nonexistent(self):
        response = self.search(finality=self.FINALITY_INEXISTENT)
        valid_response(response)
        assert xml2dict(response.content)['environment_vip'] is None

    def test_get_by_finality_empty(self):
        response = self.search(finality=self.EMPTY_ATTR)
        self._attr_invalid(response, code_error=287)


class EnvironmentVipSearchByClientTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

    def test_get_by_client_valid(self):
        response = self.search(client_txt=self.CLIENT_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_client_no_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_PERMISSION,
            client_txt=self.CLIENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_client_no_read_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_READ_PERMISSION,
            client_txt=self.CLIENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_client_nonexistent(self):
        response = self.search(client_txt=self.CLIENT_INEXISTENT)
        valid_response(response)
        assert xml2dict(response.content)['environment_vip'] is None

    def test_get_by_client_empty(self):
        response = self.search(client_txt=self.EMPTY_ATTR)
        self._attr_invalid(response, code_error=287)


class EnvironmentVipSearchByP44EnvTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

    def test_get_by_p44_env_valid(self):
        response = self.search(p44_env=self.P44_ENV_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_p44_env_no_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_PERMISSION,
            p44_env=self.P44_ENV_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_p44_env_no_read_permission(self):
        response = self.search(
            client=CLIENT_TYPES.NO_READ_PERMISSION,
            p44_env=self.P44_ENV_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_p44_env_nonexistent(self):
        response = self.search(p44_env=self.P44_ENV_INEXISTENT)
        valid_response(response)
        assert xml2dict(response.content)['environment_vip'] is None

    def test_get_by_p44_env_empty(self):
        response = self.search(p44_env=self.EMPTY_ATTR)
        self._attr_invalid(response, code_error=287)


class EnvironmentVipCombinedSearchTest(
        EnvironmentVipConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

    def test_get_by_finality_client_and_p44_env_valid(self):
        response = self.search(
            finality=self.FINALITY_VALID,
            client_txt=self.CLIENT_VALID,
            p44_env=self.P44_ENV_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_finality_client_valid_p44_env_invalid(self):
        response = self.search(
            finality=self.FINALITY_VALID,
            client_txt=self.CLIENT_VALID,
            p44_env=self.P44_ENV_INEXISTENT)
        valid_response(response)
        assert xml2dict(response.content)['environment_vip'] is None

    # Id have priority, client is ignored
    def test_get_by_id_valid_client_invalid(self):
        response = self.search(
            id_env_vip=self.ID_VALID,
            client_txt=self.CLIENT_INEXISTENT)
        valid_response(response)
        valid_content(response, self.XML_KEY)


class EnvironmentVipTest(EnvironmentVipConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, self.XML_KEY)

        response = self.search(id_env_vip=content['id'])
        valid_response(response)
        env_vip = valid_content(response, self.XML_KEY)
        self.valid_attr(mock, env_vip)

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
        mock["finalidade_txt"] = "EnvironmentVipAlter"
#        mock['finality_txt'] = "EnvironmentVipAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.search(id_env_vip=self.ID_ALTER_VALID)
        valid_response(response)
        env_vip = valid_content(response, self.XML_KEY)
        self.valid_attr(mock, env_vip)

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


class EnvironmentVipRemoveTest(EnvironmentVipConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.ENV_VIP_NOT_FOUND

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


class EnvironmentVipAttrFinalityTest(EnvironmentVipConfigTest, AttrTest):

    KEY_ATTR = "finalidade_txt"
#    KEY_ATTR = "finality_txt"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
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
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class EnvironmentVipAttrClientTest(EnvironmentVipConfigTest, AttrTest):

    KEY_ATTR = "cliente_txt"
#    KEY_ATTR = "client_txt"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
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
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class EnvironmentVipAttrP44EnvTest(EnvironmentVipConfigTest, AttrTest):

    KEY_ATTR = "ambiente_p44_txt"
#    KEY_ATTR = "p44_environment_txt"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(51)
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
        mock[self.KEY_ATTR] = string_generator(51)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)
