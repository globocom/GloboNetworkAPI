# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.grupo.models import EGrupo
from django.forms.models import model_to_dict
from networkapi.test import BasicTestCase, RemoveTest, AttrTest, CodeError, ConsultationTest,CLIENT_TYPES, me
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib

class EquipmentGroupConfigTest(BasicTestCase):

    #Constants
    fixtures = ['networkapi/equipamento/fixtures/initial_data.yaml']
    XML_KEY = "grupo"
    XML_KEY_EGROUP = "group_equipament"
    XML_KEY_EGROUP_ASSOC = "equipamento_grupo"

    ID_VALID = 1
    ID_ALTER_VALID = 2
    ID_REMOVE_VALID = 3
    ID_EQUIPMENT_VALID = 1
    ID_REMOVE_EQUIPMENT_VALID = 1
    ID_REMOVE_EQUIPMENT_GROUP_VALID = 12

    OBJ = EGrupo

    #Urls
    URL_SAVE = "/egrupo/"
    URL_ALTER = "/egrupo/%s/"
    URL_REMOVE = "/egrupo/%s/"
    URL_GET_BY_ID = "/egroup/%s/"
    URL_GET_BY_EQUIPMENT_ID = "/egrupo/equip/%s/"
    URL_GET_ALL = "/egrupo/"
    URL_SAVE_EQUIPMENT_GROUP_ASSOC = "/equipamentogrupo/associa/"
    URL_REMOVE_EQUIPMENT_GROUP_ASSOC = "/egrupo/equipamento/%s/egrupo/%s/"

    def mock_valid(self):
        mock = {}
        mock['nome'] = "NovoGrupoValido"
        return mock

    def mock_valid_alter(self):
        mock = {}
        mock['nome'] = "GrupoValidoAlter"
        return mock

    def mock_assoc_valid(self):
        mock = {}
        mock['id_grupo'] = 11
        mock['id_equipamento'] = 1
        return mock

    def valid_attr(self, mock, obj):
        assert mock["nome"] == obj["nome"]


class EquipmentGroupTest(EquipmentGroupConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock })
        valid_response(response)
        valid_content(response, 'grupo')

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock }, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock }, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_valid_alter()
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY:mock})
        valid_response(response)
        egrp = EGrupo.get_by_pk(self.ID_ALTER_VALID)
        self.valid_attr(mock, model_to_dict(egrp))

    def test_alter_no_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY:mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY:mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentGroupAttrEquipmentGroupTest(EquipmentGroupConfigTest, AttrTest):

    KEY_ATTR = "id_grupo"
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_NOT_FOUND

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


class EquipmentGroupAttrNameTest(EquipmentGroupConfigTest, AttrTest):

    KEY_ATTR = "nome"
    
    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_save_attr_invalid(mock)
    
    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):    
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)
    
    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


class EquipmentGroupTestEquipmentGroup(EquipmentGroupConfigTest):

    def test_save_valid(self):
        mock = self.mock_assoc_valid()
        response = self.client_autenticado().postXML(self.URL_SAVE_EQUIPMENT_GROUP_ASSOC, {self.XML_KEY_EGROUP_ASSOC:mock})
        valid_response(response)
        valid_content(response, 'grupo')

    def test_save_no_permission(self):
        mock = self.mock_assoc_valid()
        response = self.client_no_permission().postXML(self.URL_SAVE_EQUIPMENT_GROUP_ASSOC, {self.XML_KEY_EGROUP_ASSOC:mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_assoc_valid()
        response = self.client_no_write_permission().postXML(self.URL_SAVE_EQUIPMENT_GROUP_ASSOC, {self.XML_KEY_EGROUP_ASSOC:mock})
        valid_response(response, httplib.PAYMENT_REQUIRED)


class EquipmentGroupConsultationTest(EquipmentGroupConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_NOT_FOUND

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
        valid_content(response, self.XML_KEY_EGROUP)

    def test_get_by_id_no_permission(self):
        response = self.get_by_id(self.ID_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.get_by_id(self.ID_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
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


class EquipmentGroupConsultationEquipmentTest(EquipmentGroupConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_NOT_FOUND

    def test_get_by_equipment_id_valid(self):
        response = self.client_autenticado().get(self.URL_GET_BY_EQUIPMENT_ID % self.ID_EQUIPMENT_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY, True)

    def test_get_by_equipment_id_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_BY_EQUIPMENT_ID % self.ID_EQUIPMENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_id_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_BY_EQUIPMENT_ID % self.ID_EQUIPMENT_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_equipment_id_nonexistent(self):
        response = self.client_autenticado().get(self.URL_GET_BY_EQUIPMENT_ID % self.ID_NONEXISTENT)
        self._not_found(response)

    def test_get_by_equipment_id_negative(self):
        response = self.client_autenticado().get(self.URL_GET_BY_EQUIPMENT_ID % self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_id_letter(self):
        response = self.client_autenticado().get(self.URL_GET_BY_EQUIPMENT_ID % self.LETTER_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_id_zero(self):
        response = self.client_autenticado().get(self.URL_GET_BY_EQUIPMENT_ID % self.ZERO_ATTR)
        self._attr_invalid(response)

    def test_get_by_equipment_id_empty(self):
        response = self.client_autenticado().get(self.URL_GET_BY_EQUIPMENT_ID % self.EMPTY_ATTR)
        self._attr_invalid(response)


class EquipmentGroupRemoveTest(EquipmentGroupConfigTest, RemoveTest):
    
    CODE_ERROR_NOT_FOUND = CodeError.EQUIPMENT_GROUP_NOT_FOUND
    
    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(self.ID_REMOVE_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no_write_permission(self):
        response = self.remove(self.ID_REMOVE_VALID, CLIENT_TYPES.NO_WRITE_PERMISSION)
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


class EquipmentGroupRemoveAssocTest(EquipmentGroupConfigTest, ConsultationTest):

    def test_remove_equipment_valid(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        valid_response(response)

    def test_remove_equipment_no_permission(self):
        response = self.client_no_permission().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_equipment_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_equipment_nonexistent(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_NONEXISTENT, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        self._not_found(response, CodeError.EQUIPMENT_NOT_FOUND)

    def test_remove_equipment_negative(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.NEGATIVE_ATTR, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_letter(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.LETTER_ATTR, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_zero(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ZERO_ATTR, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_empty(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.EMPTY_ATTR, self.ID_REMOVE_EQUIPMENT_GROUP_VALID))
        self._attr_invalid(response)

    def test_remove_equipment_group_nonexistent(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.ID_NONEXISTENT))
        self._not_found(response, CodeError.EQUIPMENT_GROUP_NOT_FOUND)

    def test_remove_equipment_group_negative(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.NEGATIVE_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_group_letter(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.LETTER_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_group_zero(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.ZERO_ATTR))
        self._attr_invalid(response)

    def test_remove_equipment_group_empty(self):
        response = self.client_autenticado().get(self.URL_REMOVE_EQUIPMENT_GROUP_ASSOC % (self.ID_REMOVE_EQUIPMENT_VALID, self.EMPTY_ATTR))
        self._attr_invalid(response)