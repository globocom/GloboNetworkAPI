# -*- coding: utf-8 -*-
"""Tests for the outbox capture and the relay (ADR-0003)."""
import json

from django.test import TestCase

from networkapi.api_asn.models import Asn
from networkapi.api_outbox.capture import suppressed_capture
from networkapi.api_outbox.models import OutboxEvent
from networkapi.api_outbox.relay import relay_pending
from networkapi.api_outbox.relay import STATUS_DEAD
from networkapi.api_outbox.relay import STATUS_PENDING
from networkapi.api_outbox.relay import STATUS_PUBLISHED
from networkapi.api_outbox.publisher import build_envelope
from networkapi.api_outbox.publisher import ordering_key


class FakePublisher(object):

    def __init__(self, fail_ids=()):
        self.sent = []
        self.fail_ids = set(fail_ids)

    def publish(self, envelope):
        if envelope['aggregate_id'] in self.fail_ids:
            raise RuntimeError('pubsub unavailable')
        self.sent.append(envelope)


def _events():
    return list(OutboxEvent.objects.order_by('id'))


class OutboxCaptureTest(TestCase):

    def test_insert_emits_upsert_with_version_one(self):
        asn = Asn(name='64512')
        asn.save()

        events = _events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.aggregate, 'asn')
        self.assertEqual(event.aggregate_id, asn.id)
        self.assertEqual(event.op, 'upsert')
        self.assertEqual(event.version, 1)
        self.assertEqual(event.origin, 'legacy')
        self.assertEqual(event.status, STATUS_PENDING)
        self.assertEqual(json.loads(event.payload)['name'], '64512')

    def test_update_increments_version(self):
        asn = Asn(name='64512')
        asn.save()
        asn.description = 'alterado'
        asn.save()

        self.assertEqual([e.version for e in _events()], [1, 2])
        self.assertEqual(json.loads(_events()[1].payload)['description'], 'alterado')

    def test_delete_emits_delete_with_last_state(self):
        asn = Asn(name='64513')
        asn.save()
        asn_id = asn.id
        asn.delete()

        events = _events()
        self.assertEqual([e.op for e in events], ['upsert', 'delete'])
        self.assertEqual(events[1].aggregate_id, asn_id)
        self.assertEqual(events[1].version, 2)
        self.assertEqual(json.loads(events[1].payload)['name'], '64513')

    def test_suppressed_capture_skips_events(self):
        with suppressed_capture():
            Asn(name='64514').save()
        self.assertEqual(_events(), [])

        Asn(name='64515').save()
        self.assertEqual(len(_events()), 1)


class OutboxEnvelopeTest(TestCase):

    def test_envelope_and_ordering_key(self):
        Asn(name='64516').save()
        event = _events()[0]

        envelope = build_envelope(event)
        self.assertEqual(
            sorted(envelope.keys()),
            ['aggregate', 'aggregate_id', 'event_id', 'occurred_at', 'op', 'origin', 'payload', 'version'],
        )
        self.assertEqual(ordering_key(envelope), 'asn:%s' % event.aggregate_id)


class OutboxRelayTest(TestCase):

    def test_relay_publishes_in_order_and_marks_published(self):
        asn = Asn(name='64517')
        asn.save()
        asn.description = 'v2'
        asn.save()

        publisher = FakePublisher()
        result = relay_pending(publisher)

        self.assertEqual(result, {'published': 2, 'failed': 0, 'held': 0, 'dead': 0})
        self.assertEqual([e['version'] for e in publisher.sent], [1, 2])
        self.assertTrue(all(e.status == STATUS_PUBLISHED for e in _events()))

    def test_relay_holds_later_events_for_the_same_row_after_a_failure(self):
        failing = Asn(name='64518')
        failing.save()
        other = Asn(name='64519')
        other.save()
        failing.description = 'v2'
        failing.save()

        result = relay_pending(FakePublisher(fail_ids={failing.id}))

        self.assertEqual(result['published'], 1)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['held'], 1)
        failing_events = [e for e in _events() if e.aggregate_id == failing.id]
        self.assertTrue(all(e.status == STATUS_PENDING for e in failing_events))
        self.assertIn('pubsub unavailable', failing_events[0].last_error)

    def test_relay_marks_dead_after_max_attempts(self):
        asn = Asn(name='64520')
        asn.save()

        publisher = FakePublisher(fail_ids={asn.id})
        for _ in range(3):
            relay_pending(publisher, max_attempts=3)

        event = _events()[0]
        self.assertEqual(event.status, STATUS_DEAD)
        self.assertEqual(event.attempts, 3)
