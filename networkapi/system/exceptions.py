# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidIdNameException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Name for Variable.'


class InvalidIdValueException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Value for Variable.'


class VariableDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Variable Does Not Exist.'


class VariableDuplicateNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Variable already exists.'


class VariableError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Falha ao inserir variavel.'


class InvalidInputException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
