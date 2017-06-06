

from nose.tools import assert_raises
from nose.tools import assert_equal
from nose.tools import assert_in
from nose.tools import assert_not_in

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder


class ACLFlowBuilderTestCase(NetworkApiTestCase):
    """ Class to test ACL Flow Builder """

    def setUp(self):
        self.tcp_path = 'networkapi/plugins/SDN/ODL/json/builder/tcp/'
        self.tcp_input_path = self.tcp_path + 'input/{}.json'
        self.tcp_output_path = self.tcp_path + 'output/'

        self.mixed_path = 'networkapi/plugins/SDN/ODL/json/builder/mixed/'
        self.mixed_input_path = self.mixed_path + 'input/{}.json'
        self.mixed_output_path = self.mixed_path + 'output/'

    def test_build_acl_tcp_double_range(self):
        """ Build flows from TCP Double Range ACL."""

        input_ = self.tcp_input_path.format('double_range')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path + 'double_range/chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(2)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(3)
        self.compare_json(output_, generator.next())

    def test_build_acl_tcp_eq_src_eq_dst(self):
        """ Build flows from TCP eq source and eq destination ACL."""

        input_ = self.tcp_input_path.format('eq_src_eq_dst')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path + 'eq_src_eq_dst/chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

    def test_build_acl_tcp_range_dst(self):
        """ Build flows from TCP range destination ACL."""

        input_ = self.tcp_input_path.format('range_dst')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path + 'range_dst/chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

    def test_build_acl_tcp_range_dst_eq_src(self):
        """ Build flows from TCP range destination and source eq ACL."""

        input_ = self.tcp_input_path.format('range_dst_eq_src')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path + 'range_dst_eq_src/chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

    def test_build_acl_tcp_range_src(self):
        """ Build flows from TCP range source ACL."""

        input_ = self.tcp_input_path.format('range_src')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path + 'range_src/chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

    def test_build_acl_tcp_range_src_eq_dst(self):
        """ Build flows from TCP range source and destination eq ACL."""

        input_ = self.tcp_input_path.format('range_src_eq_dst')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path + 'range_src_eq_dst/chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

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

        input_ = self.mixed_input_path.format('1tcp_range_dst_eq_src+'
                                              '3icmp+1ip+1udp_range_dst')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path + '1tcp_range_dst_eq_src+' \
                                               '3icmp+1ip+1udp_range_dst/' \
                                               'chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(2)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(3)
        self.compare_json(output_, generator.next())

    def test_build_1tcp_range_src_eq_dst_4icmp_1ip_1udp_double_range\
        (self):
        """ Build set of ACLs with 1 TCP Range Source and Eq Destination,
            4 ICMP, 1 IP and 1 UDP Double Range.
        """

        input_ = self.mixed_input_path.format('1tcp_range_src_eq_dst+'
                                              '4icmp+1ip+1udp_double_range')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path + '1tcp_range_src_eq_dst+' \
                                               '4icmp+1ip+1udp_double_range/' \
                                               'chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(2)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(3)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(4)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(5)
        self.compare_json(output_, generator.next())

    def test_build_1udp_1udp_range_src_2icmp_1tcp_src_eq(self):
        """ Build set of ACLs with 1 UDP, 1 UDP Range Source, 2 ICMP and
            1 TCP Source Eq.
        """

        input_ = self.mixed_input_path.format('1udp+1udp_range_src+'
                                              '2icmp+1tcp_src_eq')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path + '1udp+1udp_range_src+' \
                                               '2icmp+1tcp_src_eq/' \
                                               'chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(2)
        self.compare_json(output_, generator.next())

    def test_build_2ip_1udp_3tcp_src_eq_dst_eq_1udp_double_range\
        (self):
        """ Build set of ACLs with 2 IP, 1 UDP, 3 TCP Source Eq Destination Eq
            and 1 UDP Double Range.
        """

        input_ = self.mixed_input_path.format('2ip+1udp+3tcp_src_eq_dst_eq+'
                                              '1udp_double_range')
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path + '2ip+1udp+3tcp_src_eq_dst_eq+' \
                                               '1udp_double_range/' \
                                               'chunk_{}.json'

        generator = flow_builder.build()

        output_ = output_path.format(1)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(2)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(3)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(4)
        self.compare_json(output_, generator.next())

        output_ = output_path.format(5)
        self.compare_json(output_, generator.next())

'
''
''