

from nose.tools import assert_raises
from nose.tools import assert_equal
from nose.tools import assert_in
from nose.tools import assert_not_in

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder


class ACLFlowBuilderTestCase(NetworkApiTestCase):
    """ Class to test ACL Flow Builder """

    def setUp(self):
        self.input_file_path = 'input/{}.json'
        self.output_file_path = 'output/{}/chunk_{}.json'
        self.general_builder_path = 'plugins/SDN/ODL/json/builder/'


        self.tcp_path = self.general_builder_path +  'tcp/'
        self.tcp_input_path = self.tcp_path + self.input_file_path
        self.tcp_output_path = self.tcp_path + self.output_file_path

        self.udp_path = self.general_builder_path + 'udp/'
        self.udp_input_path = self.udp_path + self.input_file_path
        self.udp_output_path = self.udp_path + self.output_file_path

        self.mixed_path = self.general_builder_path + 'mixed/'
        self.mixed_input_path = self.mixed_path + self.input_file_path
        self.mixed_output_path = self.mixed_path + self.output_file_path

    def test_build_acl_tcp_double_range(self):
        """ Build flows from TCP Double Range ACL."""

        type_ = 'double_range'
        input_ = self.tcp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path

        generator = flow_builder.build()

        limit_ = 3
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_tcp_eq_src_eq_dst(self):
        """ Build flows from TCP eq source and eq destination ACL."""

        type_ = 'eq_src_eq_dst'
        input_ = self.tcp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_tcp_range_dst(self):
        """ Build flows from TCP range destination ACL."""

        type_ = 'range_dst'
        input_ = self.tcp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_tcp_range_dst_eq_src(self):
        """ Build flows from TCP range destination and source eq ACL."""

        type_ = 'range_dst_eq_src'
        input_ = self.tcp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_tcp_range_src(self):
        """ Build flows from TCP range source ACL."""

        type_ = 'range_src'
        input_ = self.tcp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_tcp_range_src_eq_dst(self):
        """ Build flows from TCP range source and destination eq ACL."""

        type_ = 'range_src_eq_dst'
        input_ = self.tcp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.tcp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_udp_double_range(self):
        """ Build flows from UDP Double Range ACL."""

        type_ = 'double_range'
        input_ = self.udp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.udp_output_path

        generator = flow_builder.build()

        limit_ = 3
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_udp_eq_src_eq_dst(self):
        """ Build flows from UDP eq source and eq destination ACL."""

        type_ = 'eq_src_eq_dst'
        input_ = self.udp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.udp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_udp_range_dst(self):
        """ Build flows from UDP range destination ACL."""

        type_ = 'range_dst'
        input_ = self.udp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.udp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_udp_range_dst_eq_src(self):
        """ Build flows from UDP range destination and source eq ACL."""

        type_ = 'range_dst_eq_src'
        input_ = self.udp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.udp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_udp_range_src(self):
        """ Build flows from UDP range source ACL."""

        type_ = 'range_src'
        input_ = self.udp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.udp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_acl_udp_range_src_eq_dst(self):
        """ Build flows from UDP range source and destination eq ACL."""

        type_ = 'range_src_eq_dst'
        input_ = self.udp_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.udp_output_path

        generator = flow_builder.build()

        limit_ = 1
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_1tcp_range_dst_eq_src_3icmp_1ip_1udp_range_dst\
        (self):
        """ Build set of ACLs with 1 TCP Range Destination and Eq Source,
            3 ICMP, 1 IP and 1 UDP Range Destination.
        """
        type_ = '1tcp_range_dst_eq_src+3icmp+1ip+1udp_range_dst'
        input_ = self.mixed_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path

        generator = flow_builder.build()

        limit_ = 3
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_1tcp_range_src_eq_dst_4icmp_1ip_1udp_double_range\
        (self):
        """ Build set of ACLs with 1 TCP Range Source and Eq Destination,
            4 ICMP, 1 IP and 1 UDP Double Range.
        """

        type_ = '1tcp_range_src_eq_dst+4icmp+1ip+1udp_double_range'
        input_ = self.mixed_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path

        generator = flow_builder.build()

        limit_ = 5
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_1udp_1udp_range_src_2icmp_1tcp_src_eq(self):
        """ Build set of ACLs with 1 UDP, 1 UDP Range Source, 2 ICMP and
            1 TCP Source Eq.
        """

        type_ = '1udp+1udp_range_src+2icmp+1tcp_src_eq'
        input_ = self.mixed_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path

        generator = flow_builder.build()

        limit_ = 2
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)

    def test_build_2ip_1udp_3tcp_src_eq_dst_eq_1udp_double_range\
        (self):
        """ Build set of ACLs with 2 IP, 1 UDP, 3 TCP Source Eq Destination Eq
            and 1 UDP Double Range.
        """

        type_ = '2ip+1udp+3tcp_src_eq_dst_eq+1udp_double_range'
        input_ = self.mixed_input_path.format(type_)
        data = self.load_json_file(input_)
        flow_builder = AclFlowBuilder(data)

        output_path = self.mixed_output_path

        generator = flow_builder.build()

        limit_ = 5
        for i in xrange(1, limit_ + 1):
            output_ = output_path.format(type_, i)
            self.compare_json(output_, generator.next())

        self.assertRaises(StopIteration, generator.next)