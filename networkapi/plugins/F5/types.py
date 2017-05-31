# -*- coding: utf-8 -*-
import logging

from networkapi.plugins import exceptions as base_exceptions

log = logging.getLogger(__name__)


def address_type(value):

    values = {
        # 'ATYPE_UNSET'
        '*:*': 'ATYPE_STAR_ADDRESS_STAR_PORT',
        '*:$': 'ATYPE_STAR_ADDRESS_EXPLICIT_PORT',
        # 'ATYPE_EXPLICIT_ADDRESS_EXPLICIT_PORT',
        # 'ATYPE_STAR_ADDRESS',
        # 'ATYPE_EXPLICIT_ADDRESS',
    }

    try:
        ipport = value.split(':')
        key = '*:$' if ipport[1] != '*' else '*:*'

        return {
            'address_type': values[key],
            'ipport': {
                'address': ipport[0] if ipport[0] != '*' else '0.0.0.0',
                'port': ipport[1] if ipport[1] != '*' else '0'
            }
        }
    except Exception:
        msg = 'Adress type not is invalid: %s' % (value)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)


def template_type(value):

    values = {
        # 'unset':'TTYPE_UNSET',
        # 'icmp':'TTYPE_ICMP',
        'tcp': 'TTYPE_TCP',
        # 'tcp_echo':'TTYPE_TCP_ECHO',
        # 'external':'TTYPE_EXTERNAL',
        'http': 'TTYPE_HTTP',
        'https': 'TTYPE_HTTPS',
        # 'nntp':'TTYPE_NNTP',
        # 'ftp':'TTYPE_FTP',
        # 'pop3':'TTYPE_POP3',
        # 'smtp':'TTYPE_SMTP',
        # 'mssql':'TTYPE_MSSQL',
        # 'gateway':'TTYPE_GATEWAY',
        # 'imap':'TTYPE_IMAP',
        # 'radius':'TTYPE_RADIUS',
        # 'ldap':'TTYPE_LDAP',
        # 'wmi':'TTYPE_WMI',
        # 'snmp_dca':'TTYPE_SNMP_DCA',
        # 'snmp_dca_base':'TTYPE_SNMP_DCA_BASE',
        # 'real_server':'TTYPE_REAL_SERVER',
        'udp': 'TTYPE_UDP',
        # 'none':'TTYPE_NONE',
        # 'oracle':'TTYPE_ORACLE',
        # 'soap':'TTYPE_SOAP',
        # 'gateway_icmp':'TTYPE_GATEWAY_ICMP',
        # 'sip':'TTYPE_SIP',
        # 'tcp_half_open':'TTYPE_TCP_HALF_OPEN',
        # 'scripted':'TTYPE_SCRIPTED',
        # 'wap':'TTYPE_WAP',
        # 'rpc':'TTYPE_RPC',
        # 'smb':'TTYPE_SMB',
        # 'sasp':'TTYPE_SASP',
        # 'module_score':'TTYPE_MODULE_SCORE',
        # 'firepass':'TTYPE_FIREPASS',
        # 'inband':'TTYPE_INBAND',
        # 'radius_accounting':'TTYPE_RADIUS_ACCOUNTING',
        # 'diameter':'TTYPE_DIAMETER',
        # 'virtual_location':'TTYPE_VIRTUAL_LOCATION',
        # 'mysql':'TTYPE_MYSQL',
        # 'postgresql':'TTYPE_POSTGRESQL'
    }

    try:
        return values[value.lower()]
    except Exception:
        msg = 'Template type not is invalid: %s' % (value)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)


def procotol_type(value):

    values = {
        # 'any': 'PROTOCOL_ANY',
        # 'ipv6': 'PROTOCOL_IPV6',
        # 'routing': 'PROTOCOL_ROUTING',
        # 'none': 'PROTOCOL_NONE',
        # 'fragment': 'PROTOCOL_FRAGMENT',
        # 'dstopts': 'PROTOCOL_DSTOPTS',
        'tcp': 'PROTOCOL_TCP',
        'udp': 'PROTOCOL_UDP',
        # 'icmp': 'PROTOCOL_ICMP',
        # 'icmpv6': 'PROTOCOL_ICMPV6',
        # 'ospf': 'PROTOCOL_OSPF',
        # 'sctp': 'PROTOCOL_SCTP'
    }

    try:
        return values[value.lower()]
    except Exception:
        msg = 'Protocol type not is invalid: %s' % (value)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)
