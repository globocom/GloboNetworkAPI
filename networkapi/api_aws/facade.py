# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_aws import exceptions
from networkapi.api_aws.models import VPC
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_aws_vpc_by_search(search=dict()):
    """
    Return a list of vpcs by dict

    :param search: dict
    """

    try:
        vpcs = VPC.objects.filter()
        vpc_map = build_query_to_datatable_v3(vpcs, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return vpc_map


def get_vpc_by_id(vpc_id):
    """
    Return a vpc by id

    :param vpc_id: id of vpc
    """

    try:
        vpc = VPC.objects.get(id=vpc_id)
    except ObjectDoesNotExist:
        raise exceptions.VPCNotFoundError()

    return vpc


def get_vpcs_by_ids(vpc_ids):
    """
    Return vpc list by ids

    :param vpc_ids: ids list

    """

    vpc_ids = [get_vpc_by_id(vpc_id).id for vpc_id in vpc_ids]

    return VPC.objects.filter(id__in=vpc_ids)


def create_vpc(vpc):
    """
    Create vpc

    :param env: dict
    """

    vpc_obj = VPC()

    vpc_obj.vpc = vpc.get('vpc')

    vpc_obj.create(None)

    return vpc_obj


def update_vpc(vpc):
    """
    Update vpc

    :param vpc: dict
    """

    vpc_obj = get_vpc_by_id(vpc.get('id'))

    VPC.update(
        None,
        vpc_obj.id,
        vpc=vpc.get('vpc')
    )

    return vpc_obj


def delete_vpc(vpc_id):
    """
    Delete vpc

    :param vpc_id: int
    """

    VPC.remove(vpc_id)
