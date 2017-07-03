# -*- coding: utf-8 -*-
from django.contrib import admin


class ServerPoolMemberAdmin(admin.ModelAdmin):
    search_fields = ['identifier', 'ip', 'server_pool__identifier']
    list_display = ['id', 'get_server_pool', 'identifier', 'get_ip']

    def get_ip(self, obj):
        return u'{} (id {})'.format(obj.ip.ip_formated, obj.ip.id)

    def get_server_pool(self, obj):
        return obj.server_pool.identifier

    get_server_pool.short_description = 'Server Pool'
    get_server_pool.admin_order_field = 'server_pool__identifier'
