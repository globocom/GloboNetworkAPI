# -*- coding: utf-8 -*-

from os import environ


class OpenDaylightTestUtils(object):
    """  Utilitary methods for testing OpenDaylight controller """

    CTRL_IP_ENV = "REMOTE_CTRL_IP"
    CTRL_PORT = 8181
    CTRL_PROTOCOL = "http"

    def set_controller_endpoint(self, equipment_access=None):
        """ Sets OpenDaylight endpoint uri for requests """

        if equipment_access is None:
            raise ValueError("Missing equipment")

        controller_endpoint = environ.get(self.CTRL_IP_ENV)

        if controller_endpoint is not None:

            ctrl_uri = "{protocol}://{addr}:{port}".format(
                protocol=self.CTRL_PROTOCOL,
                addr=controller_endpoint,
                port=self.CTRL_PORT
            )

            equipment_access.fqdn = ctrl_uri
            equipment_access.save()
