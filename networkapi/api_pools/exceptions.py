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

class InvalidIdEnvironmentException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Environment.'


class InvalidServiceDownActionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid value for Service-Down-Action.'


class InvalidIdVipException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for VIP.'


class InvalidIdentifierAlreadyPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Identifier already exists.'


class InvalidIdentifierFistDigitPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'The first character of the identifier field can not be a number.'

class CreatedPoolIdentifierException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Pool already created. Cannot change Identifier.'


class InvalidIdPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool Member.'

class ScriptRemovePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute remove script for pool.'

class ScriptAlterServiceDownActionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute service-down-action script for pool.'


class ScriptCreatePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute create script for pool.'


class ScriptAddPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute add script for pool.'


class ScriptCheckStatusPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute status script for pool member.'


class ScriptDeletePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute delete script for pool.'


class ScriptEnablePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute enable script for pool.'


class ScriptDisablePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute disable script for pool.'

class ScriptAlterLimitPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute limits script for pool.'

class ScriptAlterPriorityPoolMembersException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute priority script for pool.'

class ScriptAlterLimitPoolDiffMembersException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to change limits for pool. Members limit differs from pool default limit \
    Set all members with the same default limit before changing default pool limit.'

class PoolConstraintVipException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Pool nao pode ser excluido pois esta associado com um VIP.'

class PoolConstraintCreatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Pool request can not be deleted because it is created in equipment.'

class UpdateEnvironmentVIPException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ambiente nao pode ser alterado pois o server pool esta associado com um ou mais VIP.'

class UpdateEnvironmentPoolCreatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ambiente nao pode ser alterado pois o server pool ja esta criado no equipamento.'

class UpdateEnvironmentServerPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ambiente nao pode ser alterado pois o server pool esta associado com um ou mais server pool member.'


class IpNotFoundByEnvironment(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'O ambiente do IP e diferente do ambiente do Server Pool.'


class InvalidRealPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Parametros invalidos do real.'


class InvalidIdPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool.'


class ScriptManagementPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute management pool members script for pool.'


class InvalidStatusPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid status for Pool Member.'


class OptionPoolDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Option Pool Does Not Exist.'

class EnvironmentDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Environment Does Not Exist.'

class InvalidIdOptionPoolRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Option Pool Request.'

class OptionPoolEnvironmentDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Environment Option Pool Does Not Exist.'

class InvalidIdOptionPoolEnvironmentRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Environment Option Pool Request.'

class ScriptAddPoolOptionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute add script for pool option.'

class ScriptAddEnvironmentPoolOptionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute add script for environment pool option.'

class OptionPoolConstraintPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'OptionPool can not be deleted because it is associated with a Pool.'

class ScriptDeletePoolOptionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute delete script for pool option.'

class ScriptModifyPoolOptionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute modify script for pool option.'

class ScriptDeleteEnvironmentPoolOptionException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute delete script for environment pool option.'

class AllEquipamentMaintenance(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'All equipments is in maintenance.'

    def __init__(self, msg=None):
        self.detail = u'All equipments is in maintenance. Pool: <<%s>>' % (msg)

class DiffStatesEquipament(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Poolmember has states different in equipments.'

    def __init__(self, msg=None):
        self.detail = u'The poolmember <<%s>> has states different in equipments.' % (msg)
