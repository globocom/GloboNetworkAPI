from django.contrib import admin
from networkapi.requisicaovips.models import ServerPoolMember, RequisicaoVips, ServerPool

from .server_pool_member import ServerPoolMemberAdmin
from .server_pool import ServerPoolAdmin
from .requisicao_vip import RequisicaoVipsAdmin

admin.site.register(ServerPoolMember, ServerPoolMemberAdmin)
admin.site.register(ServerPool, ServerPoolAdmin)
admin.site.register(RequisicaoVips, RequisicaoVipsAdmin)