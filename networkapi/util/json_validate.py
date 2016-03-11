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
        for member in pool['server_pool_members']:
            ips.append((resolve(member, '#/ip/id'), resolve(member, '#/port_real')))

        if len(ips) != len(list(set(ips))):
            raise ValidationError(
                'Ips have same ports',
                ['#server_pools/%s/server_pool_members/*/ip/id - #server_pools/%s/server_pool_members/*/port_real' % (idx, idx)])


def json_validate(json_file):

    with open(json_file) as data_file:
        data = json.load(data_file)
        validator = load(data)

    return validator


def raise_json_validate(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        try:
            return func(self, request, *args, **kwargs)
        except ValidationError as error:
            msg = list()
            if error.flatten():
                for pointer, reasons in error.flatten().items():
                    valor = resolve(error[1], pointer) if pointer != '#/' else ''
                    msg.append({
                        'field': pointer,
                        'valor': valor,
                        'reasons': list(reasons)
                    })
            else:
                msg.append({
                    'field': error[0],
                    'valor': '',
                    'reasons': list(error[1])
                })
            log.error(msg)
            raise rest_exceptions.ValidationExceptionJson(msg)
        except Exception as error:
            log.error(error)
            raise rest_exceptions.NetworkAPIException(error)
    return inner
