# -*- coding: utf-8 -*-
from django.contrib import admin

from .event_log import EventLogAdmin
from networkapi.eventlog.models import EventLog

admin.site.register(EventLog, EventLogAdmin)
