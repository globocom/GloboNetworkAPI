from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

map_fields = {
    'remote_ip': 'neighbor-router',
    'remote_as': 'remote-as' ,
    'password' : 'password',
    'maximum_hops': 'ebgp-multihop',
    'timer_keepalive': {
        'timers': 'keepalive'
    },
    'timer_timeout': {
        'timers': 'hold-time'
    },
    'description': 'description',
    'soft_reconfiguration': 'soft-reconfiguration',
    'community': 'send-community',
    'remove_private_as': 'remove-private-as',
    'next_hop_self': 'next-hop-self'
}

class Generic(object):

    def treat_neighbor(self, neighbor):

        if neighbor['soft_reconfiguration'] == 0:
            del neighbor['soft_reconfiguration']

        if neighbor['community'] == 0:
            del neighbor['community']

    def json_to_xml(self, neighbor):

        neighbor = self.treat_neighbor(neighbor)

        bgp_xml = Element('bgp')

        as_xml = SubElement(bgp_xml, 'as-name')
        as_xml.text = '65114'
        neighbor_xml = SubElement(bgp_xml, 'neighbor')

        for field in neighbor:

            if isinstance(map_fields[field], basestring):

                child_xml = SubElement(neighbor_xml, map_fields[field])
                child_xml.text = self._to_str(neighbor[field])

            elif isinstance(map_fields[field], dict):

                for child in map_fields[field]:

                    child_xml = self._create_or_get_element(neighbor_xml,
                                                                child)

                    child_of_child_xml = SubElement(child_xml,
                                                    map_fields[field][child])
                    child_of_child_xml.text = self._to_str(neighbor[field])



        return tostring(bgp_xml)

    def _create_or_get_element(self, root, tag):

        if root.find(tag) is not None:
            return root.find(tag)
        else:
            return SubElement(root, tag)

    def _to_str(self, value):

        if isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

    def deploy_neighbor(self):

        pass

    def undeploy_neighbor(self):

        pass

