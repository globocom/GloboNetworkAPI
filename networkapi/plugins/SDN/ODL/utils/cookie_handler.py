# -*- coding: utf-8 -*-


class CookieHandler(object):
    """This class intends to Handle the cookie field described by the
        OpenFlow Specification and present in OpenVSwitch.

        Cookie field has 64 bits. The first 32-bits are assigned to the id
        of ACL input. The next 32 bits are assigned to the ID of the
        environment.
    """

    def __init__(self, id_acl, id_env):

        id_acl = format(int(id_acl), '032b')
        id_environment = format(int(id_env), '032b')

        self.cookie = id_acl + id_environment

    @property
    def cookie(self):
        return int(self.cookie, 2)

    def raw(self):
        return self.cookie

    def get_id_acl(self):
        return int(self.cookie[0:32], 2)

    def get_id_environment(self):
        return int(self.cookie[32:64], 2)
