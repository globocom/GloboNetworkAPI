# -*- coding:utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class EnvironmentDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Environment Does Not Exist.'

    def __init__(self, msg=None):
        self.detail = self.default_detail if not msg else msg
