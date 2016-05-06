# -*- coding:utf-8 -*-
import logging

from networkapi.plugins.F5 import types
from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.profile import ProfileFastL4, ProfileHttp, ProfileTCP, ProfileUDP
from networkapi.plugins.F5.util import logger
from networkapi.util import valid_expression


log = logging.getLogger(__name__)


class VirtualServer(F5Base):

    __properties = None

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

        vip_rules = {
            'virtual_servers': list(),
            'rules': list()
        }

        vip_traffic_groups = {
            'virtual_addresses': list(),
            'traffic_groups': list()
        }

        tcp = ProfileTCP(self._lb)
        http = ProfileHttp(self._lb)
        fastl4 = ProfileFastL4(self._lb)
        udp = ProfileUDP(self._lb)
        profiles_list = tcp.get_list() + http.get_list() + fastl4.get_list() + udp.get_list()

        for vip_request in kwargs['vips']:

            self.__prepare_properties(vip_request, profiles_list)

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

            vip_profiles = self.__properties['profiles']

            # vip_rules['rules'].append(vip_request['rules'])

            if vip_request['optionsvip']['traffic_group']:
                vip_traffic_groups['virtual_addresses'].append(vip_request['address'])
                vip_traffic_groups['traffic_groups'].append(vip_request['optionsvip']['traffic_group'])

        self._lb._channel.System.Session.start_transaction()
        try:

            self.__profiles_timeout_create(
                profiles_timeout_tcp=self.__properties['profiles_timeout_tcp'],
                profiles_timeout_udp=self.__properties['profiles_timeout_udp'],
                profiles_timeout_fastl4=self.__properties['profiles_timeout_fastl4'])

            self._lb._channel.LocalLB.VirtualServer.create(
                definitions=vip_definitions,
                wildmasks=vip_wildmasks,
                resources=vip_resources,
                profiles=vip_profiles
            )

            # self.__add_rule(vip_rules)
            # self.__set_traffic_group(vip_traffic_groups)

            self.__set_snat(
                vip_snat_pool=self.__properties['vip_snat_pool'],
                vip_snat_auto=self.__properties['vip_snat_auto'],
                vip_snat_none=self.__properties['vip_snat_none'])

            self.__add_persistence_profile(self.__properties['profiles_persistence'])

            self.__set_translate_port_state(self.__properties['translate_port_state'])
        except Exception, e:
            self._lb._channel.System.Session.rollback_transaction()
            raise e
        else:
            self._lb._channel.System.Session.submit_transaction()

    @logger
    def update(self, **kwargs):
        virtual_servers = [vip_request['name'] for vip_request in kwargs['vips']]

        tcp = ProfileTCP(self._lb)
        http = ProfileHttp(self._lb)
        fastl4 = ProfileFastL4(self._lb)
        udp = ProfileUDP(self._lb)
        profiles_list = tcp.get_list() + http.get_list() + fastl4.get_list() + udp.get_list()
        current_profiles = self.__get_profile(virtual_servers=virtual_servers)

        profiles_to_delete = {
            'virtual_servers': list(),
            'profiles': list()
        }

        profiles_to_insert = {
            'virtual_servers': list(),
            'profiles': list()
        }

        resources = {
            'virtual_servers': list(),
            'pool': list()
        }

        vip_rules = {
            'virtual_servers': list(),
            'rules': list()
        }

        vip_traffic_groups = {
            'virtual_addresses': list(),
            'traffic_groups': list()
        }

        for idx, vip_request in enumerate(kwargs['vips']):

            self.__prepare_properties(vip_request, profiles_list)

            current_profiles[idx] = [{
                'profile_context': profile['profile_context'],
                'profile_name':profile['profile_name']
            } for profile in current_profiles[idx]]

            old_profiles = list()
            for profile in current_profiles[idx]:
                if not [prot for prot in ['tcp', 'udp', 'fastL4'] if prot in profile['profile_name']]:
                    if profile not in self.__properties['profiles'][idx] and profile:
                        old_profiles.append(profile)

            if old_profiles:
                profiles_to_delete['virtual_servers'].append(vip_request['name'])
                profiles_to_delete['profiles'].append(old_profiles)

            new_profiles = list()
            for profile in self.__properties['profiles'][idx]:
                if not [prot for prot in ['tcp', 'udp', 'fastL4'] if prot in profile['profile_name']]:
                    if profile not in current_profiles[idx]:
                        new_profiles.append(profile)

            if new_profiles:
                profiles_to_insert['virtual_servers'].append(vip_request['name'])
                profiles_to_insert['profiles'].append(new_profiles)

            resources['pool'].append(vip_request['pool'])

            # vip_rules['rules'].append(vip_request['rules'])

            if vip_request['optionsvip']['traffic_group']:
                vip_traffic_groups['traffic_groups'].append(vip_request['optionsvip']['traffic_group'])
                vip_traffic_groups['virtual_addresses'].append(vip_request['address'])

        self.__remove_profile(profiles_to_delete)
        self.__remove_all_persistence_profiles(virtual_servers)
        self.__remove_all_rule(virtual_servers)

        self.__profiles_timeout_create(
            profiles_timeout_tcp=self.__properties['profiles_timeout_tcp'],
            profiles_timeout_udp=self.__properties['profiles_timeout_udp'],
            profiles_timeout_fastl4=self.__properties['profiles_timeout_fastl4'])

        self.__add_profile(profiles_to_insert)

        resources['virtual_servers'] = virtual_servers
        vip_rules['virtual_servers'] = virtual_servers
        # self.__add_rule(vip_rules)
        self.__set_default_pool_name(resources)
        self.__set_traffic_group(vip_traffic_groups)

        self.__set_snat(
            vip_snat_pool=self.__properties['vip_snat_pool'],
            vip_snat_auto=self.__properties['vip_snat_auto'],
            vip_snat_none=self.__properties['vip_snat_none'])

        self.__add_persistence_profile(self.__properties['profiles_persistence'])

        self.__set_translate_port_state(self.__properties['translate_port_state'])

    @logger
    def __set_snat(self, **kwargs):
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
    def __add_persistence_profile(self, profiles_persistence):
        log.info(profiles_persistence)
        if profiles_persistence['virtual_servers']:
            self._lb._channel.LocalLB.VirtualServer.add_persistence_profile(
                virtual_servers=profiles_persistence['virtual_servers'],
                profiles=profiles_persistence['profiles']
            )

    @logger
    def __set_traffic_group(self, traffic_groups):
        if traffic_groups['virtual_addresses']:
            self._lb._channel.LocalLB.VirtualAddressV2.set_traffic_group(
                virtual_addresses=traffic_groups['virtual_addresses'],
                traffic_groups=traffic_groups['traffic_groups']
            )

    @logger
    def __set_translate_port_state(self, translate_port_state):
        if translate_port_state['virtual_servers']:
            self._lb._channel.LocalLB.VirtualAddressV2.set_translate_port_state(
                virtual_servers=translate_port_state['virtual_servers'],
                states=translate_port_state['states']
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

    @logger
    def __set_default_pool_name(self, resources):

        self._lb._channel.LocalLB.VirtualServer.set_default_pool_name(
            virtual_servers=resources['virtual_servers'],
            default_pools=resources['pool']
        )

    @logger
    def __add_rule(self, rules):
        if rules['virtual_servers']:
            version_split = self._lb._version[8:len(self._lb._version)].split('.')
            # old version
            if version_split[0] == '11' and int(version_split[1]) <= 2:
                self._lb._channel.LocalLB.VirtualServer.add_rule(
                    virtual_servers=rules['virtual_servers'],
                    rules=rules['rules']
                )
            else:
                self._lb._channel.LocalLB.VirtualServer.add_related_rule(
                    virtual_servers=rules['virtual_servers'],
                    rules=rules['rules']
                )

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

    @logger
    def __remove_all_rule(self, virtual_servers):
        version_split = self._lb._version[8:len(self._lb._version)].split('.')
        # old version
        if version_split[0] == '11' and int(version_split[1]) <= 2:
            self._lb._channel.LocalLB.VirtualServer.remove_all_rules(
                virtual_servers=virtual_servers
            )
        else:
            self._lb._channel.LocalLB.VirtualServer.remove_all_related_rules(
                virtual_servers=virtual_servers
            )

    @logger
    def __get_profile(self, virtual_servers):

        profiles = self._lb._channel.LocalLB.VirtualServer.get_profile(
            virtual_servers=virtual_servers
        )
        return profiles

    @logger
    def __remove_profile(self, profiles):
        if profiles['virtual_servers']:
            self._lb._channel.LocalLB.VirtualServer.remove_profile(
                virtual_servers=profiles['virtual_servers'],
                profiles=profiles['profiles']
            )

    @logger
    def __add_profile(self, profiles):
        if profiles['virtual_servers']:
            self._lb._channel.LocalLB.VirtualServer.add_profile(
                virtual_servers=profiles['virtual_servers'],
                profiles=profiles['profiles']
            )

    @logger
    def __remove_all_persistence_profiles(self, virtual_servers):

        self._lb._channel.LocalLB.VirtualServer.remove_all_persistence_profiles(
            virtual_servers=virtual_servers
        )

    def __prepare_properties(self, vip_request, profiles_list, update=False):

        self.__properties = {

            'profiles': list(),
            'profiles_timeout_tcp': {
                'profile_names': list(),
                'timeouts': list()
            },
            'profiles_timeout_udp': {
                'profile_names': list(),
                'timeouts': list()
            },
            'profiles_timeout_fastl4': {
                'profile_names': list(),
                'timeouts': list()
            },
            'profiles_persistence': {
                'virtual_servers': list(),
                'profiles': list()
            },
            'translate_port_state': {
                'virtual_servers': list(),
                'states': list()
            },
            'vip_snat_auto': {
                'virtual_servers': list()
            },
            'vip_snat_none': {
                'virtual_servers': list()
            },
            'vip_snat_pool': {
                'virtual_servers': list(),
                'pools': list()
            }
        }

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

                        if validated:
                            use = condicional.get('use')
                            for item in use:
                                if item.get('type') == 'profile':
                                    profile_name = item.get('value')
                                    if '$' in profile_name:
                                        try:
                                            pn = profile_name.split('$')
                                            time_profie = int(vip_request['optionsvip']['timeout']['nome_opcao_txt']) * 60
                                            profile_name = pn[0] + str(time_profie)
                                            if '/Common/' + profile_name not in profiles_list:
                                                if 'tcp' in profile_name and profile_name not in self.__properties['profiles_timeout_tcp']['profile_names']:
                                                    self.__properties['profiles_timeout_tcp']['profile_names'].append(profile_name)
                                                    self.__properties['profiles_timeout_tcp']['timeouts'].append({
                                                        'value': time_profie,
                                                        'default_flag': 0
                                                    })
                                                elif 'udp' in profile_name and profile_name not in self.__properties['profiles_timeout_udp']['profile_names']:
                                                    self.__properties['profiles_timeout_udp']['profile_names'].append(profile_name)
                                                    self.__properties['profiles_timeout_udp']['timeouts'].append({
                                                        'value': time_profie,
                                                        'default_flag': 0
                                                    })
                                                elif 'fastL4' in profile_name and profile_name not in self.__properties['profiles_timeout_fastl4']['profile_names']:
                                                    self.__properties['profiles_timeout_fastl4']['profile_names'].append(profile_name)
                                                    self.__properties['profiles_timeout_fastl4']['timeouts'].append({
                                                        'value': time_profie,
                                                        'default_flag': 0
                                                    })
                                        except:
                                            if '/Common/' + profile_name not in profiles_list:
                                                raise Exception(u'Profile %s nao existe')
                                            pass
                                    profiles.append({
                                        'profile_name': '/Common/' + profile_name,
                                        'profile_context': 'PROFILE_CONTEXT_TYPE_ALL'
                                    })

                                elif item.get('type') == 'snat':
                                    if item.get('value') == 'automap':
                                        self.__properties['vip_snat_auto']['virtual_servers'].append(vip_request['name'])
                                    elif item.get('type') == '':
                                        self.__properties['vip_snat_none']['virtual_servers'].append(vip_request['name'])
                                    else:
                                        self.__properties['vip_snat_pool']['virtual_servers'].append(vip_request['name'])
                                        self.__properties['vip_snat_pool']['pools'].append(item.get('value'))

                                elif item.get('type') == 'persistence':
                                    if item.get('value'):
                                        profile = [{
                                            'profile_name': item.get('value'),
                                            'default_profile': 1
                                        }]
                                        self.__properties['profiles_persistence']['virtual_servers'].append(vip_request['name'])
                                        self.__properties['profiles_persistence']['profiles'].append(profile)

                                elif item.get('type') == 'translate_port_state':
                                    self.__properties['translate_port_state']['virtual_servers'].append(vip_request['name'])
                                    self.__properties['translate_port_state']['states'].append(item.get('value'))

                            break
        self.__properties['profiles'].append(profiles)
