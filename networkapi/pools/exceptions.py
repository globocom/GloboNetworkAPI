from rest_framework.exceptions import APIException


class PoolDoesNotExists(APIException):
    """Example Raised Exception
    """
    status_code = 400
    default_detail = 'Pool Does Not Exist.'
