# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class TemplateNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Template not found.'

    def __init__(self, name=None):
        self.detail = u'Template %s not found.' % name if name \
            else self.default_detail


class InvalidTemplatePathException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid template path.'

    def __init__(self, path=None):
        self.detail = u'Invalid template path: %s.' % path if path \
            else self.default_detail


class InvalidTemplateTypeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid template type.'

    def __init__(self, template_type=None):
        self.detail = u'Invalid template type: %s.' % template_type \
            if template_type else self.default_detail


class TemplateReadException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to read template.'

    def __init__(self, name=None):
        self.detail = u'Failed to read template %s.' % name if name \
            else self.default_detail
