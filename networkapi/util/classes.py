# -*- coding: utf-8 -*-
from rest_framework.views import APIView

from networkapi.extra_logging import local


class CustomAPIView(APIView):

    def finalize_response(self, request, *args, **kwargs):
        response = super(CustomAPIView, self)\
            .finalize_response(request, *args, **kwargs)

        response['X-Request-Context'] = local.request_context
        response['X-Request-Id'] = local.request_id,

        return response
