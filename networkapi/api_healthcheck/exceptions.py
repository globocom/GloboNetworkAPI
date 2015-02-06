from rest_framework.exceptions import APIException
from rest_framework import status


class PoolDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Pool Does Not Exist.'


class PoolMemberDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Pool Member Does Not Exist.'


class InvalidIdPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool.'


class InvalidIdPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool Member.'


class ScriptRemovePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute remove script for pool.'


class ScriptCreatePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute create script for pool.'


class ScriptAddPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute add script for pool.'


class ScriptDeletePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute delete script for pool.'


class ScriptEnablePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute enable script for pool.'


class ScriptDisablePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute disable script for pool.'


class PoolConstraintVipException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Pool can not be deleted because it is associated with a VIP.'
