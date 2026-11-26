# -*- coding: utf-8 -*-
"""Relay: publishes pending outbox events in order and records each outcome (ADR-0003)."""
import logging
from datetime import datetime

from networkapi.api_outbox.models import OutboxEvent
from networkapi.api_outbox.publisher import build_envelope

log = logging.getLogger(__name__)

STATUS_PENDING = 'pending'
STATUS_PUBLISHED = 'published'
STATUS_DEAD = 'dead'
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_ATTEMPTS = 10
MAX_ERROR_LENGTH = 2000


def relay_pending(publisher, batch_size=DEFAULT_BATCH_SIZE, max_attempts=DEFAULT_MAX_ATTEMPTS):
    """Publish one batch of pending events.

    - Events go out in id order.
    - After a failure for a row, later events for that same row are held back in this run.
    - Each outcome is saved on its own, so progress survives a crash. A crash between
      publish and save can resend an event; consumers dedupe by event_id.
    - After max_attempts failures an event is marked dead for manual reprocessing.
    """
    events = list(OutboxEvent.objects.filter(status=STATUS_PENDING).order_by('id')[:batch_size])
    result = {'published': 0, 'failed': 0, 'held': 0, 'dead': 0}
    held_rows = set()

    for event in events:
        row = (event.aggregate, event.aggregate_id)
        if row in held_rows:
            result['held'] += 1
            continue

        try:
            publisher.publish(build_envelope(event))
        except Exception as exc:  # any publish failure is recorded and retried later
            event.attempts += 1
            event.last_error = str(exc)[:MAX_ERROR_LENGTH]
            held_rows.add(row)
            if event.attempts >= max_attempts:
                event.status = STATUS_DEAD
                result['dead'] += 1
                log.error('Outbox event %s marked dead after %s attempts: %s', event.event_id, event.attempts, exc)
            else:
                result['failed'] += 1
                log.warning('Outbox event %s failed (attempt %s): %s', event.event_id, event.attempts, exc)
        else:
            event.status = STATUS_PUBLISHED
            event.published_at = datetime.utcnow()
            event.last_error = None
            result['published'] += 1

        event.save()

    return result
