# -*- coding: utf-8 -*-

class CookieHandler(object):
    """This class intends to Handle the cookie field described by the 
        OpenFlow Specification and present in OpenVSwitch.

        Cookie field has 64 bits. The first 32-bits are assigned to the id
        of ACL input. The next 4 bits are assigned to the operation type and
        the remaining 28 bits are filled by zeros.
    """

    @staticmethod
    def get_cookie(id_acl, op_type):
        id_acl = format(int(id_acl), '032b')
        op_type = format(int(op_type), '04b')
        padding = format(0, '028b')

        cookie = id_acl + op_type + padding

        return int(cookie, 2)

    @staticmethod
    def get_id_acl(cookie):
        cookie = format(cookie, '064b')

        return int(cookie[0:32], 2)

    @staticmethod
    def get_op_type(cookie):
        cookie = format(cookie, '064b')

        return int(cookie[32:36], 2)
