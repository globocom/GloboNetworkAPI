# -*- coding: utf-8 -*-


class CookieHandler(object):
    """This class intends to Handle the cookie field described by the
        OpenFlow Specification and present in OpenVSwitch.

        Cookie field has 64 bits. The first 32-bits are assigned to the id
        of ACL input. The next 4 bits are assigned to the operation type and
        the remaining 28 bits are filled by zeros.
    """

    @staticmethod
    def get_cookie(id_acl, src_port=0, dst_port=0):
        id_acl = format(int(id_acl), '032b')
        src_port = format(int(src_port), '016b')
        dst_port = format(int(dst_port), '016b')

        cookie = id_acl + src_port + dst_port

        return int(cookie, 2)

    @staticmethod
    def get_id_acl(cookie):
        cookie = format(cookie, '064b')

        return int(cookie[0:32], 2)

    @staticmethod
    def get_src_port(cookie):
        cookie = format(cookie, '064b')

        return int(cookie[32:48], 2)

    @staticmethod
    def get_dst_port(cookie):
        cookie = format(cookie, '064b')

        return int(cookie[48:64], 2)
