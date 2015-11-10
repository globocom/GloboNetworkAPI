import bigsuds
from functools import wraps
import logging
from networkapi.plugins import exceptions as base_exceptions

log = logging.getLogger(__name__)

########################################
# Decorators
########################################
def transation(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            with bigsuds.Transaction(self._lb._channel):
                return func(self, *args, **kwargs)
        except bigsuds.OperationFailed, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)
        except Exception, e:
            log.error("Error  %s" % e)
            raise base_exceptions.CommandErrorException(e)
    return inner