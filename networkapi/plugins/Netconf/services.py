import json
import logging

import requests
from django.conf import settings

from networkapi.extra_logging import local
from networkapi.plugins import exceptions


log = logging.getLogger(__name__)


class NetconfServices:

    """Client of the netconf microservice."""

    def __init__(self, equipment_access):
        self.equipment_access = equipment_access
        self.retrieve_url = '{}/retrieve'.format(settings.NETWORKAPI_NETCONF_URL)

    def get_resource(self, filter, source=''):

        """
        Get a resource (configuration or state) from the equipment using the netconf
        microservice (POST /retrieve).

        :param str filter: subtree filter (XML) that matches the resource
        :param str source: datastore, example:
            'running': active configuration (the resource may be up or down).
            'candidate': configuration not yet committed
            '' or omitted: configuration + operational state.
        :returns:
            Returns the response of netconf microservice as is (XML of the resource), otherwise,
            raise an exception (NetconfMicroserviceException with the error response of
            netconf microservice as is, e.g. 404 when the filter matches nothing).
            That means will NOT return a false result.
        """

        log.info("Trying to get resource by netconf from host {} ... ".format(self.equipment_access.fqdn))

        try:
            response = requests.post(
                url=self.retrieve_url,
                headers={"Content-type": "application/json",
                         "X-Request-Id": getattr(local, "request_id", None)},
                data=json.dumps({
                    "address": self.equipment_access.fqdn,
                    "username": self.equipment_access.user,
                    "password": self.equipment_access.password,
                    "source": source,
                    "filter": filter
                })
            )
        except Exception as e:
            message = "Unknown error while getting resource by netconf from host {}.".format(
                self.equipment_access.fqdn)
            log.error("{}: {}".format(message, e))
            raise exceptions.APIException(message)

        # Error responses (e.g. 404 when the filter matches nothing) are passed through as is
        if response.status_code != 200:
            log.error("Error response from netconf microservice for host {} (status {}): {}. Filter: {}".format(
                self.equipment_access.fqdn, response.status_code, response.text, filter))
            raise exceptions.NetconfMicroserviceException(
                response.status_code, response.content,
                response.headers.get('Content-Type', 'application/xml'))

        log.info("Resource was got successfully from host {}!".format(self.equipment_access.fqdn))

        # Returns the response of netconf microservice as is (XML)
        return response.text
