
from rest_framework import status
from rest_framework.exceptions import APIException

class InvalidNeighborException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Neighbor is Invalid.'

    def __init__(self, msg):
        self.detail = msg
