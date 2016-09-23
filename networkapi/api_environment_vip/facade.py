# -*- coding:utf-8 -*-
import logging

from networkapi.ambiente.models import EnvironmentVip
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import OptionVipEnvironmentVip

log = logging.getLogger(__name__)


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
            optionvipenvironmentvip__environment__id=item['environment_vip_id'],
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

        type_options = [type_option['tipo_opcao'] for type_option in type_options]

        type_option_vip.append(type_options)
    return type_option_vip


def get_environmentvip_by_ids(environment_vip_ids):

    environmentvips = EnvironmentVip.objects.filter(id__in=environment_vip_ids)

    return environmentvips


def update_environment_vip(environment_vip):

    env = EnvironmentVip.objects.get(id=environment_vip.get('id'))
    env.conf = environment_vip.get('conf')
    env.save()

    return env
