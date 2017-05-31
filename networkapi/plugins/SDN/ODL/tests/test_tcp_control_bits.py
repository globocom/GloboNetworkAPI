# -*- coding: utf-8 -*-

from nose.tools import assert_raises
from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_is_instance

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.SDN.ODL.utils.tcp_control_bits import TCPControlBits


class TestTCPControlBits(NetworkApiTestCase):
    """ Class to test creation of TCP / IP Control bits """

    def test_should_raise_value_error_for_missing_parameters(self):
        """ Should raise value error for missing paramters """

        assert_raises(ValueError, TCPControlBits)

    def test_should_build_a_simple_tcp_flags_with_ack_bit_enabled(self):
        """ Should build a simple tcp flags with ACK bit enabled """

        tcp_flags = TCPControlBits(['ACK'])
        assert_equal(tcp_flags.control_bits['ACK'], 1)

    def test_should_have_all_bits_zeroed_because_there_is_no_valid_flag(self):
        """ Should have all bits zeroed because there is no valid flag """
        tcp_flags = TCPControlBits(['AAA', 'BBB', 'CCC'])
        assert_false(any(tcp_flags.control_bits.values()))

    def test_should_return_a_dict(self):
        """ Should return a dict from the informed tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_is_instance(tcp_flags.to_dict(), dict)

    def test_should_return_a_list(self):
        """ Should return a list from the informed tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_is_instance(tcp_flags.to_list(), list)

    def test_should_return_a_str(self):
        """ Should return a str from the informed tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_is_instance(tcp_flags.to_str(), str)

    def test_should_return_a_integer(self):
        """ Should return an int from the informed tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_is_instance(tcp_flags.to_int(), int)

    def test_should_return_a_binary(self):
        """ Should return a bin from the informed tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_is_instance(tcp_flags.to_bin(), str)

    def test_should_return_a_hexadecimal(self):
        """ Should return a hex from the informed tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_is_instance(tcp_flags.to_hex(), str)

    def test_should_return_the_correct_hexadecimal(self):
        """ Should return the correct Hexadecimal from tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_equal(tcp_flags.to_hex(), '0x12')

    def test_should_return_the_correct_binary(self):
        """ Should return the correct Binary from tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_equal(tcp_flags.to_bin(), '0b10010')

    def test_should_return_the_correct_string(self):
        """ Should return the correct String from tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_equal(tcp_flags.to_str(), '00010010')

    def test_should_return_the_correct_integer(self):
        """ Should return the correct Integer from tcp flags """

        tcp_flags = TCPControlBits(['SYN', 'ACK'])
        assert_equal(tcp_flags.to_int(), 18)
