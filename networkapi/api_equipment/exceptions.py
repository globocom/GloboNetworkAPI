from rest_framework.exceptions import APIException
from rest_framework import status


class AllEquipmentsAreInMaintenanceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'All equipments to be configured are in maintenance mode.'
