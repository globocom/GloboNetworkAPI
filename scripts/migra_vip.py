from django.db.transaction import commit_on_success

from networkapi.api_vip_request.models import RequisicaoVips, VipPortToPool
from networkapi.api_vip_request.syncs import old_to_new


@commit_on_success
def run():
    # migrate old vips
    vip_requests = RequisicaoVips.objects.all()
    for vip_request in vip_requests:
        pools = VipPortToPool.get_by_vip_id(vip_request.id)
        old_to_new(vip_request, pools)

    # vip_requests = VipRequest.objects.all()
    # for vip_request in vip_requests:
    #     new_to_old(vip_request)
