# -*- coding: utf-8 -*-
from django.contrib import admin


class EventLogAdmin(admin.ModelAdmin):
    search_fields = ['id', 'usuario__user']
    list_display = ['id', 'hora_evento',
                    'get_usuario', 'acao', 'funcionalidade']
    list_filter = ['acao']

    def get_usuario(self, obj):
        return u'{} (id {})'.format(obj.usuario.user, obj.usuario.id)

    get_usuario.short_description = 'usuario'
    get_usuario.admin_order_field = 'usuario__user'
