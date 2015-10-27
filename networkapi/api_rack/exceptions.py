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

class RackError(Exception):

    """Representa um erro ocorrido durante acesso ?|  tabela racks."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')

class RackAplError(Exception):

    """Retorna excecao quao a configuracao nao pode ser aplicada."""

    def __init__(self, cause, param=None, value=None):
        self.cause = cause
        self.param = param
        self.value = value