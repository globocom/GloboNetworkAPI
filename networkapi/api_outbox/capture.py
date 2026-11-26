# -*- coding: utf-8 -*-
"""Captures writes to the BGP tables and records them in outbox_event (ADR-0003).

Handlers run on Django model signals, so every save/delete made through the ORM
is captured, including cascades. Queryset .update() and raw SQL are not captured.
The event row is written on the same database connection as the change, so a
rollback discards both.
"""
import json
import threading
import uuid
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal

from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save

from networkapi.api_outbox.models import OutboxEvent

# Tables replicated to the BGP microservice. Must match src/outbox/capture.py in networkapi-bgp.
TRACKED_TABLES = frozenset([
    'asn',
    'asn_equipment',
    'route_map',
    'route_map_entry',
    'equipment_route_map',
    'peer_group',
    'environment_peer_group',
    'neighbor_v4',
])

ORIGIN_LEGACY = 'legacy'

_state = threading.local()


@contextmanager
def suppressed_capture():
    """Skip capture inside the block. Use it when applying events that came from the BGP side."""
    previous = getattr(_state, 'suppressed', False)
    _state.suppressed = True
    try:
        yield
    finally:
        _state.suppressed = previous


def _is_suppressed():
    return getattr(_state, 'suppressed', False)


def _is_tracked(model):
    return model._meta.db_table in TRACKED_TABLES


def _serialize(instance):
    """Column values keyed by DB column name, the same keys the BGP service uses."""
    data = {}
    for field in instance._meta.concrete_fields:
        value = getattr(instance, field.attname)
        if isinstance(value, (datetime, date)):
            value = value.isoformat()
        elif isinstance(value, Decimal):
            value = str(value)
        data[field.column] = value
    return data


def _next_version(model, instance):
    if instance.pk is None:
        return 1
    current = list(model._base_manager.filter(pk=instance.pk).values_list('version', flat=True))
    return (current[0] if current else 0) + 1


def _record(table, aggregate_id, op, version, payload):
    OutboxEvent.objects.create(
        event_id=str(uuid.uuid4()),
        aggregate=table,
        aggregate_id=aggregate_id,
        op=op,
        version=version,
        origin=ORIGIN_LEGACY,
        occurred_at=datetime.utcnow(),
        payload=json.dumps(payload, default=str, sort_keys=True),
        status='pending',
        attempts=0,
    )


def _on_pre_save(sender, instance, raw=False, **kwargs):
    if raw or _is_suppressed() or not _is_tracked(sender):
        return
    instance.version = _next_version(sender, instance)


def _on_post_save(sender, instance, created=False, raw=False, **kwargs):
    if raw or _is_suppressed() or not _is_tracked(sender):
        return
    _record(sender._meta.db_table, instance.pk, 'upsert', instance.version, _serialize(instance))


def _on_pre_delete(sender, instance, **kwargs):
    if _is_suppressed() or not _is_tracked(sender):
        return
    # Read the state now: the row is gone after the DELETE.
    instance._outbox_delete = (instance.pk, _next_version(sender, instance), _serialize(instance))
    instance.version = instance._outbox_delete[1]


def _on_post_delete(sender, instance, **kwargs):
    pending = getattr(instance, '_outbox_delete', None)
    if pending is None:
        return
    instance._outbox_delete = None
    aggregate_id, version, payload = pending
    _record(sender._meta.db_table, aggregate_id, 'delete', version, payload)


pre_save.connect(_on_pre_save, dispatch_uid='outbox_pre_save')
post_save.connect(_on_post_save, dispatch_uid='outbox_post_save')
pre_delete.connect(_on_pre_delete, dispatch_uid='outbox_pre_delete')
post_delete.connect(_on_post_delete, dispatch_uid='outbox_post_delete')
