# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.exceptions import APIException


class RouteMapNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'RouteMap %s do not exist.' % (msg)


class RouteMapError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class RouteMapDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = u'RouteMap does not exists.'


class RouteMapEntryNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, msg):
        self.detail = u'RouteMapEntry %s do not exist.' % (msg)


class RouteMapEntryError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, msg):
        self.detail = msg


class RouteMapEntryDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = u'RouteMapEntry does not exists.'


class RouteMapAssociatedToRouteMapEntryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map):
        self.detail = u'RouteMap id = {} is associated ' \
                      u'with RouteMapEntries = {}'. \
            format(route_map.id, route_map.route_map_entries_id)


class RouteMapAssociatedToPeerGroupException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, route_map):
        self.detail = u'RouteMap id = {} is associated ' \
                      u'with PeerGroups = {}'. \
            format(route_map.id, route_map.peer_groups_id)
