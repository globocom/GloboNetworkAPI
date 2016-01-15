import itertools
import logging
import time

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import lb, types, pool, util
from bigsuds import OperationFailed

log = logging.getLogger(__name__)


class Monitor(object):

    def __init__(self, _lb=None):
        if _lb is not None and not isinstance(_lb, lb.Lb):
            raise base_exceptions.PluginUninstanced('lb must be of type F5.Lb')

        self._lb = _lb

    def createTemplate(self, **kwargs):
        log.info('monitor:createTemplate:%s' % kwargs)

        templates = []
        template_attributes = []
        template_names = []
        values = []
        monitor_associations = []

        try:
            templates_exists = self._lb._channel.LocalLB.Monitor.get_template_list()

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

                    name = self.generateName(kwargs['names'][i])
                    template = {
                        'template_name': name,
                        'template_type': types.TemplateType(kwargs['healthcheck'][i]['healthcheck_type'])
                    }
                    if util.search_dict(templates_exists, template):
                        template['template_name'] += str(time.time())
                        name = template['template_name']

                    templates.append(template)
                    template_attributes.append({
                        'parent_template': kwargs['healthcheck'][i]['healthcheck_type'].lower(),
                        'interval': 5,
                        'timeout': 16,
                        'dest_ipport': types.AddressType(kwargs['healthcheck'][i]['destination']),
                        'is_read_only': 0,
                        'is_directly_usable': 1
                    })

                    healthcheck_request = kwargs['healthcheck'][i]['healthcheck_request']
                    healthcheck_expect = kwargs['healthcheck'][i]['healthcheck_expect']

                    template_names.append(name)
                    values.append({
                        'type': 'STYPE_SEND',
                        'value': healthcheck_request
                    })

                    template_names.append(name)
                    values.append({
                        'type': 'STYPE_RECEIVE',
                        'value': healthcheck_expect
                    })
                else:
                    name = kwargs['healthcheck'][i]['healthcheck_type'].lower()

                monitor_association['pool_name'] = kwargs['names'][i]
                monitor_association['monitor_rule']['monitor_templates'].append(name)
                monitor_association['monitor_rule']['type'] = 'MONITOR_RULE_TYPE_SINGLE'
                monitor_association['monitor_rule']['quorum'] = 0
                monitor_associations.append(monitor_association)

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
        except Exception, e:
            log.error(e)
        return monitor_associations

    def deleteTemplateAssoc(self, **kwargs):
        log.info('monitor:deleteTemplateAssoc:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        try:
            pl = pool.Pool(self._lb)
            monitor_associations = pl.getMonitorAssociation(names=kwargs['names'])

            self._lb._channel.System.Session.start_transaction()
            pl.removeMonitorAssociation(names=kwargs['names'])

        except Exception, e:
            self._lb._channel.System.Session.rollback_transaction()
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            d = pl.get_list()
            monitor_associations_all = pl.getMonitorAssociation(names=d)
            monitor_associations_all = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations_all])) if 'MONITOR' in m]
            monitor_associations = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]

            template_names = list()
            for m in monitor_associations:
                if not util.search_dict(monitor_associations_all, m):
                    template_names.append(m)

            if template_names:
                self.deleteTemplate(template_names=template_names)

    def deleteTemplate(self, **kwargs):
        log.info('monitor:deleteTemplate:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return
        try:
            self._lb._channel.System.Session.start_transaction()
            self._lb._channel.LocalLB.Monitor.delete_template(template_names=kwargs['template_names'])
        except Exception:
            self._lb._channel.System.Session.rollback_transaction()
        else:
            self._lb._channel.System.Session.submit_transaction()

    def generateName(self, identifier, number=0):
        return '/Common/MONITOR_POOL_%s_%s' % (identifier, str(number))
