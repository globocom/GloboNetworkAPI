# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated

from networkapi.api_template.v4 import facade
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview

log = logging.getLogger(__name__)


class TemplateView(CustomAPIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated,))
    def get(self, request, *args, **kwargs):
        """
        Returns the exact content of a template by its type and name,
        as plain text.

        params:
            template_type: Type of template to be retrieved.
                           Type is config or rack.
            file_path: Template path relative to the root directory of
                       the type, e.g. bgp/template_neighbor_v4_remove_junos.
        """

        template_type = kwargs.get('template_type')
        file_path = kwargs.get('file_path')

        content = facade.get_template_content(template_type, file_path)

        return HttpResponse(content, content_type='text/plain; charset=utf-8')
