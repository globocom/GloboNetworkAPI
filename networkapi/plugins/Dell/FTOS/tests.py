# -*- coding: utf-8 -*-
from mock import MagicMock
from mock import patch

from networkapi.plugins import exceptions
from networkapi.plugins.Dell.FTOS.plugin import FTOS
from networkapi.test.test_case import NetworkApiTestCase


class FTOSPluginTest(NetworkApiTestCase):

    """
    FTOS plugin tests

    How to use:
        cd GloboNetworkAPI
        docker exec -it netapi_app ./fast_start_test_reusedb.sh networkapi/plugins/Dell/FTOS/tests.py
    """

    def setUp(self):
        self.plugin = FTOS(equipment=MagicMock(nome='LF-CM-AH08-1'))
        self.plugin.channel = MagicMock()
        self.plugin.ensure_privilege_level = MagicMock()

        patcher = patch('networkapi.plugins.Dell.FTOS.plugin.sleep')
        patcher.start()
        self.addCleanup(patcher.stop)

    def mock_outputs(self, *outputs):
        """
        Each output is returned in a single recv() call, after the command is sent
        """
        pending = []

        def send(command):
            pending.append(outputs[len(self.plugin.channel.send.call_args_list) - 1])

        self.plugin.channel.send.side_effect = send
        self.plugin.channel.recv_ready.side_effect = lambda: bool(pending)
        self.plugin.channel.recv.side_effect = lambda size: pending.pop(0)

    def test_get_port_channel_success(self):
        """
        test_get_port_channel_success - Returns the running config of port-channel
        """

        self.mock_outputs(
            'terminal length 0\r\nLF-CM-AH08-1#',
            'show running-config interface port-channel 21\r\n'
            '!\r\n'
            'interface Port-channel 21\r\n'
            ' description to-host\r\n'
            ' no ip address\r\n'
            ' portmode hybrid\r\n'
            ' switchport\r\n'
            ' no shutdown\r\n'
            'LF-CM-AH08-1#')

        result = self.plugin.get_port_channel('21')

        self.assertEqual(
            '!\n'
            'interface Port-channel 21\n'
            ' description to-host\n'
            ' no ip address\n'
            ' portmode hybrid\n'
            ' switchport\n'
            ' no shutdown', result)
        self.plugin.ensure_privilege_level.assert_called_once_with()
        self.plugin.channel.send.assert_called_with(
            'show running-config interface port-channel 21\n')

    def test_get_port_channel_not_found(self):
        """
        test_get_port_channel_not_found - Raises PortChannelNotFoundException
        """

        # Real output of FTOS 9.14 (S5048F-ON) for an inexistent port-channel
        self.mock_outputs(
            'terminal length 0\r\nLF-CM-AH08-1#',
            'show running-config interface port-channel 99\r\n'
            'LF-CM-AH08-1#')

        with self.assertRaises(exceptions.PortChannelNotFoundException):
            self.plugin.get_port_channel('99')

    def test_get_port_channel_invalid_command(self):
        """
        test_get_port_channel_invalid_command - Raises InvalidCommandException
        """

        self.mock_outputs(
            'terminal length 0\r\nLF-CM-AH08-1#',
            'show running-config interface port-channel abc\r\n'
            '                                                ^\r\n'
            '% Error: Invalid input at "^" marker.\r\n'
            'LF-CM-AH08-1#')

        with self.assertRaises(exceptions.InvalidCommandException):
            self.plugin.get_port_channel('abc')

    def test_get_port_channel_timeout(self):
        """
        test_get_port_channel_timeout - Raises UnableToVerifyResponse when prompt never returns
        """

        self.mock_outputs(
            'terminal length 0\r\nLF-CM-AH08-1#',
            'show running-config interface port-channel 21\r\n')

        with self.assertRaises(exceptions.UnableToVerifyResponse):
            self.plugin.get_port_channel('21')
