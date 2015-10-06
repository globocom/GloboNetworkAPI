# -*- coding:utf-8 -*-

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

from __future__ import with_statement
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from networkapi.ambiente.models import Ambiente
import logging
from networkapi.models.BaseModel import BaseModel
from networkapi.exception import InvalidValueError, OptionPoolEnvironmentDuplicatedError, OptionPoolError, OptionPoolNotFoundError, \
    OptionPoolEnvironmentNotFoundError, OptionPoolEnvironmentError
from networkapi.util import is_valid_string_maxsize, is_valid_option
from _mysql_exceptions import OperationalError


class OpcaoPool(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_opcaopool')
    description = models.CharField(blank=False, max_length=200)

    log = logging.getLogger('OpcaoPool')

    class Meta(BaseModel.Meta):
        db_table = u'opcoespool'
        managed = True


class OpcaoPoolAmbiente(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_opcaopool_ambiente_xref')
    opcao_pool = models.ForeignKey(OpcaoPool, db_column='id_opcaopool')
    ambiente = models.ForeignKey(Ambiente, db_column='id_ambiente')

    log = logging.getLogger('OpcaoPoolAmbiente')

    class Meta(BaseModel.Meta):
        db_table = u'opcoespool_ambiente_xref'
        managed = True


class OptionPool (BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_optionspool')
    type = models.CharField(
        max_length=50, blank=False, db_column='type')
    name = models.CharField(
        max_length=50, blank=False, db_column='description')

    log = logging.getLogger('OptionPool')

    class Meta(BaseModel.Meta):
        db_table = u'optionspool'
        managed = True

    def valid_option_pool(self, optionpool_map):
            '''Validate the values ​​of option pool

            @param optionpool_map: Map with the data of the request.

            @raise InvalidValueError: Represents an error occurred validating a value.
            '''

            # Get XML data
            type = optionpool_map.get('type')
            name = optionpool_map.get('name')

            # type can NOT be greater than 50
            if not is_valid_string_maxsize(type, 50, True) or not is_valid_option(type):
                self.log.error(
                    u'Parameter type is invalid. Value: %s.', type)
                raise InvalidValueError(None, 'type', type)

            # name_txt can NOT be greater than 50
            if not is_valid_string_maxsize(name, 50, True) or not is_valid_option(name):
                self.log.error(
                    u'Parameter name_txt is invalid. Value: %s.', name)
                raise InvalidValueError(None, 'name', name)

            # set variables
            self.type = type
            self.name = name

    @classmethod
    def get_by_pk(cls, id):
        """"Get  Option Pool by id.

        @return: Option Pool.

        @raise OptionPoolNotFoundError: Option Pool is not registered.
        @raise OptionPoolError: Failed to search for the Option Pool.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return OptionPool.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise OptionPoolNotFoundError(
                e, u'There is no option pool with pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option pool.')
            raise OptionPoolError(e, u'Failure to search the option pool.')

    @classmethod
    def get_all(cls):
        """Get All Option Pool.

            @return: All Option Pool.

            @raise OptionPoolError: Failed to search for all Option Pool.
        """
        try:
            return OptionPool.objects.all()
        except Exception, e:
            cls.log.error(u'Failure to list all Option Pool.')
            raise OptionPoolError(e, u'Failure to list all Option Pool.')


    @classmethod
    def get_all_by_type_and_environment (cls, optiontype, id_environment):
        """Get All Option pool by environmentvip_id and type.

            @return: Get All Option Pool by type.

            @raise OperationalError: Failed to search for all Option Pool type.
        """
        try:

            opools = OptionPool.objects.select_related().all()
            opools = opools.filter(type=optiontype)
            opools = opools.filter(
                optionpoolenvironment__environment__id=int(id_environment))

            return opools
        except Exception, e:
            cls.log.error(u'Failure to list all Option Pool in environment') #, %(optiontype, id_environment) )
            raise OptionPoolError(
                e, u'Failure to list all Option Pool in environment id' ) #, %(optiontype, id_environment)


    def delete(self):
        '''Override Django's method to remove option vip

        Before removing the option pool removes all relationships with environment vip.
        '''

        # Remove all related OptionPool environment
        for option_environment in OptionPoolEnvironment.objects.filter(option=self.id):
            option_environment.delete()

        super(OptionPool, self).delete()



class OptionPoolEnvironment(BaseModel):


    id = models.AutoField(primary_key=True, db_column='id_optionspool_environment_xref')
    option = models.ForeignKey(OptionPool, db_column='id_optionspool')
    environment = models.ForeignKey(Ambiente, db_column='id_environment')

    log = logging.getLogger('OptionPoolEnvironment')

    class Meta(BaseModel.Meta):
        db_table = u'optionspool_environment_xref'
        managed = True
        unique_together = ('option', 'environment')

    def get_by_option_environment(self, option_id, environment_id):
        """Get OptionVipEnvironmentPool by OptionPool and EnvironmentVip.

        @return: OptionPoolEnvironment.

        @raise OptionVipEnvironmentVipNotFoundError: Ipv6Equipament is not registered.
        @raise OptionVipEnvironmentVipError: Failed to search for the OptionVipEnvironmentVip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return OptionPoolEnvironment.objects.filter(option__id=option_id,
                                                          environment__id=environment_id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise OptionPoolEnvironmentNotFoundError(
                e, u'Dont there is a OptionPoolEnvironment by option_id = %s and environment_id = %s' % (
                    option_id, environment_id))
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the OptionPoolEnvironment.')
            raise OptionPoolEnvironmentError(
                e, u'Failure to search the OptionPoolEnvironment.')

    def validate(self):
        """Validates whether OptionPool is already associated with EnvironmentVip

            @raise IpEquipamentoDuplicatedError: if OptionPool is already associated with EnvironmentVip
        """
        try:
            OptionPoolEnvironment.objects.get(
                option=self.option, environment=self.environment)
            raise OptionPoolEnvironmentDuplicatedError(
                None, u'Option pool already registered for the environment vip.')
        except ObjectDoesNotExist:
            pass

