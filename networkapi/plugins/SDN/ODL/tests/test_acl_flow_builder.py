

from nose.tools import assert_raises
from nose.tools import assert_equal
from nose.tools import assert_in
from nose.tools import assert_not_in

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder


class ACLFlowBuilderTestCase(NetworkApiTestCase):
    """ Class to test ACL Flow Builder """

    def test_build_acl_tcp_double_range(self):
        """ Build flows from TCP Double Range ACL."""

    def test_build_acl_tcp_eq_src_eq_dst(self):
        """ Build flows from TCP eq source and eq destination ACL."""

    def test_build_acl_tcp_range_dst(self):
        """ Build flows from TCP range destination ACL."""

    def test_build_acl_tcp_range_dst_eq_src(self):
        """ Build flows from TCP range destination and source eq ACL."""

    def test_build_acl_tcp_range_src(self):
        """ Build flows from TCP range source ACL."""

    def test_build_acl_tcp_range_src_eq_dst(self):
        """ Build flows from TCP range source and destination eq ACL."""

    def test_build_acl_udp_double_range(self):
        """ Build flows from UDP Double Range ACL."""

    def test_build_acl_udp_eq_src_eq_dst(self):
        """ Build flows from UDP eq source and eq destination ACL."""

    def test_build_acl_udp_range_dst(self):
        """ Build flows from UDP range destination ACL."""

    def test_build_acl_udp_range_dst_eq_src(self):
        """ Build flows from UDP range destination and source eq ACL."""

    def test_build_acl_udp_range_src(self):
        """ Build flows from UDP range source ACL."""

    def test_build_acl_udp_range_src_eq_dst(self):
        """ Build flows from UDP range source and destination eq ACL."""

    def test_build_1tcp_range_dst_eq_src_3icmp_1ip_1udp_range_dst\
        (self):
        """ Build set of ACLs with 1 TCP Range Destination and Eq Source,
            3 ICMP, 1 IP and 1 UDP Range Destination.
        """

    def test_build_1tcp_range_src_eq_dst_4icmp_1ip_1udp_double_range\
        (self):
        """ Build set of ACLs with 1 TCP Range Source and Eq Destination,
            4 ICMP, 1 IP and 1 UDP Double Range.
        """

    def test_build_1udp_1udp_range_src_2icmp_1tcp_src_eq(self):
        """ Build set of ACLs with 1 UDP, 1 UDP Range Source, 2 ICMP and
            1 TCP Source Eq.
        """

    def test_build_2ip_1udp_3tcp_src_eq_dst_eq_1udp_double_range\
        (self):
        """ Build set of ACLs with 2 IP, 1 UDP, 3 TCP Source Eq Destination Eq
            and 1 UDP Double Range.
        """