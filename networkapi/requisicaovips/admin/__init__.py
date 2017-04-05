# -*- coding: utf-8 -*-
from django.contrib import admin

from .requisicao_vip import RequisicaoVipsAdmin
from .server_pool import ServerPoolAdmin
from .server_pool_member import ServerPoolMemberAdmin
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolMember

admin.site.register(ServerPoolMember, ServerPoolMemberAdmin)
admin.site.register(ServerPool, ServerPoolAdmin)
admin.site.register(RequisicaoVips, RequisicaoVipsAdmin)
