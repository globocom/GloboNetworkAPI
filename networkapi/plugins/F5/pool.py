import logging

from networkapi.plugins.F5.f5base import F5Base


log = logging.getLogger(__name__)


class Pool(F5Base):

    def create(self, **kwargs):
        log.info('pool:create:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.create_v2(
            kwargs['names'],
            kwargs['lbmethod'],
            kwargs['members'])

    def delete(self, **kwargs):
        log.info('pool:delete:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.delete_pool(
            kwargs['names'])

    def set_service_down_action(self, **kwargs):
        log.info('pool:set_service_down_action:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_action_on_service_down(
            kwargs['names'],
            kwargs['actions']
        )

    def set_lb_method(self, **kwargs):
        log.info('pool:set_lb_method:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_lb_method(
            kwargs['names'],
            kwargs['lbmethod'])

    def set_monitor_association(self, **kwargs):
        log.info('pool:set_monitor_association:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_monitor_association(
            monitor_associations=kwargs['monitor_associations'])

    def remove_monitor_association(self, **kwargs):
        log.info('pool:remove_monitor_association:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.remove_monitor_association(pool_names=kwargs['names'])

    def get_monitor_association(self, **kwargs):
        log.info('pool:get_monitor_association:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        monitor_associations = self._lb._channel.LocalLB.Pool.get_monitor_association(
            pool_names=kwargs['names'])

        return monitor_associations

    def set_server_ip_tos(self, **kwargs):
        self._lb._channel.LocalLB.Pool.set_server_ip_tos(
            pool_names=kwargs['pool_names'],
            values=kwargs['values'])

    def get_list(self):
        list_pool = self._lb._channel.LocalLB.Pool.get_list()
        return list_pool
