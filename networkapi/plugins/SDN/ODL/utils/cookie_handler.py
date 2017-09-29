# -*- coding: utf-8 -*-


class CookieHandler(object):
    """This class intends to Handle the cookie field described by the
        OpenFlow Specification and present in OpenVSwitch.

        Cookie field has 64 bits. The first 32-bits are assigned to the id
        of ACL input. The next 32 bits are assigned to the ID of the
        environment.
    """

    def __init__(self, id_acl, id_env=0):

        self.id_acl = format(int(id_acl), '032b')
        self.id_env = format(int(id_env), '032b')

        self._cookie = self.id_acl + self.id_env

    @property
    def cookie(self):
        return int(self._cookie, 2)

    def raw(self):
        return self._cookie

    def get_id_acl(self):
        return int(self._cookie[0:32], 2)

    def get_id_environment(self):
        return int(self._cookie[32:64], 2)
