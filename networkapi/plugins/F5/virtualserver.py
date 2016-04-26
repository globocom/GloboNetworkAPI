# -*- coding:utf-8 -*-
import logging

from networkapi.plugins.F5 import types
from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.profile import ProfileFastL4, ProfileHttp, ProfileTCP, ProfileUDP
from networkapi.util import logger, valid_expression


log = logging.getLogger(__name__)


class VirtualServer(F5Base):

    @logger
    def delete(self, **kwargs):
        self._lb._channel.LocalLB.VirtualServer.delete_virtual_server(
            virtual_servers=kwargs['vps_names']
        )

    @logger
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
            log.info('optionsvip_extended:%s' % vip_request['optionsvip_extended'])
            profiles = list()

            if vip_request['optionsvip_extended']:
                requiments = vip_request['optionsvip_extended'].get('requiments')
                if requiments:
                    for requiment in requiments:
                        condicionals = requiment.get('condicionals')
                        for condicional in condicionals:

                            validated = True

                            validations = condicional.get('validations')
                            for validation in validations:
                                if validation.get('type') == 'optionvip':
                                    validated &= valid_expression(
                                        validation.get('operator'),
                                        int(vip_request['optionsvip'][validation.get('variable')]['id']),
                                        int(validation.get('value'))
                                    )
                                    log.info(vip_request['optionsvip'][validation.get('variable')]['id'])
                                    log.info(validation.get('value'))

                            if validated:
                                use = condicional.get('use')
                                for item in use:
                                    if item.get('type') == 'profile':
                                        profile_name = item.get('value')
                                        try:
                                            pn = profile_name.split('$')
                                            time_profie = int(vip_request['optionsvip']['timeout']['nome_opcao_txt']) * 60
                                            profile_name = pn[0] + str(time_profie)
                                            if '/Common/' + profile_name not in profiles_list:
                                                if 'tcp' in profile_name:
                                                    profiles_timeout_tcp['profile_names'].append(profile_name)
                                                    profiles_timeout_tcp['timeouts'].append({
                                                        'value': time_profie,
                                                        'default_flag': 0
                                                    })
                                                elif 'udp' in profile_name:
                                                    profiles_timeout_udp['profile_names'].append(profile_name)
                                                    profiles_timeout_udp['timeouts'].append({
                                                        'value': time_profie,
                                                        'default_flag': 0
                                                    })
                                                elif 'fastL4' in profile_name:
                                                    profiles_timeout_fastl4['profile_names'].append(profile_name)
                                                    profiles_timeout_fastl4['timeouts'].append({
                                                        'value': time_profie,
                                                        'default_flag': 0
                                                    })
                                        except:
                                            if '/Common/' + profile_name not in profiles_list:
                                                raise Exception(u'Profile %s nao existe')
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
                'protocol': types.procotol_type(vip_request['optionsvip']['l4_protocol']['nome_opcao_txt'].lower())
            })

            vip_wildmasks.append('255.255.255.255')

            vip_resources.append({
                'type': 'RESOURCE_TYPE_POOL',
                'default_pool_name': vip_request['pool']
            })

            vip_profiles.append(profiles)

        try:
            self._lb._channel.System.Session.start_transaction()

            self.__profiles_timeout_create(
                profiles_timeout_tcp=profiles_timeout_tcp,
                profiles_timeout_udp=profiles_timeout_udp,
                profiles_timeout_fastl4=profiles_timeout_fastl4)
            self._lb._channel.LocalLB.VirtualServer.create(
                definitions=vip_definitions,
                wildmasks=vip_wildmasks,
                resources=vip_resources,
                profiles=vip_profiles
            )
            self.__snat(
                vip_snat_pool=vip_snat_pool,
                vip_snat_auto=vip_snat_auto,
                vip_snat_none=vip_snat_none)

            self.__add_persistence_profile(profiles_persistence=profiles_persistence)

            self.__translate_port_state(translate_port_state=translate_port_state)
        except Exception, e:
            raise e
        else:
            self._lb._channel.System.Session.submit_transaction()

    @logger
    def __snat(self, **kwargs):
        version_split = self._lb._version[8:len(self._lb._version)].split('.')
        # old version
        if version_split[0] == '11' and int(version_split[1]) <= 2:

            if kwargs.get('vip_snat_auto').get('virtual_servers'):
                self._lb._channel.LocalLB.VirtualServer.set_snat_automap(
                    virtual_servers=kwargs.get('vip_snat_auto').get('virtual_servers')
                )
            if kwargs.get('vip_snat_pool').get('virtual_servers'):
                self._lb._channel.LocalLB.VirtualServer.set_snat_pool(
                    virtual_servers=kwargs.get('vip_snat_pool').get('virtual_servers'),
                    pools=kwargs.get('vip_snat_pool').get('pools')
                )
            if kwargs.get('vip_snat_none').get('virtual_servers'):
                self._lb._channel.LocalLB.VirtualServer.set_snat_none(
                    virtual_servers=kwargs.get('vip_snat_none').get('virtual_servers')
                )
        else:
            if kwargs.get('vip_snat_auto').get('virtual_servers'):
                self._lb._channel.LocalLB.VirtualServer.set_source_address_translation_automap(
                    virtual_servers=kwargs.get('vip_snat_auto').get('virtual_servers')
                )
            if kwargs.get('vip_snat_pool').get('virtual_servers'):
                self._lb._channel.LocalLB.VirtualServer.set_source_address_translation_lsn_pool(
                    virtual_servers=kwargs.get('vip_snat_pool').get('virtual_servers'),
                    pools=kwargs.get('vip_snat_pool').get('pools')
                )
            if kwargs.get('vip_snat_none').get('virtual_servers'):
                self._lb._channel.LocalLB.VirtualServer.set_source_address_translation_none(
                    virtual_servers=kwargs.get('vip_snat_none').get('virtual_servers')
                )

    @logger
    def __add_persistence_profile(self, **kwargs):
        if kwargs['profiles_persistence']['virtual_servers']:
            self._lb._channel.LocalLB.VirtualServer.add_persistence_profile(
                virtual_servers=kwargs['profiles_persistence']['virtual_servers'],
                profiles=kwargs['profiles_persistence']['profiles']
            )

    @logger
    def set_traffic_group(self, **kwargs):
        self._lb._channel.LocalLB.VirtualAddressV2.set_traffic_group(
            virtual_addresses=kwargs['virtual_addresses'],
            traffic_groups=kwargs['traffic_groups']
        )

    @logger
    def __translate_port_state(self, **kwargs):
        if kwargs['translate_port_state']['virtual_servers']:
            self._lb._channel.LocalLB.VirtualAddressV2.set_translate_port_state(
                virtual_servers=kwargs['translate_port_state']['virtual_servers'],
                states=kwargs['translate_port_state']['states']
            )

    @logger
    def __profiles_timeout_create(self, **kwargs):
        if kwargs['profiles_timeout_tcp']['profile_names']:
            ptcp = ProfileTCP(self._lb)
            ptcp.create(profile_names=kwargs['profiles_timeout_tcp']['profile_names'])
            ptcp.set_idle_timeout(
                profile_names=kwargs['profiles_timeout_tcp']['profile_names'],
                timeouts=kwargs['profiles_timeout_tcp']['timeouts'],
            )
        if kwargs['profiles_timeout_udp']['profile_names']:
            pudp = ProfileUDP(self._lb)
            pudp.create(profile_names=kwargs['profiles_timeout_udp']['profile_names'])
            pudp.set_idle_timeout(
                profile_names=kwargs['profiles_timeout_udp']['profile_names'],
                timeouts=kwargs['profiles_timeout_udp']['timeouts'],
            )
        if kwargs['profiles_timeout_fastl4']['profile_names']:
            pfl4 = ProfileFastL4(self._lb)
            pfl4.create(profile_names=kwargs['profiles_timeout_fastl4']['profile_names'])
            pfl4.set_idle_timeout(
                profile_names=kwargs['profiles_timeout_fastl4']['profile_names'],
                timeouts=kwargs['profiles_timeout_fastl4']['timeouts'],
            )

    # @logger
    # def __add_rule(self, **kwargs):
    #     version_split = self._lb._version[8:len(self._lb._version)].split('.')
    #     # old version
    #     if version_split[0] == '11' and int(version_split[1]) <= 2:
    #         self._lb._channel.LocalLB.VirtualServer.add_rule(
    #             virtual_servers=,
    #             rules=
    #         )
    #     else:
    #         self._lb._channel.LocalLB.VirtualServer.add_related_rule(
    #             virtual_servers=,
    #             rules=
    #         )

    # @logger
    # def __get_rule(self, **kwargs):
    #     version_split = self._lb._version[8:len(self._lb._version)].split('.')
    #     # old version
    #     if version_split[0] == '11' and int(version_split[1]) <= 2:
    #         self._lb._channel.LocalLB.VirtualServer.get_rule(
    #             virtual_servers=
    #         )
    #     else:
    #         self._lb._channel.LocalLB.VirtualServer.get_related_rule(
    #             virtual_servers=
    #         )
