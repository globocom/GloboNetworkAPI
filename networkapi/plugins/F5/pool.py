import F5
import F5.util

from networkapi.plugins import exceptions as base_exceptions

class Pool(object):

    def __init__(self, lb=None):
        if lb is not None and not isinstance(lb, F5.Lb):
            raise base_exceptions.PluginUninstanced('lb must be of type F5.Lb')

        self._lb = lb

	def createPool(self, pools):
		self._lb._channel.LocalLB.Pool.create_v2(
		    pools['pools_name'],
		    pools['pools_lbmethod'],
		    pools['pools_members'])