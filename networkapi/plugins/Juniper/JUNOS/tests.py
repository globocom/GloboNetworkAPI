"""
How to use onlu this test:
cd GloboNetworkAPI
docker exec -it netapi_app ./fast_start_test_reusedb.sh networkapi/plugins/Juniper/JUNOS

"""
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.base import BasePlugin
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS
from mock import patch


class JunosPluginTest(NetworkApiTestCase):

    def test_create_junos_plugin_class(self):
        """
        JunosPluginTest - test_create_junos_plugin_class - Tests if the class will be properly created
        """
        plugin = JUNOS()
        self.assertIsInstance(plugin, BasePlugin)

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS.connect')
    def test_call_connect(self, mock_plugin_function):
        mock_plugin_function.assert_called()

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS.close')
    def test_call_close(self, mock_plugin_function):
        mock_plugin_function.assert_called()

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS.exec_command')
    def test_call_exec_command(self, mock_plugin_function):
        mock_plugin_function.assert_called()

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS.copyScriptFileToConfig')
    def test_call_copyScriptFileToConfig(self, mock_plugin_function):
        mock_plugin_function.assert_called()

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS.ensure_privilege_level')
    def test_call_ensure_privilege_level(self, mock_plugin_function):
        mock_plugin_function.assert_called()
