from django.db.transaction import commit_on_success

from networkapi.api_vip_request.syncs import old_to_new
from networkapi.requisicaovips.models import RequisicaoVips


@commit_on_success
def sync_vip():
    # migrate old vips
    vip_requests = RequisicaoVips.objects.all()
    for vip_request in vip_requests:
        old_to_new(vip_request)


def run():
    sync_vip()
