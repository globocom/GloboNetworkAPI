# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


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


class RackError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'RackError.'


class RackAplError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Erro aplicando a configuracao no Rack.'


class RackNumberNotFoundError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Rack does not exist.'
