# -*- coding: utf-8 -*-

from collections import OrderedDict


class TCPControlBits(object):
    """ Class to handle all format of the TCP IP control bits """

    def __init__(self, flags_list=None):
        """ A list of strings representing the TCP flags is expected """

        if flags_list is None:
            raise ValueError("No bits list received")

        self.control_bits = OrderedDict([
            ("CWR", 0),
            ("ECE", 0),
            ("URG", 0),
            ("ACK", 0),
            ("PSH", 0),
            ("RST", 0),
            ("SYN", 0),
            ("FIN", 0)
        ])

        self._build_bits(flags_list)

    def _build_bits(self, flags_list):
        """ Matches which flags are On """

        for flag in flags_list:
            if flag in self.control_bits:
                self.control_bits[flag] = 1

    def to_dict(self):
        return dict(self.control_bits)

    def to_list(self):
        return self.control_bits.values()

    def to_str(self):
        return "".join([str(bit) for bit in self.to_list()])

    def to_int(self):
        return int(self.to_str(), 2)

    def to_bin(self):
        return bin(self.to_int())

    def to_hex(self):
        return hex(self.to_int())
