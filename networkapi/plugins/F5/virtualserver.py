import logging

from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.profile import ProfileFastL4, ProfileHttp, ProfileTCP, ProfileUDP
from networkapi.util import valid_expression


log = logging.getLogger(__name__)


class VirtualServer(F5Base):

    def create(self, **kwargs):

        vip_definitions = list()
        vip_wildmasks = list()
        vip_resources = list()
        vip_profiles = list()

        profiles_timeout_tcp = {
            'profile_names': list(),
            'timeouts': list()
        }
        profiles_timeout_udp = {
            'profile_names': list(),
            'timeouts': list()
        }
        profiles_timeout_fastl4 = {
            'profile_names': list(),
            'timeouts': list()
        }

        profiles_persistence = {
            'virtual_servers': list(),
            'profiles': list()
        }

        translate_port_state = {
            'virtual_servers': list(),
            'states': list()
        }

        vip_snat_auto = {
            'virtual_servers': list()
        }
        vip_snat_none = {
            'virtual_servers': list()
        }
        vip_snat_pool = {
            'virtual_servers': list(),
            'pools': list()
        }

        tcp = ProfileTCP(self._lb)
        http = ProfileHttp(self._lb)
        fastl4 = ProfileFastL4(self._lb)
        udp = ProfileUDP(self._lb)
        profiles_list = tcp.get_list() + http.get_list() + fastl4.get_list() + udp.get_list()

        for vip_request in kwargs['vips']:

            profiles = list()

            if kwargs['conf']['optionsvip_extended']:
                requiments = kwargs['conf']['optionsvip_extended'].get('requiments')
                if requiments:
                    for requiment in requiments:
                        condicionals = requiment.get('condicionals')
                        for condicional in condicionals:

                            validated = True

                            validations = condicional.get('validations')
                            for validation in validations:
                                if validation.get('type') == 'optionvip':
                                    vip_request['optionsvip'][validation.get('variable')]
                                    validated &= valid_expression(
                                        validation.get('operator'),
                                        vip_request['optionsvip'][validation.get('variable')],
                                        validation.get('value')
                                    )

                            if validated:
                                use = condicional.get('use')
                                for item in use:
                                    if item.get('type') == 'profile':
                                        profile_name = item.get('value')
                                        try:
                                            pn = profile_name.split('$')
                                            profile_name = pn[0] + vip_request['optionsvip']['timeout']
                                            if '/Common/' + profile_name not in profiles_list:
                                                if 'tcp' in profile_name:
                                                    profiles_timeout_tcp['profile_names'].append(profile_name)
                                                    profiles_timeout_tcp['timeouts'].append({
                                                        'value': vip_request['optionsvip']['timeout'],
                                                        'default_flag': 1
                                                    })
                                                elif 'udp' in profile_name:
                                                    profiles_timeout_udp['profile_names'].append(profile_name)
                                                    profiles_timeout_udp['timeouts'].append({
                                                        'value': vip_request['optionsvip']['timeout'],
                                                        'default_flag': 1
                                                    })
                                                elif 'fastL4' in profile_name:
                                                    profiles_timeout_fastl4['profile_names'].append(profile_name)
                                                    profiles_timeout_fastl4['timeouts'].append({
                                                        'value': vip_request['optionsvip']['timeout'],
                                                        'default_flag': 1
                                                    })
                                        except:
                                            if '/Common/' + profile_name not in profiles_list:
                                                raise Exception('Profile %s não existe')
                                            pass
                                        profiles.append({
                                            'profile_context': 'PROFILE_CONTEXT_TYPE_ALL',
                                            'profile_name': profile_name
                                        })

                                    elif item.get('type') == 'snat':
                                        if item.get('value') == 'automap':
                                            vip_snat_auto['virtual_servers'].append(vip_request['name'])
                                        elif item.get('type') == '':
                                            vip_snat_none['virtual_servers'].append(vip_request['name'])
                                        else:
                                            vip_snat_pool['virtual_servers'].append(vip_request['name'])
                                            vip_snat_pool['pools'].append(item.get('value'))

                                    elif item.get('type') == 'persistence':
                                        if item.get('value'):
                                            profile = {
                                                'profile_name': item.get('value'),
                                                'default_profile': 1
                                            }
                                            profiles_persistence['virtual_servers'].append(vip_request['name'])
                                            profiles_persistence['profiles'].append(profile)

                                    elif item.get('type') == 'translate_port_state':
                                        translate_port_state['virtual_servers'].append(vip_request['name'])
                                        translate_port_state['states'].append(item.get('value'))

                                break

            vip_definitions.append({
                'name': vip_request['name'],
                'address': vip_request['address'],
                'port': vip_request['port'],
                'protocol': vip_request['optionsvip']['protocol_l4']
            })

            vip_wildmasks.append('255.255.255.255')

            vip_resources.append({
                'type': 'RESOURCE_TYPE_POOL',
                'default_pool_name': vip_request['pool']
            })

            vip_profiles.append(profiles)

        self.__snat(
            vip_snat_pool=vip_snat_pool,
            vip_snat_auto=vip_snat_auto,
            vip_snat_none=vip_snat_none)

        self.__profiles_timeout_create(
            profiles_timeout_tcp=profiles_timeout_tcp,
            profiles_timeout_udp=profiles_timeout_udp,
            profiles_timeout_fastl4=profiles_timeout_fastl4)

        self.__add_profiles_persistence(profiles_persistence=profiles_persistence)

        self.__translate_port_state(translate_port_state=translate_port_state)

        self._lb._channel.VirtualServer.create(
            definitions=vip_definitions,
            wildmasks=vip_wildmasks,
            resources=vip_resources,
            profiles=vip_profiles
        )

    def __snat(self, **kwargs):

        version_split = self._version[8:len(self._version)].split('.')
        # old version
        if version_split[0] == '11' and int(version_split[1]) <= 2:

            if kwargs.get('vip_snat_auto').get('virtual_servers'):
                self._lb._channel.VirtualServer.set_snat_automap(
                    kwargs.get('vip_snat_auto')
                )
            if kwargs.get('vip_snat_pool').get('virtual_servers'):
                self._lb._channel.VirtualServer.set_snat_pool(
                    kwargs.get('vip_snat_pool')
                )
            if kwargs.get('vip_snat_none').get('virtual_servers'):
                self._lb._channel.VirtualServer.set_snat_none(
                    kwargs.get('vip_snat_none')
                )
        else:
            if kwargs.get('vip_snat_auto').get('virtual_servers'):
                self._lb._channel.VirtualServer.set_source_address_translation_automap(
                    kwargs.get('vip_snat_auto')
                )
            if kwargs.get('vip_snat_pool').get('virtual_servers'):
                self._lb._channel.VirtualServer.set_source_address_translation_lsn_pool(
                    kwargs.get('vip_snat_pool')
                )
            if kwargs.get('vip_snat_none').get('virtual_servers'):
                self._lb._channel.VirtualServer.set_source_address_translation_none(
                    kwargs.get('vip_snat_none')
                )

    def __add_persistence_profile(self, **kwargs):
        self._lb._channel.VirtualServer.add_persistence_profile(
            virtual_servers=kwargs['virtual_servers'],
            profiles=kwargs['profiles']
        )

    def set_traffic_group(self, **kwargs):

        self._lb._channel.VirtualAddressV2.set_traffic_group(
            virtual_addresses=kwargs['virtual_addresses'],
            traffic_groups=kwargs['traffic_groups']
        )

    def __translate_port_state(self, **kwargs):
        self._lb._channel.VirtualAddressV2.set_translate_port_state(
            virtual_servers=kwargs['translate_port_state'],
            states=kwargs['translate_port_state']
        )

    def __profiles_timeout_create(self, **kwargs):
        if kwargs['profiles_timeout_tcp']:
            ProfileTCP.create(kwargs)
            ProfileTCP.set_idle_timeout(kwargs)
        if kwargs['profiles_timeout_udp']:
            ProfileUDP.create(kwargs)
            ProfileUDP.set_idle_timeout(kwargs)
        if kwargs['profiles_timeout_fastl4']:
            ProfileFastL4.create(kwargs)
            ProfileFastL4.set_idle_timeout(kwargs)
