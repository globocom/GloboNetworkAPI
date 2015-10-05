from rest_framework.exceptions import APIException
from rest_framework import status

class InvalidIdNameException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Name for Variable.'

class InvalidIdValueException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Value for Variable.'
