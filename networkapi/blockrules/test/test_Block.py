# -*- coding:utf-8 -*-

from networkapi.ambiente.models import DivisaoDc
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib
from networkapi.blockrules.models import BlockRules


class BlockConfigTest(BasicTestCase): 
    
    #Constants
    fixtures = ['networkapi/blockrules/fixtures/initial_data.yaml']
    XML_KEY = 'map'
    ID_VALID = '100'
    ID_INVALID = '1000'
    ID_ENV_TO_INSERT = '101'
    ID_NONEXISTENT = '12312'
    OBJ = BlockRules
    
    #Urls
    URL_GET_BLOCK = "/environment/get_blocks/%s/"
    URL_SAVE = "/environment/save_blocks/"
    URL_ALTER = "/environment/update_blocks/"
    URL_LIST_NO_BLOCKS = "/environment/list_no_blocks/"
    
    def mock_valid(self):
        mock = {}
        mock["blocks"] = ["Content valid"]
        mock["id_env"] = self.ID_ENV_TO_INSERT
        return mock
    
    def mock_valid_alter(self):
        mock = {}
        mock["blocks"] = ["Content valid_alter"]
        mock["id_env"] = self.ID_ENV_TO_INSERT
        return mock
    
    def alter_attr_invalid(self, attr, code_error = None):
        mock = self.mock_valid_alter()
        mock[self.KEY_ATTR] = attr
        response = self.client_autenticado().postXML(self.URL_ALTER, { self.XML_KEY : mock })
        self._attr_invalid(response, code_error)    

class BlockConsultationTest(BlockConfigTest, ConsultationTest):
    
    def test_get_by_environment(self):
        
        response = self.client_autenticado().get(self.URL_GET_BLOCK % self.ID_VALID)
        valid_response(response)
        valid_content(response, 'blocks', True)
        
    def test_get_by_environment_no_permission(self):
        response = self.client_no_permission().get(self.URL_GET_BLOCK % self.ID_VALID)
        valid_response(response, httplib.PAYMENT_REQUIRED)
        
    def test_get_by_environment_negative(self):
        response = self.client_autenticado().get(self.URL_GET_BLOCK % self.NEGATIVE_ATTR)
        self._attr_invalid(response)    
        
    def test_get_by_environment_letter(self):
        response = self.client_autenticado().get(self.URL_GET_BLOCK % self.LETTER_ATTR)
        self._attr_invalid(response)         
        
    def test_get_by_environment_none(self):
        response = self.client_autenticado().get(self.URL_GET_BLOCK % self.NONE_ATTR)
        self._attr_invalid(response)
        
    def test_get_by_environment_zero(self):
        response = self.client_autenticado().get(self.URL_GET_BLOCK % self.ZERO_ATTR)
        self._attr_invalid(response)       
        
    def test_get_by_environment_empty(self):
        response = self.client_autenticado().get(self.URL_GET_BLOCK % self.EMPTY_ATTR)
        self._attr_invalid(response)
    
    def test_get_environment_no_blocks(self):
        response = self.client_autenticado().get(self.URL_LIST_NO_BLOCKS)
        valid_response(response)
        valid_content(response, 'ambiente', True)
        

class BlockTest(BlockConfigTest):
    
    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock })
        valid_response(response)
        
    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock }, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock }, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)
        
    def test_update_valid(self):
        mock = self.mock_valid_alter()
        response = self.client_autenticado().putXML(self.URL_ALTER, { self.XML_KEY : mock })
        valid_response(response)
    
    def test_update_no_permission(self):
        mock = self.mock_valid_alter()
        response = self.client_no_permission().putXML(self.URL_ALTER, { self.XML_KEY : mock })
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_update_no_write_permission(self):
        mock = self.mock_valid_alter()
        response = self.client_no_write_permission().putXML(self.URL_ALTER, { self.XML_KEY : mock })
        valid_response(response, httplib.PAYMENT_REQUIRED)              
        
class BlockAttrIdEnvTest(BlockConfigTest, AttrTest):
    
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
        response = self.save({ self.XML_KEY : mock })
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
        response = self.save({ self.XML_KEY : mock })
        self._not_found(response, self.CODE_ERROR_ENVIRONMENT_NOT_FOUND)