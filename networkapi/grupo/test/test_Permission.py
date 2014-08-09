# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.grupo.models import Permission
from networkapi.test import BasicTestCase, CodeError, ConsultationTest, CLIENT_TYPES, me
from networkapi.test.functions import valid_content, valid_response, valid_get_all
import httplib


class PermissionConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/grupo/fixtures/initial_data.yaml']
    XML_KEY = ""
    ID_VALID = 1
    OBJ = Permission

    # Urls
    URL_SAVE = ""
    URL_ALTER = ""
    URL_REMOVE = ""
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/perms/all/"

    def mock_valid(self):
        mock = {}
        mock['id'] = 1
        mock['function'] = "mock"
        return mock


class PermissionConsultationTest(PermissionConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.PERMISSION_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "perms")
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_active(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response, httplib.UNAUTHORIZED)
