# -*- coding:utf-8 -*-
import logging

from networkapi.ambiente.models import Ambiente
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_environment_by_search(search=dict()):
    """Return
    """

    environments = Ambiente.objects.filter()

    env_map = build_query_to_datatable_v3(environments, 'envs', search)

    return env_map
