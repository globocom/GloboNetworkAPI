from rest_framework.exceptions import APIException
from rest_framework import status

class RackNumberDuplicatedValueError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Numero de Rack ja existe.'

class RackNameDuplicatedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Nome ja existe.'

class InvalidInputException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'

class VariableDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Variable Does Not Exist.'

class VariableDuplicateNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Variable already exists.'