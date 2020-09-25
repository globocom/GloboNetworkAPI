from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.base import BasePlugin
from networkapi.plugins.Junos.plugin import Junos


class JunosPluginTest(NetworkApiTestCase):

    def test_create_junos_plugin_class(self):
        """
        JunosPluginTest - test_create_junos_plugin_class - Tests if the class will be properly created
        """
        obj = Junos()
        self.assertIsInstance(obj, BasePlugin)
