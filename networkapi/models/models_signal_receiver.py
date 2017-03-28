# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import re

from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from networkapi.eventlog.models import AuditRequest
from networkapi.eventlog.models import EventLog
from networkapi.util import signals_helper as m2m_audit

MODEL_LIST = set()
LOG = logging.getLogger(__name__)
DEFAULT_CACHE_TIMEOUT = 120


def get_cache_key_for_instance(instance, cache_prefix='networkapi_event_log'):

    return '%s:%s:%s' % (cache_prefix, instance.__class__.__name__, instance.pk)


def get_value(obj, attr):
    """
    Returns the value of an attribute. First it tries to return the unicode value.
    """
    if hasattr(obj, attr):
        try:
            return getattr(obj, attr).__unicode__()
        except:
            value = getattr(obj, attr)
            if hasattr(value, 'all'):
                return [v.__unicode__() for v in value.all()]
            else:
                return value
    else:
        return None


def to_dict(obj):
    if obj is None:
        return {}

    if isinstance(obj, dict):
        return dict.copy()

    state = {}

    for key in obj._meta.get_all_field_names():
        state[key] = get_value(obj, key)

    return state


def dict_diff(old, new):

    keys = set(old.keys() + new.keys())
    diff = {}
    for key in keys:
        old_value = old.get(key, None)
        new_value = new.get(key, None)
        if old_value != new_value:
            try:
                if re.match(key, 'password'):
                    old_value = 'xxxxxxxx'
                    new_value = '*' * len(new.get(key))
                elif re.match(key, 'pwd'):
                    old_value = 'xxxxxxxx'
                    new_value = '*' * len(new.get(key))
                elif re.match(key, 'enable_pass'):
                    old_value = 'xxxxxxxx'
                    new_value = '*' * len(new.get(key))
            except:
                pass
            diff[key] = (old_value, new_value)

    # if diff:
    #     LOG.debug("dict_diff: %s" % diff)
    return diff


def format_value(v):
    if isinstance(v, basestring):
        return u"'%s'" % v
    return unicode(v)


def save_audit(instance, operation, kwargs={}):
    """
    Saves the audit.
    However, the variable persist_audit controls if the audit should be really
    saved to the database or not. This variable is only affected in a change operation. If no
    change is detected than it is setted to False.

    Keyword arguments:
    instance -- instance
    operation -- operation type (add, change, delete)
    kwargs -- kwargs dict sent from m2m signal
    """

    m2m_change = kwargs.get('m2m_change', False)
    event = dict()
    action = None
    try:
        persist_audit = True

        new_state = to_dict(instance)
        old_state = {}
        try:
            if operation == EventLog.CHANGE and instance.pk:
                if not m2m_change:
                    old_state = to_dict(
                        instance.__class__.objects.get(pk=instance.pk))
                else:
                    # m2m change
                    LOG.debug('m2m change detected')
                    new_state = kwargs.get('new_state', {})
                    old_state = kwargs.get('old_state', {})
        except:
            pass

        if m2m_change:
            # m2m_change returns a list of changes
            changed_fields = m2m_audit.m2m_dict_diff(old_state, new_state)
        else:
            changed_fields = dict_diff(old_state, new_state)

        ########################
        # CHANGE OPERATION
        ########################
        if operation == EventLog.CHANGE:
            action = 'Alterar'
            # is there any change?
            if not changed_fields:
                persist_audit = False

            if m2m_change:
                descriptions = []
                for changed_field in changed_fields:
                    description = u'\n'.join([u'%s %s: %s %s %s %s' %
                                              (
                                                  _('field'),
                                                  k,
                                                  _('was changed from'),
                                                  format_value(v[0]),
                                                  _('to'),
                                                  format_value(v[1]),
                                              ) for k, v in changed_field.items()])
                    descriptions.append(description)
            else:
                description = u'\n'.join([u'%s %s: %s %s %s %s' %
                                          (
                                              _('field'),
                                              k,
                                              _('was changed from'),
                                              format_value(v[0]),
                                              _('to'),
                                              format_value(v[1]),
                                          ) for k, v in changed_fields.items()])
        elif operation == EventLog.DELETE:
            action = 'Remover'
            description = _('Deleted %s') % unicode(instance)
        elif operation == EventLog.ADD:
            action = 'Cadastrar'
            description = _('Added %s') % unicode(instance)

        # LOG.debug("called audit with operation=%s instance=%s persist=%s" % (operation, instance, persist_audit))
        if persist_audit:
            if m2m_change:
                for description in descriptions:
                    obj_description = (
                        instance and unicode(instance) and '')[:100]
                    audit_request = AuditRequest.current_request(True)

                    changed_field = changed_fields.pop(0)
                    old_value_list = []
                    new_value_list = []
                    for field, (old_value, new_value) in changed_field.items():
                        old_value_list.append('{0} : {1}'.format(
                            field, handle_unicode(old_value)))
                        new_value_list.append('{0} : {1}'.format(
                            field, handle_unicode(new_value)))

                    event['acao'] = 'Alterar' if action is None else action
                    event['funcionalidade'] = instance.__class__.__name__
                    event['parametro_anterior'] = u'\n'.join(old_value_list)
                    event['parametro_atual'] = u'\n'.join(new_value_list)
                    event['id_objeto'] = instance.pk
                    event['audit_request'] = audit_request
                    # save the event log
                    if audit_request:
                        EventLog.log(audit_request.user, event)
                    else:
                        EventLog.log(None, event)

            else:
                obj_description = (instance and unicode(instance) and '')[:100]
                audit_request = AuditRequest.current_request(True)

                old_value_list = []
                new_value_list = []
                for field, (old_value, new_value) in changed_fields.items():
                    old_value_list.append('{0} : {1}'.format(
                        field, handle_unicode(old_value)))
                    new_value_list.append('{0} : {1}'.format(
                        field, handle_unicode(new_value)))

                event['acao'] = 'Alterar' if action is None else action
                event['funcionalidade'] = instance.__class__.__name__
                event['parametro_anterior'] = u'\n'.join(old_value_list)
                event['parametro_atual'] = u'\n'.join(new_value_list)
                event['id_objeto'] = instance.pk
                event['audit_request'] = audit_request
                if audit_request:
                    EventLog.log(audit_request.user, event)
                else:
                    EventLog.log(None, event)
    except:
        LOG.error(u'Error registering auditing to %s: (%s) %s',
                  repr(instance), type(instance), getattr(instance, '__dict__', None), exc_info=True)

###################
# SIGNALS         #
###################
# @receiver(pre_delete)


def audit_pre_delete(sender, instance, **kwargs):

    # instance=kwargs.get('instance')
    from networkapi.models.BaseModel import BaseModel

    if (not issubclass(instance.__class__, BaseModel)):
        return

    save_audit(instance, EventLog.DELETE)

# @receiver(pre_save)


def audit_pre_save(sender, instance, **kwargs):

    # instance=kwargs.get('instance')
    from networkapi.models.BaseModel import BaseModel

    if (not issubclass(instance.__class__, BaseModel)):
        return

    if instance.pk:
        if m2m_audit.get_m2m_fields_for(instance):  # has m2m fields?
            cache_key = get_cache_key_for_instance(instance)
            dict_ = {'old_state': {}, 'new_state': {}}
            dict_['old_state'] = m2m_audit.get_m2m_values_for(
                instance=instance)
            cache.set(cache_key, dict_, DEFAULT_CACHE_TIMEOUT)
            LOG.debug(
                'old_state saved in cache with key %s for m2m auditing' % cache_key)
        save_audit(instance, EventLog.CHANGE)


def audit_post_save(sender, instance, created, **kwargs):

    from networkapi.models.BaseModel import BaseModel

    if (not issubclass(instance.__class__, BaseModel)):
        return

    if created:
        save_audit(instance, EventLog.ADD)


def handle_unicode(s):
    if isinstance(s, basestring):
        return s.encode('utf-8')
    return s


# # Registra os processadores de signals post_save e post_delete
# post_save.connect(networkapi_post_save)
# post_delete.connect(networkapi_post_delete)


######
# pre_save.connect(audit_pre_save)
# post_save.connect(audit_post_save)
# pre_delete.connect(audit_pre_delete)
