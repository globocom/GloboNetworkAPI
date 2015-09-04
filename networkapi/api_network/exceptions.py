from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidNetworkIDException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Network ID.'
