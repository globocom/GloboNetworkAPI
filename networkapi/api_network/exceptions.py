from rest_framework.exceptions import APIException
from rest_framework import status


class EquipmentIDNotInCorrectEnvException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Equipments are not part of network environment.'

class InvalidNetworkIDException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid Network ID.'

class NoEnvironmentRoutersFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No environment routers found for network configuration.'

class IncorrectRedundantGatewayRegistryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Equipment IPs not correctly registered. \
			 Equipments should have first IP of network allocated for them as gateways.'

class IncorrectNetworkRouterRegistryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Equipment IPs not correctly registered. \
			 In case of multiple gateways, they should a registered IP other than the gateway.'
