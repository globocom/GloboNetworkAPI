# -*- coding:utf-8 -*-
from functools import wraps
import json
import logging

from jsonspec.reference import resolve
from jsonspec.validators import load
from jsonspec.validators.exceptions import ValidationError

from networkapi.api_rest import exceptions as rest_exceptions

log = logging.getLogger(__name__)


def verify_ports(pools):
    for idx, pool in enumerate(pools['server_pools']):
        ips = list()
        v6 = list()
        for member in pool['server_pool_members']:
            if member['ip']:
                ips.append((resolve(member, '#/ip/id'), resolve(member, '#/port_real')))
            if member['ipv6']:
                v6.append((resolve(member, '#/ipv6/id'), resolve(member, '#/port_real')))

        if len(ips) != len(list(set(ips))):
            raise ValidationError(
                'Ips have same ports',
                ['#server_pools/%s/server_pool_members/*/ip/id - #server_pools/%s/server_pool_members/*/port_real' % (idx, idx)])
        if len(v6) != len(list(set(v6))):
            raise ValidationError(
                'Ipv6 have same ports',
                ['#server_pools/%s/server_pool_members/*/ipv6/id - #server_pools/%s/server_pool_members/*/port_real' % (idx, idx)])


def json_validate(json_file):

    with open(json_file) as data_file:
        data = json.load(data_file)
        validator = load(data)

    return validator


def raise_json_validate(info=None):
    def raise_json_validate_inner(func):
        @wraps(func)
        def inner(self, request, *args, **kwargs):
            try:
                return func(self, request, *args, **kwargs)
            except ValidationError, error:
                msg = list()

                if error.flatten():
                    for pointer, reasons in error.flatten().items():
                        valor = resolve(error[1], pointer) if pointer != '#/' else ''
                        msg.append({
                            'error_pointer': pointer,
                            'received_value': valor,
                            'error_reasons': list(reasons)
                        })
                else:
                    msg.append({
                        'error_pointer': error[0],
                        'received_value': None,
                        'error_reasons': list(error[1])
                    })
                res = {
                    'errors': msg
                }
                if info:
                    res['spec'] = '/api/v3/help/%s/' % info
                log.error(res)
                raise rest_exceptions.ValidationExceptionJson(res)
            except Exception as error:
                log.error(error)
                raise rest_exceptions.NetworkAPIException(error)
        return inner
    return raise_json_validate_inner
