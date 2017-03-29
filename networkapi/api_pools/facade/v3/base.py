# -*- coding: utf-8 -*-
import logging
import time

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from networkapi.api_pools import exceptions
from networkapi.api_pools import models
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.requisicaovips.models import ServerPool

log = logging.getLogger(__name__)


########################
# Pools
########################
def create_pool(pool, user):
    """Creates pool"""

    try:
        sp = ServerPool()
        sp.create_v3(pool, user)
    except exceptions.InvalidIdentifierAlreadyPoolException, e:
        raise ValidationAPIException(e)
    except exceptions.CreatedPoolValuesException, e:
        raise ValidationAPIException(e)
    except exceptions.PoolNameChange, e:
        raise ValidationAPIException(e)
    except exceptions.PoolEnvironmentChange, e:
        raise ValidationAPIException(e)
    except exceptions.IpNotFoundByEnvironment, e:
        raise ValidationAPIException(e)
    except exceptions.PoolError, e:
        raise ValidationAPIException(e)
    except ValidationAPIException, e:
        raise ValidationAPIException(e)
    except Exception, e:
        raise NetworkAPIException(e)
    else:
        return sp


def update_pool(pool, user):
    """Updates pool"""

    try:
        sp = get_pool_by_id(pool['id'])
        sp.update_v3(pool, user)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e)
    except exceptions.PoolNotExist, e:
        raise ObjectDoesNotExistException(e)
    except exceptions.InvalidIdentifierAlreadyPoolException, e:
        raise ValidationAPIException(e)
    except exceptions.CreatedPoolValuesException, e:
        raise ValidationAPIException(e)
    except exceptions.PoolNameChange, e:
        raise ValidationAPIException(e)
    except exceptions.PoolEnvironmentChange, e:
        raise ValidationAPIException(e)
    except exceptions.IpNotFoundByEnvironment, e:
        raise ValidationAPIException(e)
    except exceptions.PoolError, e:
        raise ValidationAPIException(e)
    except ValidationAPIException, e:
        raise ValidationAPIException(e)
    except Exception, e:
        raise NetworkAPIException(e)
    else:
        return sp


def delete_pool(pools_ids):
    """Delete pool"""

    for pool_id in pools_ids:
        try:
            sp = get_pool_by_id(pool_id)
            sp.delete_v3()
        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e)
        except exceptions.PoolNotExist, e:
            raise ObjectDoesNotExistException(e)
        except exceptions.PoolConstraintCreatedException, e:
            raise ValidationAPIException(e)
        except exceptions.PoolError, e:
            raise ValidationAPIException(e)
        except ValidationAPIException, e:
            raise ValidationAPIException(e)
        except Exception, e:
            raise NetworkAPIException(e)


def get_pool_by_ids(pools_ids):
    """
    Return pool list by ids
    param pools_ids: ids list
    example: [<pools_id>,...]
    """

    pls_ids = list()
    for pool_id in pools_ids:
        try:
            sp = get_pool_by_id(pool_id).id
            pls_ids.append(sp)
        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e)
        except exceptions.PoolNotExist, e:
            raise ObjectDoesNotExistException(e)
        except Exception, e:
            raise NetworkAPIException(e)

    server_pools = ServerPool.objects.filter(id__in=pls_ids)

    return server_pools


def get_pool_by_id(pool_id):
    """
    Return pool by id
    param pools_id: id
    """

    try:
        server_pool = ServerPool.objects.get(id=pool_id)
    except ObjectDoesNotExist:
        raise exceptions.PoolNotExist()
    else:
        return server_pool


def get_pool_list_by_environmentvip(environment_vip_id):
    """
    Return pool list by environment_vip_id
    param environment_vip_id: environment_vip_id
    """

    server_pool = ServerPool.objects.filter(
        Q(environment__vlan__networkipv4__ambient_vip__id=environment_vip_id) |
        Q(environment__vlan__networkipv6__ambient_vip__id=environment_vip_id)
    ).distinct().order_by('identifier')

    return server_pool


def get_options_pool_list_by_environment(environment_id):
    """
    Return list of options pool by environment_id
    param environment_id: environment_id
    """

    options_pool = models.OptionPool.objects.filter(
        optionpoolenvironment__environment=environment_id
    ).order_by('name')

    return options_pool


def get_pool_by_search(search=dict()):

    try:
        pools = ServerPool.objects.filter()
        pool_map = build_query_to_datatable_v3(pools, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return pool_map


def reserve_name_healthcheck(pool_name):
    name = '/Common/MONITOR_POOL_%s_%s' % (pool_name, str(time.time()))

    return name
