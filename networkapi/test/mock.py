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


class MockPluginNetwork(object):

    _status = True

    @classmethod
    def status(cls, status=True):
        cls._status = status

    @classmethod
    def remove_svi(cls, svi_number):
        if cls._status:
            log.info('Mock Remove Network')
        else:
            raise Exception('Error')

    @classmethod
    def create_svi(cls, svi_number, svi_description='no description'):
        if cls._status:
            log.info('Mock Create Network')
        else:
            raise Exception('Error')

    @classmethod
    def connect(cls):
        if cls._status:
            log.info('Mock Connecting')
        else:
            raise Exception('Error')

    @classmethod
    def close(cls):
        if cls._status:
            log.info('Mock Closing')
        else:
            raise Exception('Error')

    @classmethod
    def ensure_privilege_level(cls):
        if cls._status:
            log.info('Mock Ensuring Privilege Level')
        else:
            raise Exception('Error')

    @classmethod
    def copyScriptFileToConfig(cls, filename, use_vrf=None, destination='running-config'):

        if cls._status:
            log.info('Mock Copying script file to config')
        else:
            raise Exception('Error')


class MockPluginVip(object):

    _status = True

    @classmethod
    def status(cls, status=True):
        cls._status = status

    @classmethod
    def create_vip(cls, vips):
        if cls._status:
            log.info('Mock Create Vip')
        else:
            raise Exception('Error')

    @classmethod
    def update_vip(cls, vips):
        if cls._status:
            log.info('Mock Update Vip')
        else:
            raise Exception('Error')

    @classmethod
    def delete_vip(cls, vips):
        if cls._status:
            log.info('Mock Delete Vip')
        else:
            raise Exception('Error')
