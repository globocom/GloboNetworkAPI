# -*- coding: utf-8 -*-
"""Publishes pending outbox events to Pub/Sub. Run it periodically (cron or scheduler)."""
from django.conf import settings
from django.core.management.base import BaseCommand

from networkapi.api_outbox.publisher import PubSubRestPublisher, ServiceAccountTokenProvider
from networkapi.api_outbox.relay import relay_pending


class Command(BaseCommand):
    help = 'Publishes pending outbox events to Pub/Sub (ADR-0003).'

    def handle(self, *args, **options):
        if not getattr(settings, 'OUTBOX_PUBLISH_ENABLED', False):
            self.stdout.write('OUTBOX_PUBLISH_ENABLED is off; nothing published.')
            return

        publisher = PubSubRestPublisher(
            project_id=settings.PUBSUB_PROJECT_ID,
            topic=settings.PUBSUB_TOPIC,
            token_provider=ServiceAccountTokenProvider(settings.PUBSUB_SA_KEY_FILE),
        )
        self.stdout.write(str(relay_pending(publisher)))
