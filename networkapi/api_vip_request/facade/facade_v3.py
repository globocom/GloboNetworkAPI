# -*- coding:utf-8 -*-
import logging

from networkapi.ambiente.models import Ambiente, EnvironmentVip
from networkapi.api_equipment.exceptions import AllEquipmentsAreInMaintenanceException
from networkapi.api_equipment.facade import all_equipments_are_in_maintenance
from networkapi.api_vip_request import exceptions
from networkapi.api_vip_request.models import VipRequest, VipRequestDSCP, VipRequestOptionVip, VipRequestPool
from networkapi.equipamento.models import Equipamento, EquipamentoAcesso, EquipamentoAmbiente
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.ip.models import Ip, Ipv6
from networkapi.plugins.factory import PluginFactory
from networkapi.requisicaovips.models import OptionVip, ServerPoolMember

protocolo_access = 'https'
log = logging.getLogger(__name__)


def get_vip_request(vip_request_ids):
    """
    get Vip Request
    """
    vip_requests = VipRequest.objects.filter(id__in=vip_request_ids)

    return vip_requests


def create_vip_request(vip_request):
    """
    Create Vip Request
    """
    validate_save(vip_request)

    vip = VipRequest()
    vip.name = vip_request['name']
    vip.service = vip_request['service']
    vip.business = vip_request['business']
    vip.environmentvip_id = vip_request['environmentvip']
    vip.port = vip_request['port']
    vip.ipv4 = Ip.get_by_pk(vip_request['ipv4']['id']) if vip_request['ipv4'] else None
    vip.ipv6 = Ipv6.get_by_pk(vip_request['ipv6']['id']) if vip_request['ipv6'] else None

    pool_create = [pool for pool in vip_request['pools']]
    option_create = vip_request['options']
    vip.save()

    _create_pool(pool_create, vip.id)
    _create_option(option_create, vip.id)


def update_vip_request(vip_request):
    """
    update Vip Request
    """
    validate_save(vip_request)

    vip = VipRequest.objects.get(
        id=vip_request['id']
    )
    vip.name = vip_request['name']
    vip.service = vip_request['service']
    vip.business = vip_request['business']
    vip.environmentvip_id = vip_request['environmentvip']
    vip.port = vip_request['port']
    vip.ipv4 = Ip.get_by_pk(vip_request['ipv4']['id']) if vip_request['ipv4'] else None
    vip.ipv6 = Ipv6.get_by_pk(vip_request['ipv6']['id']) if vip_request['ipv6'] else None

    pool_ids = [pool['server_pool'] for pool in vip_request['pools']]
    pool_ids_db = [pool.server_pool_id for pool in vip.viprequestpool_set.all()]
    pool_update = list(set(pool_ids_db) & set(pool_ids))
    pool_remove = list(set(pool_ids_db) - set(pool_ids))
    pool_create = list(set(pool_ids) - set(pool_ids_db))
    pool_create = [pool for pool in vip_request['pools'] if pool['server_pool'] in pool_create]
    pool_update = [pool for pool in vip_request['pools'] if pool['server_pool'] in pool_update]

    option_ids = [option.id for option in vip.viprequestoptionvip_set.all()]
    option_remove = list(set(option_ids) - set(vip_request['options']))
    option_create = list(set(vip_request['options']) - set(option_ids))

    vip.save()

    _create_pool(pool_create, vip.id)
    _update_pool(pool_update, vip.id)
    _delete_pool(pool_remove, vip.id)

    _create_option(option_create, vip.id)
    _delete_option(option_remove)

    dsrl3 = OptionVip.objects.filter(nome_opcao_txt='DSRL3', tipo_opcao='Retorno de trafego').values('id')
    if dsrl3:
        if dsrl3[0]['id'] in option_remove:
            VipRequestDSCP.objects.filter(vip_request=vip.id).delete()


def delete_vip_request(vip_request_ids):
    """delete vip request"""

    VipRequest.objects.filter(id__in=vip_request_ids).delete()


def _create_pool(pools, vip_request_id):
    """Create pools"""
    for pool in pools:
        pl = VipRequestPool()
        pl.vip_request_id = vip_request_id
        pl.server_pool_id = pool['server_pool']
        pl.port = pool['port']
        pl.optionvip_id = pool['optionvip']
        pl.val_optionvip = pool['val_optionvip']
        pl.save()


def _update_pool(pools, vip_request_id):
    """Update pools"""

    for pool in pools:
        pl = VipRequestPool.objects.get(
            vip_request=vip_request_id,
            server_pool=pool['server_pool'])
        pl.port = pool['port']
        pl.optionvip_id = pool['optionvip']
        pl.val_optionvip = pool['val_optionvip']
        pl.save()


def _delete_pool(pools, vip_request_id):
    """Deletes pools"""
    VipRequestPool.objects.filter(
        vip_request=vip_request_id,
        server_pool__in=pools).delete()


def _create_option(options, vip_request_id):
    """create options"""

    for option in options:
        opt = VipRequestOptionVip()
        opt.vip_request_id = vip_request_id
        opt.optionvip_id = option
        opt.save()

    dsrl3 = OptionVip.objects.filter(nome_opcao_txt='DSRL3', tipo_opcao='Retorno de trafego').values('id')
    if dsrl3:
        if dsrl3[0]['id'] in options:
            dscp = _dscp(vip_request_id)
            vip_dscp = VipRequestDSCP()
            vip_dscp.vip_request = vip_request_id
            vip_dscp.dscp = dscp


def _delete_option(options):
    """Deletes options"""
    VipRequestOptionVip.objects.filter(id__in=options).delete()


def get_vip_request_by_search(search=dict()):

    vip_requests = VipRequest.objects.filter()

    vip_requests, total = build_query_to_datatable(
        vip_requests,
        search.get('asorting_cols').split(',') or None,
        search.get('custom_search') or None,
        search.get('searchable_columns') or None,
        search.get('start_record') or 0,
        search.get('end_record') or 25)

    vip_map = dict()
    vip_map["vips"] = vip_requests
    vip_map["total"] = total

    return vip_map


def create_real_vip_request(vip_requests):

    load_balance = dict()
    keys_cache = list()

    for vip_request in vip_requests:

        equips = _validate_vip_to_apply(vip_request)

        EnvironmentVip.objects.get(id=vip_request['id'])

        for e in equips:
            eqpt_id = str(e.equipamento.id)
            equipment_access = EquipamentoAcesso.search(
                equipamento=e.equipamento.id,
                protocolo=protocolo_access
            ).uniqueResult()
            equipment = Equipamento.get_by_pk(e.equipamento.id)

            plugin = PluginFactory.factory(equipment)

            if not load_balance.get(eqpt_id):

                load_balance[eqpt_id] = {
                    'plugin': plugin,
                    'fqdn': equipment_access.fqdn,
                    'user': equipment_access.user,
                    'password': equipment_access.password,
                    'pools': [],
                }

            keys_cache.append('pool:monitor:%s' % pool['identifier'])

            load_balance[eqpt_id]['pools'].append({
                'id': pool['id'],
                'nome': pool['identifier'],
                'lb_method': pool['lb_method'],
                'healthcheck': pool['healthcheck'],
                'action': pool['servicedownaction']['name'],
                'pools_members': [{
                    'id': pool_member['id'],
                    'ip': pool_member['ip']['ip_formated'] if pool_member['ip'] else pool_member['ipv6']['ip_formated'],
                    'port': pool_member['port_real'],
                    'member_status': pool_member['member_status'],
                    'limit': pool_member['limit'],
                    'priority': pool_member['priority'],
                    'weight': pool_member['weight']
                } for pool_member in pool['server_pool_members']]
            })

    for lb in load_balance:
        load_balance[lb]['plugin'].create_pool(load_balance[lb])

    for key_cache in keys_cache:
        cache.delete(key_cache)

    ids = [pool['id'] for pool in pools]
    ServerPool.objects.filter(id__in=ids).update(pool_created=True)


#############
# helpers
#############
def validate_save(vip_request, permit_created=False):

    has_identifier = VipRequest.objects.filter(
        environmentvip__environmentenvironmentvip__environment__in=Ambiente.objects.filter(
            environmentenvironmentvip__environment_vip=vip_request['environmentvip'])
    )

    if vip_request['ipv4']:
        has_identifier = has_identifier.filter(ipv4=vip_request['ipv4']['id'])

        vips = EnvironmentVip.objects.filter(
            environmentenvironmentvip__environment__vlan__networkipv4__ip=vip_request['ipv4']['id']
        ).filter(
            id=vip_request['environmentvip']
        )
        if not vips:
            raise exceptions.IpNotFoundByEnvironment()

    if vip_request['ipv6']:
        has_identifier = has_identifier.filter(ipv6=vip_request['ipv6']['id'])
        vips = EnvironmentVip.objects.filter(
            environmentenvironmentvip__environment__vlan__networkipv6__ipv6=vip_request['ipv6']['id']
        ).filter(
            id=vip_request['environmentvip']
        )
        if not vips:
            raise exceptions.IpNotFoundByEnvironment()

    if vip_request['id']:
        vip = VipRequest.objects.get(id=vip_request['id'])
        if vip.created:
            if not permit_created:
                raise exceptions.CreatedVipRequestValuesException('vip request id: %s' % vip_request['id'])

            if vip.name != vip_request['name'] or vip.environmentvip_id != vip_request['environmentvip']:
                raise exceptions.CreatedVipRequestValuesException('vip request id: %s' % vip_request['id'])

        has_identifier = has_identifier.exclude(id=vip_request['id'])

    has_identifier = has_identifier.distinct()
    if has_identifier.count() > 0:
        raise exceptions.AlreadyVipRequestException()

    for pool in vip_request['pools']:

        spms = ServerPoolMember.objects.filter(server_pool=pool['server_pool'])
        for spm in spms:
            if spm.ip:

                vips = EnvironmentVip.objects.filter(
                    environmentenvironmentvip__environment__vlan__networkipv4__ip=spm.ip
                ).filter(
                    id=vip_request['environmentvip']
                )
                if not vips:
                    raise exceptions.ServerPoolMemberDiffEnvironmentVipException(spm.identifier)
            if spm.ipv6:

                vips = EnvironmentVip.objects.filter(
                    environmentenvironmentvip__environment__vlan__networkipv6__ipv6=spm.ipv6
                ).filter(
                    id=vip_request['environmentvip']
                )
                if not vips:
                    raise exceptions.ServerPoolMemberDiffEnvironmentVipException(spm.identifier)


def _dscp(vip_request_id):
    members = VipRequestDSCP.objects.filter(
        vip_request__viprequestpool__server_pool__serverpoolmember__in=ServerPoolMember.objects.filter(
            server_pool__viprequestpool__vip_request__id=vip_request_id)).distinct().values('dscp')
    mb = [i.get('dscp') for i in members]
    perm = range(3, 64)
    perm_new = list(set(perm) - set(mb))
    if perm_new:
        return perm_new[0]
    else:
        raise Exception('não pode usar esses pools')


def _validate_vip_to_apply(vip_request, update=False):
    vip = VipRequest.objects.get(
        name=vip_request['name'],
        environmentvip=vip_request['environmentvip'],
        id=vip_request['id'])
    if not vip:
        raise exceptions.VipRequestDoesNotExistException()

    if update and not vip.created:
        raise exceptions.VipRequestNotCreated(vip.id)

    equips = EquipamentoAmbiente.objects.filter(
        equipamento__maintenance=0,
        ambiente__environmentenvironmentvip__environment_vip__id=vip_request['environmentvip'],
        equipamento__tipo_equipamento__tipo_equipamento=u'Balanceador')

    conf = EnvironmentVip.objects.get(id=vip_request['environmentvip']).conf

    if all_equipments_are_in_maintenance([e.equipamento for e in equips]):
        raise AllEquipmentsAreInMaintenanceException()

    return equips, conf
