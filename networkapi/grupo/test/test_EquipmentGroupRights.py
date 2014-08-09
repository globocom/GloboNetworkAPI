# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.grupo.models import EGrupo, DireitosGrupoEquipamento
from django.forms.models import model_to_dict
from networkapi.test import BasicTestCase, RemoveTest, AttrTest, CodeError, ConsultationTest, CLIENT_TYPES, me
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class EquipmentGroupRightsConfigTest(BasicTestCase):

    # Constants
    fixtures = [
        'networkapi/equipamento/fixtures/initial_data.yaml',
        'networkapi/grupo/fixtures/initial_data.yaml']
    XML_KEY = "direito_grupo_equipamento"

    OBJ = DireitosGrupoEquipamento

    ID_VALID = 1
    ID_ALTER_VALID = 3
    ID_REMOVE_VALID = 4
    ID_USER_GROUP_VALID = 1
    ID_EQUIPMENT_GROUP_VALID = 1

    # Urls
    URL_SAVE = "/direitosgrupoequipamento/"
    URL_ALTER = "/direitosgrupoequipamento/%s/"
    URL_REMOVE = "/direitosgrupoequipamento/%s/"
    URL_GET_BY_ID = "/direitosgrupoequipamento/%s/"
    URL_GET_ALL = "/direitosgrupoequipamento/"
    URL_GET_BY_USER_GROUP = "/direitosgrupoequipamento/ugrupo/%s/"
    URL_GET_BY_EQUIPMENT_GROUP = "/direitosgrupoequipamento/egrupo/%s/"

    def mock_valid(self):
        mock = {}
        mock["id_grupo_usuario"] = 1
        mock["id_grupo_equipamento"] = 10
        mock["leitura"] = "1"
        mock["escrita"] = "1"
        mock["alterar_config"] = "1"
        mock["exclusao"] = "1"
        return mock

    def mock_valid_alter(self):
        mock = {}
        mock["leitura"] = "1"
        mock["escrita"] = "0"
        mock["alterar_config"] = "1"
        mock["exclusao"] = "0"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["leitura"] == obj["leitura"]
        assert mock["escrita"] == obj["escrita"]
        assert mock["alterar_config"] == obj["alterar_config"]
        assert mock["exclusao"] == obj["exclusao"]


class EquipmentGroupRightsTest(EquipmentGroupRightsConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, self.XML_KEY)

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
        mock = self.mock_valid_alter()
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)
        equip_group_right = DireitosGrupoEquipamento.get_by_pk(
            self.ID_ALTER_VALID)
        self.valid_attr(mock, model_to_dict(equip_group_right))

    def test_alter_no_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(
            self.ID_ALTER_VALID, {
                self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(
            self.ID_ALTER_VALID, {
                self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentGroupRightsAttrEquipmentGroupRightsTest(
        EquipmentGroupRightsConfigTest,
        AttrTest):

    KEY_ATTR = "id_direito"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_RIGHTS_NOT_FOUND

    def test_alter_nonexistent(self):
        self.alter_attr_nonexistent(self.ID_NONEXISTENT)

    def test_alter_negative(self):
        self.alter_attr_negative(self.NEGATIVE_ATTR)

    def test_alter_letter(self):
        self.alter_attr_letter(self.LETTER_ATTR)

    def test_alter_zero(self):
        self.alter_attr_zero(self.ZERO_ATTR)

    def test_alter_empty(self):
        self.alter_attr_empty(self.EMPTY_ATTR)

    def test_alter_none(self):
        self.alter_attr_none(self.NONE_ATTR)


class EquipmentGroupRightsAttrLeituraTest(
        EquipmentGroupRightsConfigTest,
        AttrTest):

    KEY_ATTR = "leitura"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'S'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'N'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'S'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'N'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_none(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)


class EquipmentGroupRightsAttrEscritaTest(
        EquipmentGroupRightsConfigTest,
        AttrTest):

    KEY_ATTR = "escrita"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'S'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'N'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'S'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'N'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_none(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)


class EquipmentGroupRightsAttrAlterarConfigTest(
        EquipmentGroupRightsConfigTest,
        AttrTest):

    KEY_ATTR = "alterar_config"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'S'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'N'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'S'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'N'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_none(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)


class EquipmentGroupRightsAttrExclusaoTest(
        EquipmentGroupRightsConfigTest,
        AttrTest):

    KEY_ATTR = "exclusao"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'S'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'N'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'S'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'N'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_none(self):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = self.NONE_ATTR
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)


class EquipmentGroupRightsConsultationTest(
        EquipmentGroupRightsConfigTest,
        ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_RIGHTS_NOT_FOUND

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
            self.ID_VALID,
            CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_get_by_id_negative(self):
        self.get_by_id_negative()

    def test_get_by_id_letter(self):
        self.get_by_id_letter()

    def test_get_by_id_zero(self):
        self.get_by_id_zero()


class EquipmentGroupRightsConsultationEquipmentGroupRightsTest(
        EquipmentGroupRightsConfigTest,
        ConsultationTest):

    def test_get_by_user_group_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_USER_GROUP %
            self.ID_USER_GROUP_VALID)
        valid_response(response)

    def test_get_by_user_group_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_USER_GROUP %
            self.ID_USER_GROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_user_group_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_USER_GROUP %
            self.ID_USER_GROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_group_valid(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIPMENT_GROUP %
            self.ID_EQUIPMENT_GROUP_VALID)
        valid_response(response)

    def test_get_by_equipment_group_no_permission(self):
        response = self.client_no_permission().get(
            self.URL_GET_BY_EQUIPMENT_GROUP %
            self.ID_EQUIPMENT_GROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_group_no_read_permission(self):
        response = self.client_no_read_permission().get(
            self.URL_GET_BY_EQUIPMENT_GROUP %
            self.ID_EQUIPMENT_GROUP_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_user_group_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_USER_GROUP %
            self.ID_NONEXISTENT)
        self._not_found(response, CodeError.UGROUP_NOT_FOUND)

    def test_get_by_user_group_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_USER_GROUP %
            self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_user_group_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_USER_GROUP %
            self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_user_group_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_USER_GROUP %
            self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_group_nonexistent(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIPMENT_GROUP %
            self.ID_NONEXISTENT)
        self._not_found(response, CodeError.EQUIPMENT_GROUP_NOT_FOUND)

    def test_get_by_equipment_group_negative(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIPMENT_GROUP %
            self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_group_letter(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIPMENT_GROUP %
            self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_group_zero(self):
        response = self.client_autenticado().get(
            self.URL_GET_BY_EQUIPMENT_GROUP %
            self.ZERO_ATTR)
        self._attr_invalid(response)


class EquipmentGroupRightsRemoveTest(
        EquipmentGroupRightsConfigTest,
        RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_RIGHTS_NOT_FOUND

    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID,
            CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
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
