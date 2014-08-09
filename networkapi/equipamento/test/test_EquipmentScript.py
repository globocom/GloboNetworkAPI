# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.usuario.models import Usuario
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class EquipmentScriptConfigTest(BasicTestCase):

    # Constants
    # 'networkapi/equipamento/fixtures/initial_data.yaml', 'networkapi/grupo/fixtures/initial_data.yaml',
    fixtures = ['networkapi/roteiro/fixtures/initial_data.yaml']
    XML_KEY = "equipment_script"
    ID_VALID = 1
    OBJ = EquipamentoRoteiro

    ID_EQUIPMENT = 1
    ID_SCRIPT = 1

    # Urls
    URL_SAVE = "/equipmentscript/"
    URL_REMOVE = "/equipmentscript/%s/%s/"
    URL_GET_ALL = "/equipmentscript/all/"
    URL_GET_BY_EQUIP_NAME = "/equipamentoroteiro/name/"

    def mock_valid(self):
        mock = {}
        mock['id_equipment'] = 2
        mock['id_script'] = 1
        return mock

    def dict_for_get_by_equip_name(self, name="Balanceador de Teste"):
        params = {}
        params['name'] = name
        return {"equipamento_roteiro": params}


class EquipmentScriptConsultationTest(EquipmentScriptConfigTest, ConsultationTest):

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "equipamento_roteiro", True)
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentScriptByEquipNameConsultationTest(EquipmentScriptConfigTest, ConsultationTest):

    def test_get_by_equip_name_valid(self):
        data = self.dict_for_get_by_equip_name()
        response = self.client_autenticado().postXML(
            self.URL_GET_BY_EQUIP_NAME, data)
        valid_response(response)
        content = valid_content(
            response, "equipamento_roteiro", force_list=True)

        # Verify
        user = Usuario.get_by_user('TEST')
        from_db = EquipamentoRoteiro.objects.filter(equipamento__nome__iexact="Balanceador de Teste", equipamento__grupos__direitosgrupoequipamento__ugrupo__in=user.grupos.all(
        ), equipamento__grupos__direitosgrupoequipamento__escrita='1')
        assert len(from_db) == len(content)

    def test_get_by_equip_name_no_permission(self):
        data = self.dict_for_get_by_equip_name()
        response = self.client_no_permission().postXML(
            self.URL_GET_BY_EQUIP_NAME, data)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equip_name_no_read_permission(self):
        data = self.dict_for_get_by_equip_name()
        response = self.client_no_read_permission().postXML(
            self.URL_GET_BY_EQUIP_NAME, data)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equip_name_invalid(self):
        data = self.dict_for_get_by_equip_name(string_generator(25))
        response = self.client_autenticado().postXML(
            self.URL_GET_BY_EQUIP_NAME, data)
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_get_by_equip_name_none(self):
        data = self.dict_for_get_by_equip_name(None)
        response = self.client_autenticado().postXML(
            self.URL_GET_BY_EQUIP_NAME, data)
        self._attr_invalid(response)

    def test_get_by_equip_name_empty(self):
        data = self.dict_for_get_by_equip_name("")
        response = self.client_autenticado().postXML(
            self.URL_GET_BY_EQUIP_NAME, data)
        self._attr_invalid(response)


class EquipmentScriptTest(EquipmentScriptConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        valid_content(response, "equipamento_roteiro")

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentScriptAttrEquipmentTest(EquipmentScriptConfigTest, AttrTest):

    KEY_ATTR = "id_equipment"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

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


class EquipmentScriptAttrScripttTest(EquipmentScriptConfigTest, AttrTest):

    KEY_ATTR = "id_script"
    CODE_ERROR_NOT_FOUND = CodeError.SCRIPT_NOT_FOUND

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


class EquipmentScriptRemoveTest(EquipmentScriptConfigTest, RemoveTest):

    def test_remove_valid(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_SCRIPT))
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.client_no_permission().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_SCRIPT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.client_no_write_permission().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_SCRIPT))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_equipment_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_NONEXISTENT, self.ID_SCRIPT))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_equipment_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.NEGATIVE_ATTR, self.ID_SCRIPT))
        self._attr_invalid(response)

    def test_remove_equipment_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.LETTER_ATTR, self.ID_SCRIPT))
        self._attr_invalid(response)

    def test_remove_equipment_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ZERO_ATTR, self.ID_SCRIPT))
        self._attr_invalid(response)

    def test_remove_equipment_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.EMPTY_ATTR, self.ID_SCRIPT))
        self._attr_invalid(response)

    def test_remove_equipment_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.NONE_ATTR, self.ID_SCRIPT))
        self._attr_invalid(response)

    def test_remove_script_nonexistent(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.SCRIPT_NOT_FOUND)

    def test_remove_script_negative(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_remove_script_letter(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_remove_script_zero(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_remove_script_empty(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.EMPTY_ATTR))
        self._attr_invalid(response)

    def test_remove_script_none(self):
        response = self.client_autenticado().delete(
            self.URL_REMOVE % (self.ID_EQUIPMENT, self.NONE_ATTR))
        self._attr_invalid(response)
