# -*- coding: utf-8 -*-
# copyright: https://github.com/leandrosouza/django-simple-audit
from __future__ import absolute_import
from __future__ import unicode_literals

import copy
import logging
from pprint import pprint

LOG = logging.getLogger(__name__)


def ValuesQuerySetToDict(vqs):
    """converts a ValuesQuerySet to Dict"""
    return [item for item in vqs]


def get_m2m_fields_for(instance=None):
    """gets m2mfields for instance"""
    return instance._meta._many_to_many()


def get_m2m_values_for(instance=None):
    values = {}
    for m2m_field in get_m2m_fields_for(instance=instance):
        values[m2m_field.verbose_name] = ValuesQuerySetToDict(
            m2m_field._get_val_from_obj(instance).values())

    return copy.deepcopy(values)


def normalize_dict(d):
    """removes datetime objects and passwords"""
    for k in d.keys():
        if d.get(k).find('password') != -1:
            d[k] = 'xxxxx'

    return d


def m2m_proccess_diff_states(old, new):
    """
    old and new are dictionaries in the following format

    old:
    {u'toppings.1': {u'id': [1, None], 'name': [u'ceboloa', None]},
     u'toppings.11': {u'id': [11, None], 'name': [u'abacate', None]},
     u'toppings.5': {u'id': [5, None], 'name': [u'cogumelo', None]},
     u'toppings.6': {u'id': [6, None], 'name': [u'abobrinha', None]},
     u'toppings.8': {u'id': [8, None], 'name': [u'codorna', None]},
     u'toppings.9': {u'id': [9, None], 'name': [u'banana', None]}}

    new:
    {u'toppings.1': {u'id': [None, 1], 'name': [None, u'ceboloa']},
     u'toppings.10': {u'id': [None, 10], 'name': [None, u'abacaxi']},
     u'toppings.5': {u'id': [None, 5], 'name': [None, u'cogumelo']},
     u'toppings.6': {u'id': [None, 6], 'name': [None, u'abobrinha']},
     u'toppings.8': {u'id': [None, 8], 'name': [None, u'codorna']},
     u'toppings.9': {u'id': [None, 9], 'name': [None, u'banana']}}
    """
    # print "old..."
    # pprint(old)
    # print "^^^"
    # print "new..."
    # pprint(new)
    # print "^^^"

    diff = copy.deepcopy(old)
    new_copy = copy.deepcopy(new)
    for field_id in old.keys():
        old_ = old[field_id]
        if field_id in new_copy:
            for k in old_.keys():
                try:
                    diff[field_id][k][1] = new_copy[field_id][k][1]
                except:
                    pass
            del new_copy[field_id]

    # add remaining items in new_copy to diff
    for field_id in new_copy.keys():
        new_ = new_copy[field_id]
        diff[field_id] = new_

    return diff


def m2m_clean_unchanged_fields(dict_diff):
    """
    returns a list of dicts with only the changes
    """
    dict_list = []
    for key in dict_diff.keys():
        new_dict = {}
        dict_ = dict_diff.get(key)

        for value in dict_.keys():
            compound_key = '%s.%s' % (key, value)
            if dict_[value][0] == dict_[value][1]:
                del dict_[value]
            else:
                new_dict[compound_key] = dict_[value]

        del dict_diff[key]
        if new_dict:
            dict_list.append(new_dict)

    return dict_list


def m2m_dict_diff(old, new):

    # old is empty?
    swap = False
    if not old:
        # set old to new, then swap elements at the end
        old = new
        new = {}
        swap = True

    # first create empty diff based in old state
    field_name = None
    diff_old = {}
    diff_new = {}
    for key in old.keys():
        field_name = key
        ###########
        # oldstate
        ##########
        id_ = 0
        for item in old[key]:
            empty_dict = {}
            for key_ in item.keys():
                if key_ == 'id':
                    id_ = item[key_]
                # when old is empty, the dicts are swapped
                if swap:
                    empty_dict[key_] = [None, item[key_]]
                else:
                    empty_dict[key_] = [item[key_], None]

            diff_old['%s.%s' % (field_name, id_)] = empty_dict

        ############
        # new state
        ############
        id_ = 0
        for item in new.get(key, {}):
            empty_dict = {}
            for key_ in item.keys():
                if key_ == 'id':
                    id_ = item[key_]
                empty_dict[key_] = [None, item[key_]]

            diff_new['%s.%s' % (field_name, id_)] = empty_dict

    if swap:
        diff_old, diff_new = diff_new, diff_old

    diff = m2m_proccess_diff_states(diff_old, diff_new)

    diff = m2m_clean_unchanged_fields(diff)

    if diff:
        LOG.debug('m2m diff cleaned: %s' % pprint(diff))

    return diff


def persist_m2m_audit():
    pass
