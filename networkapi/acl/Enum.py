# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''


class Enum(set):

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


NETWORK_TYPES = Enum(["v4", "v6"])
