# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.db.models import Q
from networkapi.equipamento.models import Modelo
from networkapi.test import BasicTestCase, CodeError, ConsultationTest, me, RemoveTest, AttrTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator, valid_get_filtered
import httplib

class ModelConfigTest(BasicTestCase):
        
    #Constants
    fixtures = ['networkapi/equipamento/fixtures/initial_data.yaml']
    XML_KEY = "model"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    OBJ = Modelo
    
    #Urls
    URL_SAVE = "/model/"
    URL_ALTER = "/model/%s/"
    URL_REMOVE = "/model/%s/"
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/model/all/"
    URL_GET_BRAND = "/model/brand/%s/"
    
    def mock_valid(self):
        mock = {}
        mock['name'] = 'mock'
        mock['id_brand'] = 1
        return mock
    
    def valid_attr(self, mock, obj):
        assert mock["name"] == obj["nome"]
        assert mock["id_brand"] == int(obj["id_marca"])

class ModelConsultationTest(ModelConfigTest, ConsultationTest):
    
    CODE_ERROR_NOT_FOUND = CodeError.MODEL_NOT_FOUND
    
    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "model")
        valid_get_all(content, self.OBJ) 
        
    def test_get_all_inactive(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response,httplib.UNAUTHORIZED)
    
    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

class ModelTest(ModelConfigTest): 
    
    """
    @todo:  fazer o teste para unico com os dois campos
    """
    
    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock })
        valid_response(response)
        model = valid_content(response, "model")
        
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "model")
        
        for mdl in content:
            if mdl["id"] == model["id"]:
                self.valid_attr(mock, mdl)
                break
            
    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock }, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock }, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)
        
    def test_alter_valid(self):
        mock = self.mock_valid()
        mock["name"] = "ModelAlter"
        response = self.alter(self.ID_ALTER_VALID, { self.XML_KEY : mock })
        valid_response(response)
        
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "model")

        for mdl in content:
            if mdl["id"] == self.ID_ALTER_VALID:
                self.valid_attr(mock, mdl)
                break

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(self.ID_ALTER_VALID, { self.XML_KEY : mock }, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(self.ID_ALTER_VALID, { self.XML_KEY : mock }, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

class ModelRemoveTest(ModelConfigTest, RemoveTest):
    
    CODE_ERROR_NOT_FOUND = CodeError.MODEL_NOT_FOUND
          
    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)
        
    def test_remove_no_permission(self):
        response = self.remove(self.ID_REMOVE_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
        response = self.remove(self.ID_REMOVE_VALID, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)
        
    def test_remove_script_related(self):
        response = self.remove(self.ID_VALID)
        self._attr_invalid(response, CodeError.MODEL_EQUIPMENT_RELATED)
    
    def test_remove_by_id_nonexistent(self):
        self.remove_nonexistent()
    
    def test_remove_by_id_negative(self):
        self.remove_negative()
    
    def test_remove_by_id_letter(self):
        self.remove_letter()
    
    def test_remove_by_id_zero(self):
        self.remove_zero()
    
    def test_remove_by_id_empty(self):
        self.remove_empty()        

class ModelAttrNameTest(ModelConfigTest, AttrTest):

    KEY_ATTR = "name"
    
    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_save_attr_invalid(mock)
    
    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)
        
    def test_save_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "model")
        model = content[0]
        mock = self.mock_valid()
        mock["name"] = model["nome"]
        self.process_save_attr_invalid(mock, CodeError.MODEL_DUPLICATE)
        
    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()
    
    def test_alter_maxsize(self):    
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)
    
    def test_alter_minsize(self):    
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)
        
    def test_alter_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "model")
        model = content[0]
        mock = self.mock_valid()
        mock["name"] = model["nome"]
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock, CodeError.MODEL_DUPLICATE)
    
    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)

class ModelAttrBrandTest(ModelConfigTest, AttrTest):
    
    KEY_ATTR = "id_brand"
    CODE_ERROR_NOT_FOUND = CodeError.BRAND_NOT_FOUND
    
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
        
    def test_alter_nonexistent(self):
        self.alter_attr_nonexistent(self.ID_ALTER_VALID)
    
    def test_alter_negative(self):
        self.alter_attr_negative(self.ID_ALTER_VALID)        

    def test_alter_letter(self):
        self.alter_attr_letter(self.ID_ALTER_VALID)
        
    def test_alter_zero(self):
        self.alter_attr_zero(self.ID_ALTER_VALID)
        
    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)

class ModelConsultationBrandTest(ModelConfigTest, AttrTest):
    
    CODE_ERROR_NOT_FOUND = CodeError.BRAND_NOT_FOUND

    def test_get_by_brand(self):
        response = self.client_autenticado().get(self.URL_GET_BRAND % self.ID_VALID )
        valid_response(response)
        content = valid_content(response, "model", True)
        
        query = Q(marca__id=self.ID_VALID)
        valid_get_filtered(content, Modelo, query)
        
    def test_get_by_brand_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_BRAND % self.ID_VALID )
        valid_response(response, httplib.PAYMENT_REQUIRED)
        
    def test_get_by_brand_no_read_permission(self):
        response = self.client_no_read_permission().get(self.URL_GET_BRAND % self.ID_VALID )
        valid_response(response, httplib.PAYMENT_REQUIRED)
        
    def test_get_by_brand_nonexistent(self):
        response = self.client_autenticado().get(self.URL_GET_BRAND % self.ID_NONEXISTENT)
        self._not_found(response)
    
    def test_get_by_brand_negative(self):
        response = self.client_autenticado().get(self.URL_GET_BRAND % self.NEGATIVE_ATTR)
        self._attr_invalid(response)
        
    def test_get_by_brand_letter(self):
        response = self.client_autenticado().get(self.URL_GET_BRAND % self.LETTER_ATTR)
        self._attr_invalid(response)
        
    def test_get_by_brand_zero(self):
        response = self.client_autenticado().get(self.URL_GET_BRAND % self.ZERO_ATTR)
        self._attr_invalid(response)
        
    def test_get_by_brand_empty(self):
        response = self.client_autenticado().get(self.URL_GET_BRAND % self.EMPTY_ATTR)
        self._attr_invalid(response)