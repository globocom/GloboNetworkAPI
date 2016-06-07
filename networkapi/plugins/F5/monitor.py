# -*- coding: utf-8 -*-
import logging
import time

from django.core.cache import cache

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import types
from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.util import logger

log = logging.getLogger(__name__)


class Monitor(F5Base):

    @logger
    def prepare_template(self, **kwargs):

        templates = []
        template_attributes = []
        template_names = []
        values = []
        monitor_associations = []
        monitor_associations_nodes = {
            'nodes': list(),
            'monitor_rules': list()
        }

        try:

            for i, pool in enumerate(kwargs['names']):

                monitor_association = {
                    'pool_name': None,
                    'monitor_rule': {
                        'monitor_templates': [],
                        'type': None,
                        'quorum': None
                    }
                }

                if kwargs['healthcheck'][i]['healthcheck_request'] != '' or kwargs['healthcheck'][i]['healthcheck_expect'] != '':

                    key = 'pool:monitor:%s' % kwargs['names'][i]
                    name = cache.get(key)
                    if not name:
                        name = self.generate_name(kwargs['names'][i])
                        cache.set(key, name)

                    template = {
                        'template_name': name,
                        'template_type': types.template_type(kwargs['healthcheck'][i]['healthcheck_type'])
                    }

                    templates.append(template)
                    template_attributes.append({
                        'parent_template': kwargs['healthcheck'][i]['healthcheck_type'].lower(),
                        'interval': 5,
                        'timeout': 16,
                        'dest_ipport': types.address_type(kwargs['healthcheck'][i]['destination']),
                        'is_read_only': 0,
                        'is_directly_usable': 1
                    })

                    healthcheck_request = kwargs['healthcheck'][i]['healthcheck_request']
                    healthcheck_expect = kwargs['healthcheck'][i]['healthcheck_expect']
                    healthcheck_request += '\r\n\r\n' if '\r\n\r\n' not in healthcheck_request else ''

                    template_names.append(name)
                    values.append({
                        'type': 'STYPE_SEND',
                        'value': healthcheck_request.encode('unicode-escape')
                    })

                    template_names.append(name)
                    values.append({
                        'type': 'STYPE_RECEIVE',
                        'value': healthcheck_expect.encode('unicode-escape')
                    })

                else:
                    name = kwargs['healthcheck'][i]['healthcheck_type'].lower()

                monitor_association['pool_name'] = kwargs['names'][i]
                monitor_association['monitor_rule']['monitor_templates'].append(name)
                monitor_association['monitor_rule']['type'] = 'MONITOR_RULE_TYPE_SINGLE'
                monitor_association['monitor_rule']['quorum'] = 0
                monitor_associations.append(monitor_association)

                if name == 'udp':
                    for node in kwargs['members'][i]:
                        monitor_association_node = {
                            'monitor_templates': [],
                            'type': None,
                            'quorum': None
                        }
                        monitor_association_node['monitor_templates'].append('icmp')
                        monitor_association_node['type'] = 'MONITOR_RULE_TYPE_SINGLE'
                        monitor_association_node['quorum'] = 0
                        monitor_associations_nodes['monitor_rules'].append(monitor_association_node)
                        monitor_associations_nodes['nodes'].append(node['address'])

        except Exception, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

        templates_extra = {
            'templates': templates,
            'template_attributes': template_attributes,
            'template_names': template_names,
            'values': values
        }

        return monitor_associations, monitor_associations_nodes, templates_extra

    @logger
    def create_template(self, **kwargs):

        templates = kwargs['templates_extra']['templates']
        template_attributes = kwargs['templates_extra']['template_attributes']
        template_names = kwargs['templates_extra']['template_names']
        values = kwargs['templates_extra']['values']

        if len(templates) > 0:
            try:
                self._lb._channel.System.Session.start_transaction()

                self._lb._channel.LocalLB.Monitor.create_template(
                    templates=templates,
                    template_attributes=template_attributes
                )
            except Exception, e:
                self._lb._channel.System.Session.rollback_transaction()
                raise base_exceptions.CommandErrorException(e)
            else:
                self._lb._channel.System.Session.submit_transaction()

                try:
                    self._lb._channel.System.Session.start_transaction()

                    self._lb._channel.LocalLB.Monitor.set_template_string_property(
                        template_names=template_names,
                        values=values
                    )

                except Exception, e:
                    self._lb._channel.System.Session.rollback_transaction()
                    raise base_exceptions.CommandErrorException(e)

                else:
                    self._lb._channel.System.Session.submit_transaction()

    # def delete_templateAssoc(self, **kwargs):
    #     log.info('monitor:delete_templateAssoc:%s' % kwargs)
    #     for k, v in kwargs.items():
    #         if v == []:
    #             return

    #     self._lb._channel.System.Session.start_transaction()
    #     try:
    #         pl = pool.Pool(self._lb)
    #         monitor_associations = pl.get_monitor_association(names=kwargs['names'])

    #         pl.remove_monitor_association(names=kwargs['names'])

    #     except Exception, e:
    #         self._lb._channel.System.Session.rollback_transaction()
    #         raise base_exceptions.CommandErrorException(e)
    #     else:
    #         self._lb._channel.System.Session.submit_transaction()

    #         try:
    #             template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
    #             if template_names:
    #                 self.delete_template(template_names=template_names)
    #         except bigsuds.OperationFailed:
    #             pass

    @logger
    def get_template_string_property(self, **kwargs):
        strings = self._lb._channel.LocalLB.Monitor.get_template_string_property(
            template_names=kwargs['template_names'],
            property_types=kwargs['property_types']
        )
        return strings

    @logger
    def delete_template(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return
        self._lb._channel.System.Session.start_transaction()
        try:
            self._lb._channel.LocalLB.Monitor.delete_template(template_names=kwargs['template_names'])
        except Exception:
            self._lb._channel.System.Session.rollback_transaction()
        else:
            self._lb._channel.System.Session.submit_transaction()

    @logger
    def generate_name(self, identifier, number=0):
        return '/Common/MONITOR_POOL_%s_%s_%s' % (identifier, str(number), str(time.time()))
