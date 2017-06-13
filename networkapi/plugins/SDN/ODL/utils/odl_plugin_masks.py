# -*- coding: utf-8 -*-


class ODLPluginMasks(object):

    id_ = "{}_{}"
    id_both = "{}_{}_{}"

    description = "{} - {}:{}"
    description_both = "{} - {}:{} - {}:{}"

    @staticmethod
    def to_str_id(arg1, arg2):
        return ODLPluginMasks.id_.format(arg1, arg2)

    @staticmethod
    def to_str_id_both(arg1, arg2, arg3):
        return ODLPluginMasks.id_both.format(arg1, arg2, arg3)

    @staticmethod
    def to_str_description(arg1, arg2, arg3):
        return ODLPluginMasks.description.format(arg1, arg2, arg3)

    @staticmethod
    def to_str_description_both(arg1, arg2, arg3, arg4, arg5):
        return ODLPluginMasks.description_both. \
            format(arg1, arg2, arg3, arg4, arg5)