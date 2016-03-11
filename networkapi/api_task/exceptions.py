# -*- coding:utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class TaskReadyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = u'Task has been completed or is running'
