# -*- coding:utf-8 -*_
from django.contrib import admin

class VariableAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]
    list_display = ["id", "name", "value", "description",]
