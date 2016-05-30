# -*- coding: utf-8 -*-
import logging
import suds

from django.core.cache import cache

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.Brocade import types
from networkapi.plugins.Brocade.base import Base

log = logging.getLogger(__name__)


class Monitor(Base):


    def teste_create_template(self, **kwargs):
        log.info('monitor:create_template:%s' % kwargs)

        #teste de criacao de monitor tcp
        portPolicy = self._lb.slb_factory.create('PortPolicy')
        portPolicy.name = 'TESTE_TCP'
        portPolicy.l4Check = True
        portPolicy.protocol = ("HTTP")


        httpPortPolicy = (self._lb.slb_factory
                          .create('HttpPortPolicy'))
        urlHealthCheck = (self._lb.slb_factory
                          .create('URLHealthCheck'))
        urlHealthCheck.url = 'GET /'
        httpPortPolicy.urlStatusCodeInfo = urlHealthCheck
        httpPortPolicy.healthCheckType = 'SIMPLE'

        portPolicy.httpPolInfo = httpPortPolicy

        try:
            self._lb.slb_service.createPortPolicy(portPolicy)
        except suds.WebFault as e:
            log.error(_('Error in create/update port policy %s'), e)


    # def create_template(self, **kwargs):
    #     log.info('monitor:create_template:%s' % kwargs)
    #
    #     templates = []
    #     template_attributes = []
    #     template_names = []
    #     values = []
    #     monitor_associations = []
    #
    #     try:
    #
    #         for i, pool in enumerate(kwargs['names']):
    #
    #             monitor_association = {
    #                 'pool_name': None,
    #                 'monitor_rule': {
    #                     'monitor_templates': [],
    #                     'type': None,
    #                     'quorum': None
    #                 }
    #             }
    #
    #             if kwargs['healthcheck'][i]['healthcheck_request'] != '' or kwargs['healthcheck'][i]['healthcheck_expect'] != '':
    #
    #                 key = 'pool:monitor:%s' % kwargs['names'][i]
    #                 name = cache.get(key)
    #                 if not name:
    #                     name = self.generate_name(kwargs['names'][i])
    #                     cache.set(key, name)
    #
    #                 template = {
    #                     'template_name': name,
    #                     'template_type': types.template_type(kwargs['healthcheck'][i]['healthcheck_type'])
    #                 }
    #
    #                 templates.append(template)
    #                 template_attributes.append({
    #                     'parent_template': kwargs['healthcheck'][i]['healthcheck_type'].lower(),
    #                     'interval': 5,
    #                     'timeout': 16,
    #                     'dest_ipport': types.address_type(kwargs['healthcheck'][i]['destination']),
    #                     'is_read_only': 0,
    #                     'is_directly_usable': 1
    #                 })
    #
    #                 healthcheck_request = kwargs['healthcheck'][i]['healthcheck_request']
    #                 healthcheck_expect = kwargs['healthcheck'][i]['healthcheck_expect']
    #
    #                 template_names.append(name)
    #                 values.append({
    #                     'type': 'STYPE_SEND',
    #                     'value': healthcheck_request
    #                 })
    #
    #                 template_names.append(name)
    #                 values.append({
    #                     'type': 'STYPE_RECEIVE',
    #                     'value': healthcheck_expect
    #                 })
    #             else:
    #                 name = kwargs['healthcheck'][i]['healthcheck_type'].lower()
    #
    #             monitor_association['pool_name'] = kwargs['names'][i]
    #             monitor_association['monitor_rule']['monitor_templates'].append(name)
    #             monitor_association['monitor_rule']['type'] = 'MONITOR_RULE_TYPE_SINGLE'
    #             monitor_association['monitor_rule']['quorum'] = 0
    #             monitor_associations.append(monitor_association)
    #
    #         if len(templates) > 0:
    #             try:
    #                 self._lb._channel.System.Session.start_transaction()
    #
    #                 self._lb._channel.LocalLB.Monitor.create_template(
    #                     templates=templates,
    #                     template_attributes=template_attributes
    #                 )
    #             except Exception, e:
    #                 self._lb._channel.System.Session.rollback_transaction()
    #                 raise base_exceptions.CommandErrorException(e)
    #             else:
    #                 self._lb._channel.System.Session.submit_transaction()
    #
    #                 try:
    #                     self._lb._channel.System.Session.start_transaction()
    #
    #                     self._lb._channel.LocalLB.Monitor.set_template_string_property(
    #                         template_names=template_names,
    #                         values=values
    #                     )
    #                 except Exception, e:
    #                     self._lb._channel.System.Session.rollback_transaction()
    #                     raise base_exceptions.CommandErrorException(e)
    #
    #                 else:
    #                     self._lb._channel.System.Session.submit_transaction()
    #     except Exception, e:
    #         log.error(e)
    #     return monitor_associations
    #
    # # def delete_templateAssoc(self, **kwargs):
    # #     log.info('monitor:delete_templateAssoc:%s' % kwargs)
    # #     for k, v in kwargs.items():
    # #         if v == []:
    # #             return
    #
    # #     self._lb._channel.System.Session.start_transaction()
    # #     try:
    # #         pl = pool.Pool(self._lb)
    # #         monitor_associations = pl.get_monitor_association(names=kwargs['names'])
    #
    # #         pl.remove_monitor_association(names=kwargs['names'])
    #
    # #     except Exception, e:
    # #         self._lb._channel.System.Session.rollback_transaction()
    # #         raise base_exceptions.CommandErrorException(e)
    # #     else:
    # #         self._lb._channel.System.Session.submit_transaction()
    #
    # #         try:
    # #             template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
    # #             if template_names:
    # #                 self.delete_template(template_names=template_names)
    # #         except bigsuds.OperationFailed:
    # #             pass
    #
    # def delete_template(self, **kwargs):
    #     log.info('monitor:delete_template:%s' % kwargs)
    #     for k, v in kwargs.items():
    #         if v == []:
    #             return
    #     self._lb._channel.System.Session.start_transaction()
    #     try:
    #         self._lb._channel.LocalLB.Monitor.delete_template(template_names=kwargs['template_names'])
    #     except Exception:
    #         self._lb._channel.System.Session.rollback_transaction()
    #     else:
    #         self._lb._channel.System.Session.submit_transaction()
    #
    # def generate_name(self, identifier, number=0):
    #     return '/Common/MONITOR_POOL_%s_%s_%s' % (identifier, str(number), str(time.time()))
