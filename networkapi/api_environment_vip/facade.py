# -*- coding: utf-8 -*-
import logging

from networkapi.ambiente.models import EnvironmentVip
from networkapi.ambiente.models import EnvironmentVipAssociatedToSomeNetworkError
from networkapi.ambiente.models import EnvironmentVipNotFoundError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import OptionVipEnvironmentVip

log = logging.getLogger(__name__)


def get_environmentvip_by_search(search=dict()):
    """Return a list of environments vip by dict.

    :param search: dict
    """

    env_vips = EnvironmentVip.objects.all()
    env_map = build_query_to_datatable_v3(env_vips, search)

    return env_map


def get_option_vip_by_environment_vip_ids(environment_vip_ids):
    """Return option vip list by ids of environment vip.

    :param environment_vip_ids: ids list of environment vip
    :example: [<environment_vip_id>,...]

    """
    options_vip = list()
    for environment_vip_id in environment_vip_ids:
        option_environment_vips = OptionVipEnvironmentVip.objects.filter(
            environment=environment_vip_id
        ).order_by(
            'option__tipo_opcao',
            'option__nome_opcao_txt'
        )

        options_vip.append(option_environment_vips)
    return options_vip


def get_option_vip_by_environment_vip_type(search_list):
    """Return option vip list by ids of environment vip and option vip type.

    :param environment_vip_ids: ids list of environment vip
    :param type_option: option vip type
    :example: [{
        environment_vip_id:<environment_vip_id>
        type_option:<type_option>
    ]}
    """
    options_vip = list()
    for item in search_list:

        option_environment_vips = OptionVip.objects.filter(
            optionvipenvironmentvip__environment__id=item[
                'environment_vip_id'],
            tipo_opcao=item['type_option'])

        options_vip.append(option_environment_vips)
    return options_vip


def get_type_option_vip_by_environment_vip_ids(environment_vip_ids):
    """Return option vip list by ids of environment vip and option vip type.

    :param environment_vip_ids: ids list of environment vip

    """
    type_option_vip = list()
    for environment_vip_id in environment_vip_ids:

        type_options = OptionVip.objects.filter(
            optionvipenvironmentvip__environment__id=environment_vip_id
        ).values('tipo_opcao').distinct()

        type_options = [type_option['tipo_opcao']
                        for type_option in type_options]

        type_option_vip.append(type_options)
    return type_option_vip


def get_environmentvip_by_ids(environment_vip_ids):

    envvips = list()
    for environment_vip_id in environment_vip_ids:
        try:
            envvip = get_environmentvip_by_id(environment_vip_id).id
            envvips.append(envvip)
        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    environmentvips = EnvironmentVip.objects.filter(id__in=envvips)

    return environmentvips


def get_environmentvip_by_id(environment_vip_id):

    try:
        environmentvip = EnvironmentVip.get_by_pk(environment_vip_id)
    except EnvironmentVipNotFoundError, e:
        raise ObjectDoesNotExistException(str(e))
    else:
        return environmentvip


def update_environment_vip(environment_vip):

    try:
        env = get_environmentvip_by_id(environment_vip.get('id'))
        env.update_v3(environment_vip)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env


def create_environment_vip(environment_vip):

    try:
        env = EnvironmentVip()
        env.create_v3(environment_vip)
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env


def delete_environment_vip(envvip_ids):

    for envvip_id in envvip_ids:
        try:
            envvip_obj = get_environmentvip_by_id(envvip_id)
            envvip_obj.delete_v3()
        except EnvironmentVipAssociatedToSomeNetworkError, e:
            raise ValidationAPIException(str(e))
        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))
