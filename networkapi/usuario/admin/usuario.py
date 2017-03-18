# -*- coding: utf-8 -*-
from django.contrib import admin

from networkapi.usuario.models import UsuarioGrupo

# class GruposInline(admin.TabularInline):
#     model = Usuario.grupos.through


class GruposInline(admin.TabularInline):
    model = UsuarioGrupo
    # filter_horizontal = ('ugrupo',)


class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ['id', 'user']
    list_display = ['id', 'user', 'nome', 'email', 'ativo', 'get_grupos']
    list_filter = ['ativo']
    inlines = [GruposInline]
    filter_horizontal = ('grupos',)

    def get_grupos(self, obj):
        return '{}'.format([grupo.nome for grupo in obj.grupos.all()])

    get_grupos.short_description = 'Grupos'
