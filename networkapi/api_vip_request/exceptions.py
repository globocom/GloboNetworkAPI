from rest_framework.exceptions import APIException
from rest_framework import status


class VipRequestDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Vip Request Does Not Exist.'


class EnvironmentVipDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Environment Vip Does Not Exist.'

class InvalidIdVipRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Vip Request.'