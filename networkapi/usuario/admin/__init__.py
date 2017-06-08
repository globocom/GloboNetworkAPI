# -*- coding: utf-8 -*-
from django.contrib import admin

from .usuario import UsuarioAdmin
from networkapi.usuario.models import Usuario

admin.site.register(Usuario, UsuarioAdmin)
