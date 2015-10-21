# -*- coding:utf-8 -*_
from django.contrib import admin

class RequisicaoVipsAdmin(admin.ModelAdmin):
    search_fields = ["id", "ip"]
    list_display = ["id", "validado", "vip_criado", "ip", "healthcheck_expect"]
    list_filter = ('validado','vip_criado')


