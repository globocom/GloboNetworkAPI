from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.base import BasePlugin
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS
from mock import patch, MagicMock


class JunosPluginTest(NetworkApiTestCase):

    """
    Junos plugin tests

    How to use:
        cd GloboNetworkAPI
        docker exec -it netapi_app ./fast_start_test_reusedb.sh networkapi/plugins/Juniper/JUNOS

    General notes:
        - autospec=True: responds to methods that actually exist in the real class
        - assert_called_once_with() assert if an important step was called
    """

    @patch('networkapi.equipamento.models.EquipamentoAcesso', autospec=True)
    def setUp(self, mock_equipment_access):
        
        """
        Equipment mock is a fake class used in specific test cases below
        """

        mock_equipment_access.fqdn = 'any fqdn'
        mock_equipment_access.user = 'any user'
        mock_equipment_access.password = 'any password'
        self.mock_equipment_access = mock_equipment_access

    def test_create_junos_with_super_class(self):
        plugin = JUNOS()
        self.assertIsInstance(plugin, BasePlugin)

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.Device', autospec=True)
    def test_connect_success(self, mock_device):

        """
        Simulate connect success using Junos Device mock.

        Note: All internal functions in Device Class are mocked, raising no exceptions on it

        Warning: For an unknown reason was not possible to use
        'jnpr.junos.Device' instead 'networkapi.plugins.Juniper.JUNOS.plugin.Device'
        """

        # Mocking result
        mock_device.return_value.connected = True

        # Close real test
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        connection_response = plugin.connect()

        # Asserts
        plugin.remote_conn.open.assert_called_with()
        self.assertIsNotNone(plugin.configuration)
        self.assertEqual(connection_response, True)

    @patch('jnpr.junos.utils.config.Config', autospec=True)
    def test_exec_command_success(self, mock_config):

        """
        This test asserts the success of the complete workflow of executing any command.
        Note: All internal functions in Config Class are mocked, raising no exceptions on it
        """

        # Mocking result
        plugin = JUNOS(equipment_access=self.mock_equipment_access)
        plugin.plugin_try_lock = MagicMock()
        plugin.plugin_try_lock.return_value = True
        plugin.configuration = mock_config

        # Close real test
        exec_command_response = plugin.exec_command("any command")

        # Assert
        plugin.configuration.rollback.assert_called_once_with()
        plugin.configuration.load.assert_called_once_with("any command", format='set')
        plugin.configuration.commit_check.assert_called_once_with()
        plugin.configuration.commit.assert_called_once_with()
        plugin.configuration.unlock.assert_called_once_with()
        self.assertIsNotNone(exec_command_response)

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_close(self, mock_junos_plugin):
        mock_junos_plugin.close()
        mock_junos_plugin.close.assert_called_with()

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_copyScriptFileToConfig(self, mock_junos_plugin):
        mock_junos_plugin.copyScriptFileToConfig("any file path")
        mock_junos_plugin.copyScriptFileToConfig.assert_called_with("any file path")

    @patch('networkapi.plugins.Juniper.JUNOS.plugin.JUNOS', autospec=True)
    def test_call_ensure_privilege_level(self, mock_junos_plugin):
        mock_junos_plugin.ensure_privilege_level()
        mock_junos_plugin.ensure_privilege_level.assert_called_with()
