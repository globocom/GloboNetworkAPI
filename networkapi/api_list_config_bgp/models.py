# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from networkapi.util.geral import get_model

from networkapi.api_list_config_bgp.v4 import exceptions
from networkapi.models.BaseModel import BaseModel

class ListConfigBGPType:
    p = ('P', 'P')
    a = ('A', 'A')
    c = ('C', 'C')
    list_type = (p, a, c)

class ListConfigBGP(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    name = models.CharField(
        blank=False,
        max_length=100,
        db_column='name'
    )

    type = models.CharField(
        db_column='type',
        max_length=2,
        blank=False,
        choices=ListConfigBGPType.list_type
    )

    config = models.TextField(
        blank=False,
        db_column='config'
    )

    log = logging.getLogger('ListConfigBGP')

    class Meta(BaseModel.Meta):
        db_table = u'list_config_bgp'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get ListConfigBGP by id.

        :return: ListConfigBGP.

        :raise ListConfigBGPNotFoundError: ListConfigBGP not registered.
        :raise ListConfigBGPError: Failed to search for the ListConfigBGP.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return ListConfigBGP.objects.get(id=id)
        except ObjectDoesNotExist:
            cls.log.error(u'ListConfigBGP not found. pk {}'.format(id))
            raise exceptions.ListConfigBGPNotFoundError(id)
        except OperationalError:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError()
        except Exception:
            cls.log.error(u'Failure to search the ListConfigBGP.')
            raise exceptions.ListConfigBGPError(
                u'Failure to search the ListConfigBGP.')

    def create_v4(self):
        """Create ListConfigBGP."""
        pass

    def update_v4(self):
        """Update ListConfigBGP."""
        pass

    def delete_v4(self):
        """Delete ListConfigBGP.
        """
        pass
