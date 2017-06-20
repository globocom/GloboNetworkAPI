# -*- coding: utf-8 -*-
import copy
import json
import logging

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import commit_on_success

from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_equipment import exceptions as exceptions_eqpt
from networkapi.api_equipment import facade as facade_eqpt
from networkapi.api_pools.facade.v3.base import get_pool_by_id
from networkapi.api_pools.facade.v3.base import reserve_name_healthcheck
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_vip_request import exceptions
from networkapi.api_vip_request import syncs
from networkapi.api_vip_request.models import VipRequest
from networkapi.api_vip_request.models import VipRequestDSCP
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.plugins.factory import PluginFactory
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import ServerPool
from networkapi.util import valid_expression
from networkapi.util.geral import get_app


# serializers
pool_slz = get_app('api_pools', module_label='serializers.v3')
vip_slz = get_app('api_vip_request', module_label='serializers.v3')


log = logging.getLogger(__name__)


def get_vip_request_by_ip(ipv4=None, ipv6=None, environment_vip=None):
    """
    Get Vip Request by Ipv4, Ipv6, Environment Vip

    :param ip: Id of Ipv4
    :param ipv6: Id of Ipv6
    :param environment_vip: Id of Environment Vip
    """
    vip_request = VipRequest.objects.all()

    if environment_vip:
        vip_request = vip_request.filter(environmentvip=environment_vip)

    if ipv4 is not None:
        vip_request = vip_request.filter(ipv4=ipv4)

    if ipv6 is not None:
        vip_request = vip_request.filter(ipv6=ipv6)

    return vip_request


def get_vip_request_by_id(vip_request_id):
    """Get one Vip Request"""

    try:
        vip_request = VipRequest.objects.get(id=vip_request_id)
    except ObjectDoesNotExist:
        raise exceptions.VipRequestDoesNotExistException()

    return vip_request


def get_vip_request_by_ids(vip_request_ids):
    """Get many Vip Request"""

    vps_ids = list()
    for vip_request_id in vip_request_ids:
        try:
            sp = get_vip_request_by_id(vip_request_id).id
            vps_ids.append(sp)
        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e)
        except exceptions.VipRequestDoesNotExistException, e:
            raise ObjectDoesNotExistException(e)
        except Exception, e:
            raise NetworkAPIException(e)

    vip_requests = VipRequest.objects.filter(id__in=vps_ids)

    return vip_requests


def create_vip_request(vip_request, user):
    """Create Vip Request."""

    try:
        vip = VipRequest()
        vip.create_v3(vip_request, user)
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(e)
    else:
        return vip


def update_vip_request(vip_request, user, permit_created=False):
    """Update Vip Request."""

    try:
        vip = get_vip_request_by_id(vip_request.get('id'))
        vip.update_v3(vip_request, user, permit_created)
    except exceptions.VipRequestDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except ValidationAPIException, e:
        raise ValidationAPIException(e)
    except Exception, e:
        raise NetworkAPIException(e)
    else:
        return vip


def delete_vip_request(vip_request_ids, keep_ip='0'):
    """Delete vip request."""

    for vip_request_id in vip_request_ids:
        try:
            vip = get_vip_request_by_id(vip_request_id)
            bypass_ip = True if keep_ip == '1' else False
            vip.delete_v3(bypass_ipv4=bypass_ip, bypass_ipv6=bypass_ip)
        except exceptions.VipRequestDoesNotExistException, e:
            raise ObjectDoesNotExistException(e.detail)
        except exceptions.VipConstraintCreated, e:
            raise ValidationAPIException(e)
        except ValidationAPIException, e:
            raise ValidationAPIException(e)
        except Exception, e:
            raise NetworkAPIException(e)
        else:
            return vip


def get_vip_request_by_search(search=dict()):

    try:
        vip_requests = VipRequest.objects.filter()
        vip_map = build_query_to_datatable_v3(vip_requests, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return vip_map


def prepare_apply(load_balance, vip, created=True, user=None):

    vip_request = copy.deepcopy(vip)

    id_vip = str(vip_request.get('id'))

    equips, conf, cluster_unit = _validate_vip_to_apply(
        vip_request, created, user)

    cache_group = OptionVip.objects.get(
        id=vip_request.get('options').get('cache_group'))
    traffic_return = OptionVip.objects.get(
        id=vip_request.get('options').get('traffic_return'))
    timeout = OptionVip.objects.get(
        id=vip_request.get('options').get('timeout'))
    persistence = OptionVip.objects.get(
        id=vip_request.get('options').get('persistence'))

    if vip_request['ipv4']:
        ipv4 = Ip.get_by_pk(vip_request['ipv4']) if vip_request[
            'ipv4'] else None
        vip_request['ipv4'] = {
            'id': ipv4.id,
            'ip_formated': ipv4.ip_formated
        }

    if vip_request['ipv6']:
        ipv6 = Ipv6.get_by_pk(vip_request['ipv6']) if vip_request[
            'ipv6'] else None
        vip_request['ipv6'] = {
            'id': ipv6.id,
            'ip_formated': ipv6.ip_formated
        }

    if conf:
        conf = json.loads(conf)

    vip_request['options'] = dict()
    vip_request['options']['cache_group'] = {
        'id': cache_group.id,
        'nome_opcao_txt': cache_group.nome_opcao_txt
    }
    vip_request['options']['traffic_return'] = {
        'id': traffic_return.id,
        'nome_opcao_txt': traffic_return.nome_opcao_txt
    }
    vip_request['options']['timeout'] = {
        'id': timeout.id,
        'nome_opcao_txt': timeout.nome_opcao_txt
    }
    vip_request['options']['persistence'] = {
        'id': persistence.id,
        'nome_opcao_txt': persistence.nome_opcao_txt
    }
    vip_request['options']['cluster_unit'] = cluster_unit

    try:
        vip_request['options']['dscp'] = VipRequestDSCP.objects.get(
            vip_request=vip_request['id']
        ).dscp
    except:
        vip_request['options']['dscp'] = None
        pass

    for idx, port in enumerate(vip_request['ports']):
        for i, pl in enumerate(port['pools']):

            pool = get_pool_by_id(pl['server_pool'])
            pool_serializer = pool_slz.PoolV3Serializer(pool)

            l7_rule = OptionVip.objects.get(
                id=pl['l7_rule']).nome_opcao_txt

            healthcheck = pool_serializer.data['healthcheck']
            healthcheck['identifier'] = reserve_name_healthcheck(
                pool_serializer.data['identifier'])
            healthcheck['new'] = True
            vip_request['ports'][idx]['pools'][i]['server_pool'] = {
                'id': pool_serializer.data['id'],
                'nome': pool_serializer.data['identifier'],
                'lb_method': pool_serializer.data['lb_method'],
                'healthcheck': healthcheck,
                'action': pool_serializer.data['servicedownaction']['name'],
                'pool_created': pool_serializer.data['pool_created'],
                'pools_members': [{
                    'id': pool_member['id'],
                    'identifier': pool_member['identifier'],
                    'ip': pool_member['ip']['ip_formated'] if pool_member['ip'] else pool_member['ipv6']['ip_formated'],
                    'port': pool_member['port_real'],
                    'member_status': pool_member['member_status'],
                    'limit': pool_member['limit'],
                    'priority': pool_member['priority'],
                    'weight': pool_member['weight']
                } for pool_member in pool_serializer.data['server_pool_members']]
            }

            vip_request['ports'][idx]['pools'][i]['l7_rule'] = l7_rule
        l7_protocol = OptionVip.objects.get(
            id=port['options']['l7_protocol'])
        l4_protocol = OptionVip.objects.get(
            id=port['options']['l4_protocol'])

        vip_request['ports'][idx]['options'] = dict()
        vip_request['ports'][idx]['options']['l7_protocol'] = {
            'id': l7_protocol.id,
            'nome_opcao_txt': l7_protocol.nome_opcao_txt
        }
        vip_request['ports'][idx]['options']['l4_protocol'] = {
            'id': l4_protocol.id,
            'nome_opcao_txt': l4_protocol.nome_opcao_txt
        }

    vip_request['conf'] = conf

    if conf:
        for idx, layer in enumerate(conf['conf']['layers']):
            requiments = layer.get('requiments')
            if requiments:
                # validate for port
                for idx_port, port in enumerate(vip['ports']):
                    for requiment in requiments:
                        condicionals = requiment.get('condicionals')
                        for condicional in condicionals:

                            validated = True

                            validations = condicional.get('validations')
                            for validation in validations:
                                if validation.get('type') == 'optionvip':
                                    validated &= valid_expression(
                                        validation.get('operator'),
                                        int(vip['options'][
                                            validation.get('variable')]),
                                        int(validation.get('value'))
                                    )

                                if validation.get('type') == 'portoptionvip':
                                    validated &= valid_expression(
                                        validation.get('operator'),
                                        int(port['options'][
                                            validation.get('variable')]),
                                        int(validation.get('value'))
                                    )

                                if validation.get('type') == 'field' and validation.get('variable') == 'cluster_unit':
                                    validated &= valid_expression(
                                        validation.get('operator'),
                                        cluster_unit,
                                        validation.get('value')
                                    )
                            if validated:
                                use = condicional.get('use')
                                for item in use:
                                    definitions = item.get('definitions')
                                    eqpts = item.get('eqpts')
                                    if eqpts:

                                        eqpts = Equipamento.objects.filter(
                                            id__in=eqpts,
                                            maintenance=0,
                                            tipo_equipamento__tipo_equipamento=u'Balanceador').distinct()

                                        if facade_eqpt.all_equipments_are_in_maintenance(equips):
                                            raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

                                        if user:
                                            if not facade_eqpt.all_equipments_can_update_config(equips, user):
                                                raise exceptions_eqpt.UserDoesNotHavePermInAllEqptException(
                                                    'User does not have permission to update conf in eqpt. \
                                                    Verify the permissions of user group with equipment group. Vip:{}'.format(
                                                        vip_request['id']))

                                        for eqpt in eqpts:
                                            eqpt_id = str(eqpt.id)

                                            if not load_balance.get(eqpt_id):
                                                equipment_access = EquipamentoAcesso.search(
                                                    equipamento=eqpt.id
                                                )

                                                plugin = PluginFactory.factory(
                                                    eqpt)

                                                load_balance[eqpt_id] = {
                                                    'plugin': plugin,
                                                    'access': equipment_access,
                                                    'vips': [],
                                                    'layers': {},
                                                }

                                            idx_layer = str(idx)
                                            idx_port_str = str(
                                                port['port'])
                                            if not load_balance[eqpt_id]['layers'].get(id_vip):
                                                load_balance[eqpt_id][
                                                    'layers'][id_vip] = dict()

                                            if load_balance[eqpt_id]['layers'][id_vip].get(idx_layer):
                                                if load_balance[eqpt_id]['layers'][id_vip].get(idx_layer).get('definitions').get(idx_port_str):
                                                    load_balance[eqpt_id]['layers'][id_vip][idx_layer][
                                                        'definitions'][idx_port_str] += definitions
                                                else:
                                                    load_balance[eqpt_id]['layers'][id_vip][idx_layer][
                                                        'definitions'][idx_port_str] = definitions
                                            else:
                                                load_balance[eqpt_id]['layers'][id_vip][idx_layer] = {
                                                    'vip_request': vip_request,
                                                    'definitions': {
                                                        idx_port_str: definitions
                                                    }
                                                }

    for e in equips:
        eqpt_id = str(e.id)

        if not load_balance.get(eqpt_id):

            equipment_access = EquipamentoAcesso.search(
                equipamento=e.id
            )

            plugin = PluginFactory.factory(e)

            load_balance[eqpt_id] = {
                'plugin': plugin,
                'access': equipment_access,
                'vips': [],
                'layers': {},
            }

        load_balance[eqpt_id]['vips'].append({'vip_request': vip_request})

    return load_balance


@commit_on_success
def create_real_vip_request(vip_requests, user):

    load_balance = dict()
    keys = list()

    for vip in vip_requests:
        load_balance = prepare_apply(
            load_balance, vip, created=False, user=user)

        keys.append(sorted([str(key) for key in load_balance.keys()]))

    # vips are in differents load balancers
    keys = [','.join(key) for key in keys]
    if len(list(set(keys))) > 1:
        raise Exception('Vips Request are in differents load balancers')

    for lb in load_balance:
        inst = copy.deepcopy(load_balance.get(lb))
        log.info('started call:%s' % lb)
        inst.get('plugin').create_vip(inst)
        log.info('ended call')

    ids = [vip_id.get('id') for vip_id in vip_requests]

    vips = VipRequest.objects.filter(id__in=ids)
    vips.update(created=True)

    for vip in vips:
        syncs.new_to_old(vip)

    ServerPool.objects.filter(
        viprequestportpool__vip_request_port__vip_request__id__in=ids).update(pool_created=True)


@commit_on_success
def update_real_vip_request(vip_requests, user):

    load_balance = dict()
    keys = list()
    for vip in vip_requests:

        # old VIP
        vip_old = VipRequest.get_by_pk(vip.get('id'))
        serializer_vips = vip_slz.VipRequestV3Serializer(
            vip_old,
            many=False,
            include=('ports__identifier',)
        )
        slz_vips_old = copy.deepcopy(serializer_vips.data)

        # Save
        update_vip_request(vip, user, permit_created=True)

        # new VIP
        vip_new = VipRequest.get_by_pk(vip.get('id'))
        serializer_vips = vip_slz.VipRequestV3Serializer(
            vip_new,
            many=False,
            include=('ports__identifier',)
        )
        vip_request = copy.deepcopy(serializer_vips.data)

        # Ids of ports of old vip
        ids_port_old = [port.get('id')
                        for port in slz_vips_old.get('ports')]

        # Ids of ports of new vip
        ids_port_upt = [port.get('id')
                        for port in vip_request.get('ports')]

        # Ids of ports to delete
        ids_port_to_del = list(set(ids_port_old) - set(ids_port_upt))

        # Ports to change or insert
        for idx_port, port in enumerate(vip_request.get('ports')):

            # Port changed
            if port.get('id') in ids_port_old:

                # Get old port
                idx_old_port = ids_port_old.index(port.get('id'))
                old_port = slz_vips_old.get('ports')[idx_old_port]

                # Ids of old pools
                ids_old_pool = [pool.get('id')
                                for pool in old_port.get('pools')]

                # Ids of new pools
                ids_upt_pool = [pool.get('id') for pool in port.get('pools')]

                # Ids of pools to delete
                ids_pool_to_del = list(set(ids_old_pool) - set(ids_upt_pool))

                # Ids of pools to insert
                ids_pool_to_ins = list(set(ids_upt_pool) - set(ids_old_pool))

                # Ids of pools with same ids
                ids_pool_equal = list(set(ids_upt_pool) & set(ids_old_pool))

                # Pools to insert in port
                for id_pool in ids_pool_to_ins:
                    idx_pool = ids_upt_pool.index(id_pool)
                    vip_request['ports'][idx_port][
                        'pools'][idx_pool]['insert'] = True

                # Pools to delete in port
                for id_pool in ids_pool_to_del:

                    # Indexs pool to delete
                    idx_pool_del = ids_old_pool.index(id_pool)

                    # Pool to delete
                    pool_del = copy\
                        .deepcopy(old_port.get('pools')[idx_pool_del])
                    pool_del['delete'] = True

                    # Addes pool in list pools of port
                    vip_request['ports'][idx_port]['pools'].append(pool_del)

                # pools to delete in port when id of internal controle was not
                # changed.
                # Example: OLD - Id: 1, Server_pool: 12, ..
                #          NEW - Id: 1, Server_pool: 13, ..
                for id_pool in ids_pool_equal:

                    idx_pool_old = ids_old_pool.index(id_pool)
                    idx_pool_cur = ids_upt_pool.index(id_pool)

                    # server_pool was changed
                    if old_port.get('pools')[idx_pool_old]['server_pool'] != \
                            port.get('pools')[idx_pool_cur]['server_pool']:
                        # pool to delete
                        pool_del = copy\
                            .deepcopy(old_port.get('pools')[idx_pool_old])
                        pool_del['delete'] = True
                        vip_request['ports'][idx_port]['pools']\
                            .append(pool_del)

            # New port
            else:
                vip_request['ports'][idx_port]['insert'] = True

        # Ports to delete
        for id_port in ids_port_to_del:
            # idx pool to delete
            idx_port_del = ids_port_old.index(id_port)

            # Port to delete
            port_del = copy.deepcopy(slz_vips_old.get('ports')[idx_port_del])
            port_del['delete'] = True
            vip_request['ports'].append(port_del)

        load_balance = prepare_apply(load_balance, vip_request,
                                     created=True, user=user)

        keys.append(sorted([str(key) for key in load_balance.keys()]))

    # vips are in differents load balancers
    keys = [','.join(key) for key in keys]
    if len(list(set(keys))) > 1:
        raise Exception('Vips Request are in differents load balancers')

    pools_ids_ins = list()
    pools_ids_del = list()

    for lb in load_balance:
        inst = copy.deepcopy(load_balance.get(lb))
        log.info('started call:%s' % lb)
        pool_ins, pool_del = inst.get('plugin').update_vip(inst)
        log.info('ended call')
        pools_ids_ins += pool_ins
        pools_ids_del += pool_del

    if pools_ids_ins:
        pools_ids_ins = list(set(pools_ids_ins))
        ServerPool.objects.filter(
            id__in=pools_ids_ins).update(pool_created=True)

    if pools_ids_del:
        pools_ids_del = list(set(pools_ids_del))
        ServerPool.objects.filter(
            id__in=pools_ids_del).update(pool_created=False)


@commit_on_success
def patch_real_vip_request(vip_requests, user):

    load_balance = dict()
    keys = list()
    for vip in vip_requests:

        vip_old = VipRequest.get_by_pk(vip.get('id'))
        serializer_vips = vip_slz.VipRequestV3Serializer(
            vip_old,
            many=False,
            include=('ports__identifier',)
        )

        vip_dict = serializer_vips.data

        # validate and save
        vip_dict['options']['persistence'] = vip['options']['persistence']

        update_vip_request(vip_dict, user, permit_created=True)

        load_balance = prepare_apply(
            load_balance, vip_dict, created=True, user=user)

        keys.append(sorted([str(key) for key in load_balance.keys()]))

    # vips are in differents load balancers
    keys = [','.join(key) for key in keys]
    if len(list(set(keys))) > 1:
        raise Exception('Vips Request are in differents load balancers')

    for lb in load_balance:
        inst = copy.deepcopy(load_balance.get(lb))
        log.info('started call:%s' % lb)
        inst.get('plugin').partial_update_vip(inst)
        log.info('ended call')


@commit_on_success
def delete_real_vip_request(vip_requests, user):
    load_balance = dict()

    keys = list()
    for vip in vip_requests:
        load_balance = prepare_apply(
            load_balance, vip, created=True, user=user)

        keys.append(sorted([str(key) for key in load_balance.keys()]))

    # vips are in differents load balancers
    keys = [','.join(key) for key in keys]
    if len(list(set(keys))) > 1:
        raise Exception('Vips Request are in differents load balancers')

    pools_ids = list()

    for lb in load_balance:
        inst = copy.deepcopy(load_balance.get(lb))
        log.info('started call:%s' % lb)
        pool_del = inst.get('plugin').delete_vip(inst)
        log.info('ended call')
        pools_ids += pool_del

    ids = [vip_id.get('id') for vip_id in vip_requests]

    vips = VipRequest.objects.filter(id__in=ids)
    vips.update(created=False)

    for vip in vips:
        syncs.new_to_old(vip)

    if pools_ids:
        pools_ids = list(set(pools_ids))
        ServerPool.objects.filter(id__in=pools_ids).update(pool_created=False)


def _validate_vip_to_apply(vip_request, update=False, user=None):

    vip = get_vip_request_by_id(vip_request.get('id'))

    # validate vip with same ipv4 ou ipv6
    vip_with_ip = get_vip_request_by_ip(vip.ipv4, vip.ipv6, vip.environmentvip)
    vip_with_ip = vip_with_ip.exclude(
        id=vip.id
    ).exclude(
        created=False
    ).distinct()

    if vip_with_ip.count() > 0:
        raise exceptions.AlreadyVipRequestException()

    if update and not vip.created:
        raise exceptions.VipRequestNotCreated(vip.id)

    if not update and vip.created:
        raise exceptions.VipRequestAlreadyCreated(vip.id)

    equips = facade_eqpt.get_eqpt_by_envvip(vip_request['environmentvip'])

    conf = EnvironmentVip.objects.get(id=vip_request['environmentvip']).conf

    if facade_eqpt.all_equipments_are_in_maintenance(equips):
        raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

    if user:
        if not facade_eqpt.all_equipments_can_update_config(equips, user):
            raise exceptions_eqpt.UserDoesNotHavePermInAllEqptException(
                'User does not have permission to update conf in eqpt. \
                Verify the permissions of user group with equipment group. Vip:{}'.format(
                    vip_request['id']))

    cluster_unit = vip.ipv4.networkipv4.cluster_unit if vip.ipv4 else vip.ipv6.networkipv6.cluster_unit

    return equips, conf, cluster_unit
