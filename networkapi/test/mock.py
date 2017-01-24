# -*- coding: utf-8 -*-
import logging

log = logging.getLogger(__name__)


class MockPlugin(object):

    _status = True

    @classmethod
    def status(cls, status=True):
        cls._status = status

    @classmethod
    def update_pool(cls, pools):
        if cls.status:
            log.info('Mock Update Pool')
        else:
            raise Exception('Error')

    @classmethod
    def delete_pool(cls, pools):
        if cls.status:
            log.info('Mock Delete Pool')
        else:
            raise Exception('Error')

    @classmethod
    def create_pool(cls, pools):
        if cls.status:
            log.info('Mock Create Pool')
        else:
            raise Exception('Error')
