from rest_framework.exceptions import APIException
from rest_framework import status


class PoolDoesNotExistException(APIException):
    """Example Raised Exception
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Pool Does Not Exist.'


class InvalidIdPoolException(APIException):
    """Example Raised Exception
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool.'
