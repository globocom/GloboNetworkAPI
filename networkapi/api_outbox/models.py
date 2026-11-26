# -*- coding: utf-8 -*-
"""Outbox of BGP table changes waiting to be published to Pub/Sub (ADR-0003)."""
from django.db import models


class OutboxEvent(models.Model):

    event_id = models.CharField(max_length=36, unique=True)
    aggregate = models.CharField(max_length=40)
    aggregate_id = models.IntegerField()
    op = models.CharField(max_length=10)
    version = models.IntegerField()
    origin = models.CharField(max_length=10)
    occurred_at = models.DateTimeField()
    payload = models.TextField()
    status = models.CharField(max_length=12, default='pending', db_index=True)
    attempts = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'outbox_event'


# Connects the capture handlers. Kept at the bottom: capture imports OutboxEvent.
from networkapi.api_outbox import capture  # noqa: E402,F401
