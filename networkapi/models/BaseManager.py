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


from django.db import models
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist


class BaseQuerySet(QuerySet):

    """Base class for operations to database"""

    def group_by(self, column):
        """ Returns query, rewrited to use SELECT ... GROUP BY [column].
            Note that you MUST use the database column name, not the ORM model field.
        """
        sql, params = self.query.get_compiler(self.db).as_sql()
        query = self.model._default_manager.raw(
            sql.rstrip() + ' GROUP BY ' + column, params)
        try:
            return query
        except IndexError, e:
            raise ObjectDoesNotExist

    def for_update(self):
        """ Returns query, rewrited to use SELECT ... FOR UPDATE.
            Can be used in transaction to get lock on selected rows.
            Database must support this SQL statements.

            Example:
            >>> query = MyModel.objects.filter(name = 'mateus').for_update()
            >>> unicode(query.query)
            "SELECT * FROM myapp_mymodel WHERE name = 'mateus' FOR UPDATE"
        """
        sql, params = self.query.get_compiler(self.db).as_sql()
        query = self.model._default_manager.raw(
            sql.rstrip() + ' FOR UPDATE', params)

        try:
            return query[0]
        except IndexError, e:
            raise ObjectDoesNotExist

    def uniqueResult(self):
        sql, params = self.query.get_compiler(self.db).as_sql()
        query = self.model._default_manager.raw(sql.rstrip(), params)

        try:
            return query[0]
        except IndexError, e:
            raise ObjectDoesNotExist


class BaseManager(models.Manager):

    """Base class for managing the operations to database"""

    def get_query_set(self):
        return BaseQuerySet(self.model, using=self._db)
