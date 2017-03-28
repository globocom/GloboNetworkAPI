# -*- coding: utf-8 -*-
from django.contrib import admin


class RequisicaoVipsAdmin(admin.ModelAdmin):
    search_fields = ['id', 'ip']
    list_display = ['id', 'validado',
                    'vip_criado', 'get_ip', 'get_healthcheck']
    list_filter = ('validado', 'vip_criado')

    def get_ip(self, obj):
        return u'{} (id {})'.format(obj.ip.ip_formated, obj.ip.id)

    get_ip.short_description = 'IP'
    # get_ip.admin_order_field = 'book__author'

    def get_healthcheck(self, obj):
        return obj.healthcheck_expect.expect_string

    get_healthcheck.short_description = 'Healthcheck expect'
    get_healthcheck.admin_order_field = 'healthcheck_expect__expect_string'
