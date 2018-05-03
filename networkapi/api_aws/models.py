# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_aws.exceptions import VPCError
from networkapi.api_aws.exceptions import VPCNotFoundError
from networkapi.api_aws.exceptions import VPCRelatedToEnvironment
from networkapi.filter.models import FilterNotFoundError
from networkapi.models.BaseModel import BaseModel


class VPC(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    vpc = models.TextField(
        max_length=45,
        db_column='vpc_id'
    )

    log = logging.getLogger('VPC')

    class Meta (BaseModel.Meta):
        managed = True
        db_table = u'aws_vpc'

    @classmethod
    def get_by_pk(cls, id_vpc):
        """Get VPC by id.

        @return: VPC.

        @raise VPCNotFoundError: VPC is not registered.
        @raise VPCError: Failed to search for the VPC.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return VPC.objects.filter(id=id_vpc).uniqueResult()
        except ObjectDoesNotExist as e:
            raise VPCNotFoundError(
                u'Dont there is a VPC by pk = %s.' % id_vpc)
        except OperationalError as e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                u'Lock wait timeout exceeded; try restarting transaction')
        except Exception as e:
            cls.log.error(u'Failure to search the VPC. Error: {}'.format(e))
            raise VPCError(u'Failure to search the VPC. Error: {}'.format(e))

    def create(self, authenticated_user):
        """Include new VPC.

        @return: Id new VPC

        @raise FilterNotFoundError: Dont' exist filter for pk searched
        """

        try:
            return self.save()

        except FilterNotFoundError as e:
            raise e
        except Exception:
            self.log.error(u'Fail on inserting VPC.')

    @classmethod
    def update(cls, authenticated_user, pk, **kwargs):
        """Change some VPC.

        @return: Nothing

        @raise VPCNotFoundError: It doesn't exist VPC for searched pk.

        @raise CannotDissociateFilterError: Filter in use, can't be dissociated.
        """
        vpc = VPC().get_by_pk(pk)

        try:
            try:
                vpc.objects.get(id=pk)
            except vpc.DoesNotExist:
                pass

            vpc.__dict__.update(kwargs)
            vpc.save(authenticated_user)

        except Exception as e:
            cls.log.error(u'Fail to change VPC. Error: {}'.format(e))

    @classmethod
    def remove(cls, pk):
        """Remove VPC.

        @return: Nothing

        @raise VPCNotFoundError: It doesn' exist VPC to searched id

        @raise VPCRelatedToEnvironment: At least one Environment is using this VPC

        """

        vpc = VPC().get_by_pk(pk)

        entry_env = vpc.ambiente_set.all()

        if len(entry_env) > 0:
            cls.log.error(u'Fail to remove VPC.')
            raise VPCRelatedToEnvironment(
                u'VPC with pk = %s is being used at some environment.' %
                pk)

        vpc.delete()
