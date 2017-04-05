# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import logging
import types

from kombu import Connection
from kombu import Exchange
from kombu import Producer
from kombu import Queue

from networkapi.settings import BROKER_CONNECT_TIMEOUT
from networkapi.settings import BROKER_DESTINATION
from networkapi.settings import BROKER_HOST
from networkapi.settings import BROKER_PASSWORD
from networkapi.settings import BROKER_USER
from networkapi.settings import BROKER_VHOST


class QueueManager(object):

    """Object to manager objects sent to queue."""

    log = logging.getLogger(__name__)

    def __init__(self, broker_vhost=None, broker_host=None, broker_user=None,
                 broker_password=None, queue_name=None, exchange_name=None,
                 queue_type='direct', routing_key=None):
        """
            Create a new instance QueueManager and initialize
            with parameters of destination and broker uri
            from settings or set default settings.

        """

        self._msgs = []
        self._broker_timeout = BROKER_CONNECT_TIMEOUT

        self._broker_host = broker_host if \
            broker_host is not None else BROKER_HOST
        self._broker_user = broker_user if \
            broker_user is not None else BROKER_USER
        self._broker_password = broker_password if \
            broker_password is not None else BROKER_PASSWORD
        self._broker_vhost = broker_vhost if \
            broker_vhost is not None else BROKER_VHOST
        self._queue_name = queue_name if queue_name is not None else \
            BROKER_DESTINATION
        self._exchange_name = exchange_name if exchange_name is not None \
            else BROKER_DESTINATION
        self._routing_key = routing_key if routing_key is not None else \
            BROKER_DESTINATION
        self._queue_type = queue_type

        self.log.debug('broker_host:%s', self._broker_host)
        self.log.debug('broker_user:%s', self._broker_user)
        self.log.debug('broker_password:%s', self._broker_password)
        self.log.debug('broker_vhost:%s', self._broker_vhost)
        self.log.debug('queue_name:%s', self._queue_name)
        self.log.debug('exchange_name:%s', self._exchange_name)
        self.log.debug('routing_key:%s', self._routing_key)
        self.log.debug('queue_type:%s', self._queue_type)

    def append(self, dict_obj):
        """
            Appended in list object a dictionary that represents
            the body of the message that will be sent to queue.

            :param dict_obj: Dict object

        """

        try:

            if not isinstance(dict_obj, types.DictType):
                raise ValueError(
                    u'QueueManagerError - The type must be a instance of Dict')

            self._msgs.append(dict_obj)
            self.log.debug('dict_obj:%s', dict_obj)

        except Exception, e:
            self.log.error(
                u'QueueManagerError - Error on appending objects to queue.')
            self.log.error(e)
            raise Exception(
                'QueueManagerError - Error on appending objects to queue.')

    def send(self):

        try:
            # Connection
            conn = Connection(
                host=self._broker_host,
                userid=self._broker_user,
                password=self._broker_password,
                virtual_host=self._broker_vhost)

            # Channel
            channel = conn.channel()

            # Exchange
            task_exchange = Exchange(self._exchange_name,
                                     type=self._queue_type)
            # Queues
            queue = Queue(name=self._queue_name, channel=channel,
                          exchange=task_exchange,
                          routing_key=self._routing_key)
            queue.declare()

            # Producer
            producer = Producer(exchange=task_exchange, channel=channel,
                                routing_key=self._routing_key)

            # Send message
            for message in self._msgs:
                serialized_message = json.dumps(message, ensure_ascii=False)
                producer.publish(serialized_message)

            conn.close()

        except Exception, e:

            self.log.error(
                u'QueueManagerError - Error on sending objects from queue.')
            self.log.debug(e)
            raise Exception(
                'QueueManagerError - Error on sending objects to queue.')
