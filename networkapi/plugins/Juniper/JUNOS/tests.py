"""
How to use onlu this test:
cd GloboNetworkAPI
docker exec -it netapi_app ./fast_start_test_reusedb.sh networkapi/plugins/Juniper/JUNOS

"""
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.base import BasePlugin
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS


class JunosPluginTest(NetworkApiTestCase):

    def test_create_junos_plugin_class(self):
        """
        JunosPluginTest - test_create_junos_plugin_class - Tests if the class will be properly created
        """
        plugin = JUNOS()
        self.assertIsInstance(plugin, BasePlugin)
