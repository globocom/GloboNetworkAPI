# -*- coding: utf-8 -*-
from django.test.client import Client
from mock import MagicMock
from mock import patch

from networkapi.plugins.base import BasePlugin
from networkapi.plugins.Juniper.JUNOS.plugin import JUNOS
from networkapi.test.test_case import NetworkApiTestCase


class EquipmentPortChannelGetTestCase(NetworkApiTestCase):

    port_channel_uri = '/api/v4/equipment/%s/port-channel/%s/'

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_equipment/v4/fixtures/initial_pre_equipment.json',
        'networkapi/api_equipment/v4/fixtures/initial_equipment.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

        self.plugin = JUNOS()
        self.plugin.connect = MagicMock(return_value=True)
        self.plugin.close = MagicMock(return_value=True)
        self.port_channel = {
            'name': 'ae1',
            'members': ['xe-0/0/1', 'xe-0/0/2'],
            'configuration': 'set interfaces ae1 mtu 9216'
        }
        self.plugin.get_port_channel = MagicMock(
            return_value=self.port_channel)

        self.patcher = patch(
            'networkapi.api_equipment.v4.facade.PluginFactory.factory')
        self.mock_factory = self.patcher.start()
        self.mock_factory.return_value = self.plugin

    def tearDown(self):
        self.patcher.stop()

    def _get(self, uri):
        return self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

    def test_get_port_channel(self):
        """Test GET port-channel by number in default format (text)."""

        response = self._get(self.port_channel_uri % (1, 1))

        self.compare_status(200, response.status_code)
        self.compare_values({'port_channel': self.port_channel},
                            response.data)
        self.plugin.connect.assert_called_once_with()
        self.plugin.get_port_channel.assert_called_once_with(
            'ae1', config_format='text')
        self.plugin.close.assert_called_once_with()

    def test_get_port_channel_by_junos_name_display_set(self):
        """Test GET port-channel by aeN name in set format without
        trailing slash.
        """

        response = self._get((self.port_channel_uri % (1, 'ae1'))
                             .rstrip('/') + '?display=set')

        self.compare_status(200, response.status_code)
        self.plugin.get_port_channel.assert_called_once_with(
            'ae1', config_format='set')

    def test_get_port_channel_invalid_name(self):
        """Test GET port-channel with invalid name."""

        response = self._get(self.port_channel_uri % (1, 'xe-0/0/1'))

        self.compare_status(404, response.status_code)
        self.assertFalse(self.mock_factory.called)

    def test_get_port_channel_invalid_display(self):
        """Test GET port-channel with invalid format."""

        response = self._get(self.port_channel_uri % (1, 1) + '?display=xml')

        self.compare_status(400, response.status_code)
        self.assertFalse(self.mock_factory.called)

    def test_get_port_channel_inexistent_equipment(self):
        """Test GET port-channel of inexistent equipment."""

        response = self._get(self.port_channel_uri % (1000, 1))

        self.compare_status(404, response.status_code)
        self.assertFalse(self.mock_factory.called)

    def test_get_port_channel_plugin_not_implemented(self):
        """Test GET port-channel of equipment without plugin."""

        self.mock_factory.side_effect = NotImplementedError()

        response = self._get(self.port_channel_uri % (1, 1))

        self.compare_status(400, response.status_code)

    def test_get_port_channel_not_supported_by_plugin(self):
        """Test GET port-channel with plugin that does not implement it."""

        plugin = BasePlugin()
        plugin.connect = MagicMock()
        self.mock_factory.return_value = plugin

        response = self._get(self.port_channel_uri % (1, 1))

        self.compare_status(400, response.status_code)
        self.assertFalse(plugin.connect.called)

    def test_get_port_channel_equipment_without_access(self):
        """Test GET port-channel of equipment without access."""

        self.mock_factory.return_value = 'Equipment has no Access.'

        response = self._get(self.port_channel_uri % (1, 1))

        self.compare_status(400, response.status_code)

    def test_get_port_channel_without_auth(self):
        """Test GET port-channel without authentication."""

        response = self.client.get(self.port_channel_uri % (1, 1))

        self.compare_status(401, response.status_code)
