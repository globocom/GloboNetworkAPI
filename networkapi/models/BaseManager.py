# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

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
            sql.rstrip() +
            ' GROUP BY ' +
            column,
            params)
        try:
            return query
        except IndexError as e:
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
            sql.rstrip() +
            ' FOR UPDATE',
            params)

        try:
            return query[0]
        except IndexError as e:
            raise ObjectDoesNotExist

    def uniqueResult(self):
        sql, params = self.query.get_compiler(self.db).as_sql()
        query = self.model._default_manager.raw(sql.rstrip(), params)

        try:
            return query[0]
        except IndexError as e:
            raise ObjectDoesNotExist


class BaseManager(models.Manager):

    """Base class for managing the operations to database"""

    def get_query_set(self):
        return BaseQuerySet(self.model, using=self._db)
