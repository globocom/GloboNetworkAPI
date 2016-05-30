import logging

from networkapi.plugins.Brocade.base import Base


log = logging.getLogger(__name__)


class Real(Base):

    def get_list(self):
        """Returns a list of all servers configured on the load balancer"""

        #TODO: error handle
        realServerPortList = self._lb.slb_service.getAllRealServerPortList()[0]


    def get_all_real_names_by_ip(self, ip):
        """Returns a list of all servers configured with a specific ip address"""

        pass

    def create(self):
        pass

    def delete(self):
        pass