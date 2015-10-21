# -*- coding:utf-8 -*_
from django.contrib import admin

class ServerPoolAdmin(admin.ModelAdmin):
    search_fields = ["identifier", "ip"]
    list_display = ["id", "identifier", "healthcheck", "default_port", "pool_created"]
    list_filter = ('pool_created',)


