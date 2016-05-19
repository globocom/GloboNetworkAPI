import itertools
import logging

import bigsuds

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import monitor, node, pool, poolmember, util, virtualserver
from networkapi.plugins.F5.util import logger

from ..base import BasePlugin

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    #######################################
    # VIP
    #######################################
    @logger
    @util.connection
    def delete_vip(self, vips):
        tratado = util.trata_param_vip(vips)
        try:
            vts = virtualserver.VirtualServer(self._lb)
            vps_names = [vp['name'] for vp in tratado['vips_filter']]
            vts.delete(vps_names=vps_names)
        except Exception, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)
        else:
            self.__delete_pool({'pools': tratado['pool_filter_created']})

    @logger
    @util.connection
    def create_vip(self, vips):
        tratado = util.trata_param_vip(vips)

        if tratado['pool_filter']:
            self.__create_pool({'pools': tratado['pool_filter']})
        try:
            vts = virtualserver.VirtualServer(self._lb)
            vts.create(vips=tratado['vips_filter'])
        except Exception, e:
            if tratado['pool_filter']:
                self.__delete_pool({'pools': tratado['pool_filter']})
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

    @logger
    @util.connection
    def update_vip(self, vips):
        tratado = util.trata_param_vip(vips)

        if tratado['pool_filter']:
            self.__create_pool({'pools': tratado['pool_filter']})
        try:
            vts = virtualserver.VirtualServer(self._lb)
            vts.update(vips=tratado['vips_filter'])
        except Exception, e:
            if tratado['pool_filter']:
                self.__delete_pool({'pools': tratado['pool_filter']})
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

    #######################################
    # POOLMEMBER
    #######################################
    @logger
    @util.transation
    def set_state_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)

        plm.set_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            monitor_state=pls['pools_members']['monitor'],
            session_state=pls['pools_members']['session'])

    @logger
    @util.transation
    def set_connection_limit_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setConnectionLimit(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            connection_limit=pls['pools_members']['limit'])

    @logger
    @util.transation
    def set_priority_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setPriority(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            priority=pls['pools_members']['priority'])

    @logger
    @util.transation
    def get_state_member(self, pools):
        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.get_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    @logger
    @util.transation
    def create_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.create(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    @logger
    @util.transation
    def remove_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.remove(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    #######################################
    # POOL
    #######################################
    @logger
    @util.connection
    def create_pool(self, pools):
        self.__create_pool(pools)

    @logger
    def __create_pool(self, pools):

        monitor_associations = []
        pls = util.trata_param_pool(pools)

        mon = monitor.Monitor(self._lb)

        monitor_associations, monitor_associations_nodes, templates_extra = mon.prepare_template(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            healthcheck=pls['pools_healthcheck']
        )

        mon.create_template(templates_extra=templates_extra)

        try:
            self._lb._channel.System.Session.start_transaction()

            pl = pool.Pool(self._lb)

            pl.create(
                names=pls['pools_names'],
                lbmethod=pls['pools_lbmethod'],
                members=pls['pools_members']['members'])

            pl.set_monitor_association(monitor_associations=monitor_associations)

            pl.set_service_down_action(
                names=pls['pools_names'],
                actions=pls['pools_actions'])

            plm = poolmember.PoolMember(self._lb)

            plm.set_connection_limit(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                connection_limit=pls['pools_members']['limit'])

            plm.set_priority(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                priority=pls['pools_members']['priority'])

            plm.set_states(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                monitor_state=pls['pools_members']['monitor'],
                session_state=pls['pools_members']['session'])

        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
            if template_names != []:
                mon.delete_template(
                    template_names=template_names
                )
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:
                if monitor_associations_nodes.get('nodes'):
                    nd = node.Node(self._lb)
                    nd.set_monitor_rule(monitor_associations=monitor_associations_nodes)
            except bigsuds.OperationFailed:
                pass

    @logger
    @util.connection
    def update_pool(self, pools):
        self.__update_pool(pools)

    @logger
    def __update_pool(self, pools):
        monitor_associations = []
        pls = util.trata_param_pool(pools)

        pl = pool.Pool(self._lb)
        mon = monitor.Monitor(self._lb)

        # get template currents
        monitor_associations_old = pl.get_monitor_association(names=pls['pools_names'])

        # creates templates
        monitor_associations, monitor_associations_nodes, templates_extra = mon.prepare_template(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            healthcheck=pls['pools_healthcheck']
        )

        strings_old = {
            'template_names': list(),
            'property_types': list()
        }

        strings_new = list()
        monitors_new = list()
        monitors_old = list()

        for monitor_old in monitor_associations_old:
            for monitor_new in monitor_associations:
                if monitor_old['pool_name'] == monitor_new['pool_name']:
                    if monitor_old != monitor_new:
                        template_name = monitor_old['monitor_rule']['monitor_templates'][0]
                        property_type_s = 'STYPE_SEND'
                        property_type_r = 'STYPE_RECEIVE'

                        strings_old['template_names'].append(template_name)
                        strings_old['property_types'].append(property_type_s)
                        strings_old['template_names'].append(template_name)
                        strings_old['property_types'].append(property_type_r)

                        template_name = monitor_new['monitor_rule']['monitor_templates'][0]
                        strings_new += [templates_extra['values'][k] for k, v in enumerate(templates_extra['template_names']) if v == template_name] or [{}, {}]

                        monitors_new.append(monitor_new)
                        monitors_new.append(monitor_new)
                        monitors_old.append(monitor_old)
                        monitors_old.append(monitor_old)
                    break

        get_strings_old = mon.get_template_string_property(
            template_names=strings_old.get('template_names'),
            property_types=strings_old.get('property_types')
        )
        monitors_assoc = list()
        monitors_assoc_old = list()
        template_name_found = list()

        for key, string in enumerate(get_strings_old):
            try:
                if strings_new[key] != string:
                    monitors_assoc.append(monitors_new[key])
                    monitors_assoc_old.append(monitors_old[key])
                    template_name_found.append(monitors_new[key]['monitor_rule']['monitor_templates'][0])
            except:
                pass

        values_new = list()
        template_names_new = list()
        template_attributes_new = list()
        templates_new = list()
        template_name_found = list(set(template_name_found))
        for template_name in template_name_found:
            values_new += [templates_extra['values'][k] for k, v in enumerate(templates_extra['template_names']) if v == template_name]
            template_names_new += [templates_extra['template_names'][k] for k, v in enumerate(templates_extra['template_names']) if v == template_name]
            template_attributes_new += [templates_extra['template_attributes'][k] for k, v in enumerate(templates_extra['templates']) if v['template_name'] == template_name]
            templates_new += [templates_extra['templates'][k] for k, v in enumerate(templates_extra['templates']) if v['template_name'] == template_name]

        monitors_assoc = {v['pool_name']: v for v in monitors_assoc}.values()
        monitors_assoc_old = {v['pool_name']: v for v in monitors_assoc_old}.values()
        templates_extra = {
            'values': values_new,
            'template_names': template_names_new,
            'template_attributes': template_attributes_new,
            'templates': templates_new
        }
        mon.create_template(templates_extra=templates_extra)

        try:
            self._lb._channel.System.Session.start_transaction()

            pl.set_monitor_association(monitor_associations=monitors_assoc)

            pl.set_lb_method(
                names=pls['pools_names'],
                lbmethod=pls['pools_lbmethod'])

            pl.set_service_down_action(
                names=pls['pools_names'],
                actions=pls['pools_actions'])

            plm = poolmember.PoolMember(self._lb)

            if pls['pools_members']['members_remove']:
                plm.remove(
                    names=pls['pools_names'],
                    members=pls['pools_members']['members_remove'])

            if pls['pools_members']['members_new']:
                plm.create(
                    names=pls['pools_names'],
                    members=pls['pools_members']['members_new'])

            plm.set_connection_limit(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                connection_limit=pls['pools_members']['limit'])

            plm.set_priority(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                priority=pls['pools_members']['priority'])

            plm.set_states(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                monitor_state=pls['pools_members']['monitor'],
                session_state=pls['pools_members']['session'])

        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()

            # delete templates created
            template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitors_assoc])) if 'MONITOR' in m]
            if template_names:
                mon.delete_template(
                    template_names=template_names
                )
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:

                if monitor_associations_nodes.get('nodes'):
                    nd = node.Node(self._lb)
                    nd.set_monitor_rule(monitor_associations=monitor_associations_nodes)

                if pls['pools_confirm']['pools_names']:
                    plm.set_member_monitor_state(
                        names=pls['pools_confirm']['pools_names'],
                        members=pls['pools_confirm']['members'],
                        monitor_state=pls['pools_confirm']['monitor'])
            except bigsuds.OperationFailed:
                pass

            # delete templates old
            try:
                template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitors_assoc_old])) if 'MONITOR' in m]
                if template_names:
                    mon.delete_template(template_names=template_names)
            except bigsuds.OperationFailed:
                pass

    @logger
    @util.connection
    def delete_pool(self, pools):
        self.__delete_pool(pools)

    @logger
    def __delete_pool(self, pools):

        pls = util.trata_param_pool(pools)

        pl = pool.Pool(self._lb)
        mon = monitor.Monitor(self._lb)

        try:
            self._lb._channel.System.Session.start_transaction()
            monitor_associations = pl.get_monitor_association(names=pls['pools_names'])
            pl.remove_monitor_association(names=pls['pools_names'])
        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:
                self._lb._channel.System.Session.start_transaction()
                pl.delete(names=pls['pools_names'])
            except Exception, e:
                log.error(e)
                self._lb._channel.System.Session.rollback_transaction()
                pl.set_monitor_association(monitor_associations=monitor_associations)
                raise base_exceptions.CommandErrorException(e)
            else:
                self._lb._channel.System.Session.submit_transaction()

                try:
                    template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
                    if template_names:
                        mon.delete_template(template_names=template_names)
                except bigsuds.OperationFailed:
                    pass
