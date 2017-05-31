# -*- coding: utf-8 -*-
from django.contrib import admin


class ServerPoolAdmin(admin.ModelAdmin):
    search_fields = ['identifier', 'id']
    list_display = ['id', 'identifier',
                    'get_healthcheck', 'default_port', 'pool_created']
    list_filter = ('pool_created',)

    def get_healthcheck(self, obj):
        return obj.healthcheck.healthcheck_type

    get_healthcheck.short_description = 'Healthcheck'
    get_healthcheck.admin_order_field = 'healthcheck__healthcheck_type'
