"""
How to use onlu this test:
cd GloboNetworkAPI
docker exec -it netapi_app ./fast_start_test_reusedb.sh networkapi/plugins/Juniper/JUNOS

"""
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.base import BasePlugin
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS
from mock import patch, MagicMock


class JunosPluginTest(NetworkApiTestCase):

    def test_create_junos_plugin_class(self):
        plugin = JUNOS()
        self.assertIsInstance(plugin, BasePlugin)

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_connect(self, mock_junos_plugin):
        mock_junos_plugin.connect()
        mock_junos_plugin.connect.assert_called_with()

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_close(self, mock_junos_plugin):
        mock_junos_plugin.close()
        mock_junos_plugin.close.assert_called_with()

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_exec_command(self, mock_junos_plugin):
        mock_junos_plugin.exec_command("any command")
        mock_junos_plugin.exec_command.assert_called_with("any command")

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_copyScriptFileToConfig(self, mock_junos_plugin):
        mock_junos_plugin.copyScriptFileToConfig("any file path")
        mock_junos_plugin.copyScriptFileToConfig.assert_called_with("any file path")

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_ensure_privilege_level(self, mock_junos_plugin):
        mock_junos_plugin.ensure_privilege_level()
        mock_junos_plugin.ensure_privilege_level.assert_called_with()
