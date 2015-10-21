# -*- coding:utf-8 -*_
from django.contrib import admin

class ServerPoolMemberAdmin(admin.ModelAdmin):
    search_fields = ["identifier", "ip"]
    list_display = ["id", "server_pool", "identifier", "ip"]


