# -*- coding:utf-8 -*-
import json
import logging

from networkapi.settings import SPECS

from rest_framework.response import Response
from rest_framework.views import APIView


log = logging.getLogger(__name__)


class HelperApi(APIView):

    def get(self, request, *args, **kwargs):
        """Enable/Disable pool member by list"""

        try:
            way = kwargs['way']
            with open(SPECS.get(way)) as data_file:
                data = json.load(data_file)

            return Response(data)
        except Exception, exception:
            log.error(exception)
            raise Exception('Spec not exists')
