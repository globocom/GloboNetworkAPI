# -*- coding:utf-8 -*-
import logging

from networkapi.plugins.F5 import pool
from networkapi.plugins.F5 import rule
from networkapi.plugins.F5 import types
from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.profile import ProfileFastL4
from networkapi.plugins.F5.profile import ProfileHttp
from networkapi.plugins.F5.profile import ProfileTCP
from networkapi.plugins.F5.profile import ProfileUDP
from networkapi.plugins.F5.util import logger
from networkapi.util import valid_expression


log = logging.getLogger(__name__)


class VirtualServer(F5Base):

    __properties = None

    @logger
    def delete(self, **kwargs):
        self.__remove_all_rule(kwargs['vps_names'])
        self._lb._channel.LocalLB.VirtualServer.delete_virtual_server(
            virtual_servers=kwargs['vps_names']
        )

    @logger
    def create(self, **kwargs):
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
                'timeouts': list(),
                'loose_close_state': list(),
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

        vip_dscp = {
            'pool_names': list(),
            'values': list()
        }

        rule_l7 = list()

        fastl4 = ProfileFastL4(self._lb)
        tcp = ProfileTCP(self._lb)
        http = ProfileHttp(self._lb)
        udp = ProfileUDP(self._lb)
        profiles_list = tcp.get_list() + http.get_list() + fastl4.get_list() + udp.get_list()

        for vip_request in kwargs['vips']:

            self.__prepare_properties(vip_request, profiles_list)

            # VIP
            vip_definitions.append({
                'name': vip_request['name'],
                'address': vip_request['address'],
                'port': vip_request['port'],
                'protocol': types.procotol_type(
                    vip_request['optionsvip']['l4_protocol']['nome_opcao_txt'].lower())
            })

            vip_wildmasks.append('255.255.255.255')

            vip_resources.append({
                'type': 'RESOURCE_TYPE_POOL',
                'default_pool_name': vip_request['pool']
            })

            # DSCP
            if vip_request.get('optionsvip').get('dscp'):
                vip_dscp['values'].append(vip_request['optionsvip']['dscp']['value'])
                vip_dscp['pool_names'].append(vip_request['optionsvip']['dscp']['pool_name'])

            # TRAFFIC GROUP
            if vip_request.get('optionsvip').get('traffic_group'):
                vip_traffic_groups['virtual_addresses'].append(vip_request['address'])
                vip_traffic_groups['traffic_groups'].append(
                    vip_request['optionsvip']['traffic_group'])

            # RULES
            rules = list()
            if vip_request.get('pool_l7'):
                rule_definition = vip_request['pool_l7']
                rule_name = '{}_RULE_L7'.format(vip_request['name'])

                rule_l7.append({
                    'rule_name': rule_name,
                    'rule_definition': rule_definition
                })

                rules.append({'rule_name': rule_name, 'priority': 1})

            if vip_request.get('rules'):
                for rule_name in vip_request['rules']:
                    rules.append({'rule_name': rule_name, 'priority': 1})

            if rules:
                vip_rules['rules'].append(rules)
                vip_rules['virtual_servers'].append(vip_request['name'])

        try:
            self._lb._channel.System.Session.start_transaction()

            if rule_l7:
                rl = rule.Rule(self._lb)
                rl.create(rules=rule_l7)

        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            raise e
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:
                self._lb._channel.System.Session.start_transaction()

                self.__profiles_timeout_create(
                    profiles_timeout_tcp=self.__properties['profiles_timeout_tcp'],
                    profiles_timeout_udp=self.__properties['profiles_timeout_udp'],
                    profiles_timeout_fastl4=self.__properties['profiles_timeout_fastl4'])

                vip_profiles = self.__properties['profiles']
                self.__create_vip(
                    definitions=vip_definitions,
                    wildmasks=vip_wildmasks,
                    resources=vip_resources,
                    profiles=vip_profiles)

                self.__add_rule(vip_rules)

                self.__set_snat(
                    vip_snat_pool=self.__properties['vip_snat_pool'],
                    vip_snat_auto=self.__properties['vip_snat_auto'],
                    vip_snat_none=self.__properties['vip_snat_none'])

                self.__add_persistence_profile(self.__properties['profiles_persistence'])

                self.__set_dscp(dscp=vip_dscp)

                self.__set_translate_port_state(self.__properties['translate_port_state'])

            except Exception, e:
                log.error(e)
                self._lb._channel.System.Session.rollback_transaction()

                try:
                    rule.delete(rule_name=rule_l7['rule_name'])
                except Exception, e:
                    log.error(e)
                    raise e
                raise e

            else:
                self._lb._channel.System.Session.submit_transaction()

                if vip_traffic_groups['virtual_addresses']:
                    try:
                        self._lb._channel.System.Session.start_transaction()
                        self.__set_traffic_group(vip_traffic_groups)
                    except Exception, e:
                        log.error(e)
                        self._lb._channel.System.Session.rollback_transaction()
                        raise e
                    else:
                        self._lb._channel.System.Session.submit_transaction()

    @logger
    def update(self, **kwargs):
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
                'timeouts': list(),
                'loose_close_state': list(),
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

        virtual_servers = [vip_request['name'] for vip_request in kwargs['vips']]

        resources = {
            'virtual_servers': list(),
            'pool': list()
        }

        vip_rules = {
            'virtual_servers': list(),
            'rules': list()
        }

        vip_dscp = {
            'pool_names': list(),
            'values': list()
        }

        rule_l7 = list()
        rule_l7_delete = list()

        profiles_list = list()

        for idx, vip_request in enumerate(kwargs['vips']):

            self.__prepare_properties(vip_request, profiles_list)

            # default pool
            resources['pool'].append(vip_request['pool'])
            resources['virtual_servers'].append(vip_request['name'])

            # DSCP
            vip_dscp['values'].append(vip_request['optionsvip']['dscp']['value'])
            vip_dscp['pool_names'].append(vip_request['optionsvip']['dscp']['pool_name'])

            # RULES

            rules = list()
            if vip_request.get('pool_l7'):
                rule_definition = vip_request['pool_l7']
                rule_name = '{}_RULE_L7'.format(vip_request['name'])

                rule_l7.append({
                    'rule_name': rule_name,
                    'rule_definition': rule_definition
                })

                rules.append({'rule_name': rule_name, 'priority': 1})
            else:
                rule_l7_delete.append('{}_RULE_L7'.format(vip_request['name']))

            if vip_request.get('rules'):
                for rule_name in vip_request['rules']:
                    rules.append({'rule_name': rule_name, 'priority': 1})

            if rules:
                vip_rules['rules'].append(rules)
                vip_rules['virtual_servers'].append(vip_request['name'])

        try:
            self._lb._channel.System.Session.start_transaction()

            if rule_l7:
                rl = rule.Rule(self._lb)
                rls = rl.list()
                for rl_l7 in rule_l7:
                    if '/Common/{}'.format(rl_l7['rule_name']) in rls:
                        rl.update(rules=[rl_l7])
                    else:
                        rl.create(rules=[rl_l7])

        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            raise e
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:
                self._lb._channel.System.Session.start_transaction()

                self.__remove_all_persistence_profiles(virtual_servers)

                self.__remove_all_rule(virtual_servers)

                self.__add_rule(vip_rules)

                self.__set_default_pool_name(resources)

                self.__set_snat(
                    vip_snat_pool=self.__properties['vip_snat_pool'],
                    vip_snat_auto=self.__properties['vip_snat_auto'],
                    vip_snat_none=self.__properties['vip_snat_none'])

                self.__add_persistence_profile(self.__properties['profiles_persistence'])

                self.__set_dscp(dscp=vip_dscp)

                self.__set_translate_port_state(self.__properties['translate_port_state'])

            except Exception, e:
                log.error(e)
                self._lb._channel.System.Session.rollback_transaction()
                raise e
            else:
                self._lb._channel.System.Session.submit_transaction()

                if rule_l7_delete:
                    rl = rule.Rule(self._lb)
                    for rl_l7 in rule_l7_delete:
                        try:
                            rl.delete(rule_names=[rl_l7])
                        except Exception, e:
                            log.info(e)
                            pass

    @logger
    def __create_vip(self, **kwargs):
        self._lb._channel.LocalLB.VirtualServer.create(
            definitions=kwargs['definitions'],
            wildmasks=kwargs['wildmasks'],
            resources=kwargs['resources'],
            profiles=kwargs['profiles']
        )

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
                self._lb._channel.LocalLB.VirtualServer.set_source_address_translation_snat_pool(
                    virtual_servers=kwargs.get('vip_snat_pool').get('virtual_servers'),
                    pools=kwargs.get('vip_snat_pool').get('pools')
                )
            if kwargs.get('vip_snat_none').get('virtual_servers'):
                self._lb._channel.LocalLB.VirtualServer.set_source_address_translation_none(
                    virtual_servers=kwargs.get('vip_snat_none').get('virtual_servers')
                )

    @logger
    def __add_persistence_profile(self, profiles_persistence):
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
            self._lb._channel.LocalLB.VirtualServer.set_translate_port_state(
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
            if kwargs['profiles_timeout_fastl4']['loose_close_state']:
                pfl4.set_loose_close_state(
                    profile_names=kwargs['profiles_timeout_fastl4']['profile_names'],
                    states=kwargs['profiles_timeout_fastl4']['loose_close_state'],
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
            self._lb._channel.LocalLB.VirtualServer.add_rule(
                virtual_servers=rules['virtual_servers'],
                rules=rules['rules']
            )

    @logger
    def __get_rule(self, virtual_servers):
        self._lb._channel.LocalLB.VirtualServer.get_rule(
            virtual_servers=virtual_servers
        )

    @logger
    def __remove_all_rule(self, virtual_servers):
        self._lb._channel.LocalLB.VirtualServer.remove_all_rules(
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
    def __set_protocol(self, protocols):
        self._lb._channel.LocalLB.VirtualServer.set_protocol(
            virtual_servers=protocols['virtual_servers'],
            protocols=protocols['protocols']
        )

    @logger
    def __remove_all_persistence_profiles(self, virtual_servers):

        self._lb._channel.LocalLB.VirtualServer.remove_all_persistence_profiles(
            virtual_servers=virtual_servers
        )

    @logger
    def __set_dscp(self, dscp):

        if dscp['values']:
            pl = pool.Pool(self._lb)
            pl.set_server_ip_tos(
                values=dscp['values'],
                pool_names=dscp['pool_names']
            )

    def __prepare_properties(self, vip_request, profiles_list, update=False):

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
                                            time_profile = int(vip_request['optionsvip']['timeout']['nome_opcao_txt']) * 60
                                            profile_name = pn[0] + str(time_profile)
                                            if '/Common/' + profile_name not in profiles_list:
                                                if 'tcp' in profile_name and profile_name not in self.__properties['profiles_timeout_tcp']['profile_names']:
                                                    self.__properties['profiles_timeout_tcp']['profile_names'].append(profile_name)
                                                    self.__properties['profiles_timeout_tcp']['timeouts'].append({
                                                        'value': time_profile,
                                                        'default_flag': 0
                                                    })
                                                elif 'udp' in profile_name and profile_name not in self.__properties['profiles_timeout_udp']['profile_names']:
                                                    self.__properties['profiles_timeout_udp']['profile_names'].append(profile_name)
                                                    self.__properties['profiles_timeout_udp']['timeouts'].append({
                                                        'value': time_profile,
                                                        'default_flag': 0
                                                    })
                                                elif 'fastL4' in profile_name and profile_name not in self.__properties['profiles_timeout_fastl4']['profile_names']:
                                                    self.__properties['profiles_timeout_fastl4']['profile_names'].append(profile_name)
                                                    self.__properties['profiles_timeout_fastl4']['timeouts'].append({
                                                        'value': time_profile,
                                                        'default_flag': 0
                                                    })
                                                    if 'fastL4_npath_' in profile_name:
                                                        self.__properties['profiles_timeout_fastl4']['loose_close_state'].append({
                                                            'value': 'STATE_ENABLED',
                                                            'default_flag': 0
                                                        })
                                        except:
                                            if '/Common/' + profile_name not in profiles_list:
                                                log.error(u'Profile %s nao existe')
                                                raise Exception(u'Profile %s nao existe')
                                            pass
                                    profiles.append({
                                        'profile_name': '/Common/' + profile_name,
                                        'profile_context': 'PROFILE_CONTEXT_TYPE_ALL'
                                    })

                                elif item.get('type') == 'snat':
                                    if item.get('value') == 'automap':
                                        self.__properties['vip_snat_auto']['virtual_servers'].append(vip_request['name'])
                                    elif item.get('value') == '':
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
