from rest_framework.exceptions import APIException
from rest_framework import status


class VipRequestDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Vip Request Does Not Exist.'
