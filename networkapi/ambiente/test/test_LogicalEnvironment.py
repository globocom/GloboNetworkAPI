# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.ambiente.models import AmbienteLogico
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class LogicalEnvironmentConfigTest(BasicTestCase): 
    
    #Constants
    fixtures = ['networkapi/ambiente/fixtures/initial_data.yaml']
    XML_KEY = "logical_environment"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    OBJ = AmbienteLogico
    
    #Urls
    URL_SAVE = "/logicalenvironment/"
    URL_ALTER = "/logicalenvironment/%s/"
    URL_REMOVE = "/logicalenvironment/%s/"
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/logicalenvironment/all/"
    
    def mock_valid(self):
        mock = {}
        mock['name'] = "mock"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["name"] == obj["nome"]

class LogicalEnvironmentConsultationTest(LogicalEnvironmentConfigTest, ConsultationTest):
    
    CODE_ERROR_NOT_FOUND = CodeError.LOGICAL_ENVIRONMENT_NOT_FOUND
    
    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "logical_environment")
        valid_get_all(content, self.OBJ) 
        
    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)
        
    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

class LogicalEnvironmentTest(LogicalEnvironmentConfigTest): 
    
    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({ self.XML_KEY : mock })
        valid_response(response)
        loc_env = valid_content(response, "logical_environment")
        
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "logical_environment")
        
        for env in content:
            if env["id"] == loc_env["id"]:
                self.valid_attr(mock, env)
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
        mock["name"] = "LogicalEnvironmentAlter"
        response = self.alter(self.ID_ALTER_VALID, { self.XML_KEY : mock })
        valid_response(response)
        
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "logical_environment")
        
        for grp in content:
            if grp["id"] == self.ID_ALTER_VALID:
                self.valid_attr(mock, grp)
                break
        
    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(self.ID_ALTER_VALID, { self.XML_KEY : mock }, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(self.ID_ALTER_VALID, { self.XML_KEY : mock }, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

class LogicalEnvironmentRemoveTest(LogicalEnvironmentConfigTest, RemoveTest):
    
    CODE_ERROR_NOT_FOUND = CodeError.LOGICAL_ENVIRONMENT_NOT_FOUND
    
    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(self.ID_REMOVE_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
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

class LogicalEnvironmentcAttrNameTest(LogicalEnvironmentConfigTest, AttrTest):
    
    KEY_ATTR = "name"
    
    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(81)
        self.process_save_attr_invalid(mock)
        
    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(1)
        self.process_save_attr_invalid(mock)
    
    def test_save_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "logical_environment")
        
        loc_env = content[0]
        
        mock = self.mock_valid()
        mock["name"] = loc_env["nome"]
         
        self.process_save_attr_invalid(mock, CodeError.LOGICAL_ENVIRONMENT_DUPLICATE)
       
    def test_save_empty(self):
        self.save_attr_empty()
    
    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):    
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(81)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):    
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(1)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)
       
    def test_alter_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "logical_environment")
        
        loc_env = content[0]
        
        mock = self.mock_valid()
        mock["name"] = loc_env["nome"] 
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock, CodeError.LOGICAL_ENVIRONMENT_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)