# -*- coding:utf-8 -*-
import logging

from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6

log = logging.getLogger(__name__)


def delete_ipv4_list(ipv4_list):
    for ipv4 in ipv4_list:
        ip = Ip.objects.get(id=ipv4)
        ip.delete()


def delete_ipv6_list(ipv6_list):
    for ipv6 in ipv6_list:
        ip = Ipv6.objects.get(id=ipv6)
        ip.delete()
