# -*- coding: utf-8 -*-
from django.contrib import admin


class VariableAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    list_display = ['id', 'name', 'value', 'description', ]
