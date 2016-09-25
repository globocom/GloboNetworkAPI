# -*- coding:utf-8 -*-
import copy
import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.transaction import commit_on_success

from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_equipment import exceptions as exceptions_eqpt
from networkapi.api_equipment import facade as facade_eqpt
from networkapi.api_pools import exceptions as exceptions_pool
from networkapi.api_pools.facade.v3.base import get_pool_by_id
from networkapi.api_pools.facade.v3.base import reserve_name_healthcheck
from networkapi.api_pools.serializers import PoolV3Serializer
from networkapi.api_usuario import facade as facade_usr
from networkapi.api_vip_request import exceptions
from networkapi.api_vip_request import models
from networkapi.api_vip_request import syncs
from networkapi.api_vip_request.serializers import VipRequestSerializer
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.plugins.factory import PluginFactory
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.usuario.models import UsuarioGrupo
from networkapi.util import valid_expression


log = logging.getLogger(__name__)


def get_vip_request_by_ip(ipv4=None, ipv6=None, environment_vip=None):
    """
    Get Vip Request by Ipv4, Ipv6, Environment Vip

    :param ip: Id of Ipv4
    :param ipv6: Id of Ipv6
    :param environment_vip: Id of Environment Vip
    """
    vip_request = models.VipRequest.objects.all()

    if environment_vip:
        vip_request = vip_request.filter(environmentvip=environment_vip)

    if ipv4 is not None:
        vip_request = vip_request.filter(ipv4=ipv4)

    if ipv6 is not None:
        vip_request = vip_request.filter(ipv6=ipv6)

    return vip_request


def get_vip_request_by_id(vip_request_id):
    """
    get Vip Request
    """
    try:
        vip_request = models.VipRequest.objects.get(id=vip_request_id)
    except ObjectDoesNotExist:
        raise exceptions.VipRequestDoesNotExistException()

    return vip_request


def get_vip_request_by_ids(vip_request_ids):
    """
    get Vip Request
    """
    vip_requests = list()
    for vip_request_id in vip_request_ids:
        vip_requests.append(get_vip_request_by_id(vip_request_id))

    return vip_requests


def create_vip_request(vip_request, user):
    """
    Create Vip Request
    """
    # Remove when RequisicaoVips is die
    req = RequisicaoVips()
    req.save()

    vip = models.VipRequest()
    vip.id = req.id
    vip.name = vip_request['name']
    vip.service = vip_request['service']
    vip.business = vip_request['business']
    vip.environmentvip_id = vip_request['environmentvip']
    vip.ipv4 = Ip.get_by_pk(vip_request['ipv4']) if vip_request[
        'ipv4'] else None
    vip.ipv6 = Ipv6.get_by_pk(vip_request['ipv6']) if vip_request[
        'ipv6'] else None

    option_create = [vip_request['options'][key]
                     for key in vip_request['options']]
    vip.save()

    _create_port(vip_request['ports'], vip.id)
    _create_option(option_create, vip.id)

    # perms
    groups_perm = vip_request.get('groups_permissions', [])
    groups_perm += facade_usr.get_groups(vip_request.get('users_permissions', []))
    groups = facade_usr.reduce_groups(groups_perm)
    create_groups_permissions(groups, vip.id, user)

    # sync with old tables
    syncs.new_to_old(vip)

    return vip


def update_vip_request(vip_request, user):
    """
    update Vip Request
    """

    vip = models.VipRequest.get_by_pk(vip_request['id'])

    vip.name = vip_request['name']
    vip.service = vip_request['service']
    vip.business = vip_request['business']
    vip.environmentvip_id = vip_request['environmentvip']
    vip.ipv4 = Ip.get_by_pk(vip_request['ipv4']) if vip_request[
        'ipv4'] else None
    vip.ipv6 = Ipv6.get_by_pk(vip_request['ipv6']) if vip_request[
        'ipv6'] else None

    option_ids = [int(option.optionvip.id)
                  for option in vip.viprequestoptionvip_set.all()]
    options = [int(vip_request['options'][key])
               for key in vip_request['options']]
    option_remove = list(set(option_ids) - set(options))
    option_create = list(set(options) - set(option_ids))

    vip.save()

    _update_port(vip_request['ports'], vip.id)

    _create_option(option_create, vip.id)
    _delete_option(option_remove, vip.id)

    dsrl3 = OptionVip.objects.filter(
        nome_opcao_txt='DSRL3', tipo_opcao='Retorno de trafego').values('id')
    if dsrl3:
        if dsrl3[0]['id'] in option_remove:
            models.VipRequestDSCP.objects.filter(vip_request=vip.id).delete()

    # perms
    groups_perm = vip_request.get('groups_permissions', [])
    groups_perm += facade_usr.get_groups(vip_request.get('users_permissions', []))
    groups = facade_usr.reduce_groups(groups_perm)

    perm = vip_request.get('permissions')
    perm_replace = perm.get('replace') if perm else False

    update_groups_permissions(groups, vip.id, user, perm_replace)

    # sync with old tables
    syncs.new_to_old(vip)


def delete_vip_request(vip_request_ids, keep_ip='0'):
    """delete vip request"""

    ipv4_list = list()
    ipv6_list = list()
    for vip_request_id in vip_request_ids:
        vp = models.VipRequest.get_by_pk(vip_request_id)
        if vp.ipv4 and keep_ip == '0':
            if not _is_ipv4_in_use(vp.ipv4, vip_request_id):
                ipv4_list.append(vp.ipv4.id)
        if vp.ipv6 and keep_ip == '0':
            if not _is_ipv6_in_use(vp.ipv6, vip_request_id):
                ipv6_list.append(vp.ipv6.id)

        if vp.created:
            raise exceptions.VipConstraintCreatedException(vip_request_id)

        vp.delete()

    # sync with old tables
    syncs.delete_old(vip_request_ids)

    ipv4_list = list(set(ipv4_list))
    ipv6_list = list(set(ipv6_list))
    return ipv4_list, ipv6_list


def _is_ipv4_in_use(ipv4, vip_id):

    is_in_use = True
    pool_member_count = ServerPoolMember.objects.filter(ip=ipv4).exclude(
        server_pool__vipporttopool__requisicao_vip__id=vip_id).count()
    vip_count = models.VipRequest.objects.filter(
        ipv4=ipv4).exclude(pk=vip_id).count()
    if vip_count == 0 and pool_member_count == 0:
        is_in_use = False

    return is_in_use


def _is_ipv6_in_use(ipv6, vip_id):

    is_in_use = True
    pool_member_count = ServerPoolMember.objects.filter(ipv6=ipv6).exclude(
        server_pool__vipporttopool__requisicao_vip__ipv6=vip_id).count()
    vip_count = models.VipRequest.objects.filter(
        ipv6=ipv6).exclude(pk=vip_id).count()
    if vip_count == 0 and pool_member_count == 0:
        is_in_use = False

    return is_in_use


def _create_port(ports, vip_request_id):
    """Create ports"""

    for port in ports:
        # save port
        pt = models.VipRequestPort()
        pt.vip_request_id = vip_request_id
        pt.port = port['port']
        pt.save()

        # save port option l7_protocol
        opt = models.VipRequestPortOptionVip()
        opt.vip_request_port_id = pt.id
        opt.optionvip_id = port['options']['l4_protocol']
        opt.save()

        # save port option l7_protocol
        opt = models.VipRequestPortOptionVip()
        opt.vip_request_port_id = pt.id
        opt.optionvip_id = port['options']['l7_protocol']
        opt.save()

        # save pool by port
        for pool in port.get('pools'):
            pl = models.VipRequestPortPool()
            pl.vip_request_port_id = pt.id
            pl.server_pool_id = pool.get('server_pool')
            pl.optionvip_id = pool.get('l7_rule')
            pl.val_optionvip = pool.get('l7_value')
            pl.order = pool.get('order')
            pl.save()


def _update_port(ports, vip_request_id):
    """Update ports"""

    for port in ports:
        # save port
        try:
            pt = models.VipRequestPort.objects.get(
                vip_request_id=vip_request_id,
                port=port['port'])
        except:
            pt = models.VipRequestPort()
            pt.vip_request_id = vip_request_id
            pt.port = port['port']
            pt.save()

        # save port option l4_protocol
        try:
            opt = models.VipRequestPortOptionVip.objects.get(
                vip_request_port_id=pt.id,
                optionvip_id=port['options']['l4_protocol'])
        except:
            opt = models.VipRequestPortOptionVip()
            opt.vip_request_port_id = pt.id
            opt.optionvip_id = port['options']['l4_protocol']
            opt.save()

        # save port option l7_protocol
        try:
            opt = models.VipRequestPortOptionVip.objects.get(
                vip_request_port_id=pt.id,
                optionvip_id=port.get('options').get('l7_protocol'))
        except:
            opt = models.VipRequestPortOptionVip()
            opt.vip_request_port_id = pt.id
            opt.optionvip_id = port.get('options').get('l7_protocol')
            opt.save()

        # delete option by port
        models.VipRequestPortOptionVip.objects.filter(
            vip_request_port_id=pt.id
        ).exclude(
            optionvip_id__in=[
                port.get('options').get('l4_protocol'),
                port.get('options').get('l7_protocol')]
        ).delete()

        # save pool by port
        pools = list()
        for pool in port.get('pools'):
            try:
                pl = models.VipRequestPortPool.objects.get(
                    vip_request_port=pt.id,
                    id=pool.get('id'))
            except:
                pl = models.VipRequestPortPool()
                pl.vip_request_port_id = pt.id
                pl.server_pool_id = pool.get('server_pool')
            finally:
                if pl.optionvip_id != pool.get('l7_rule') or \
                        pl.val_optionvip != pool.get('l7_value') or \
                        pl.order != pool.get('order') or \
                        pl.server_pool_id != pool.get('server_pool'):
                    pl.optionvip_id = pool.get('l7_rule')
                    pl.val_optionvip = pool.get('l7_value')
                    pl.order = pool.get('order')
                    pl.save()
            pools.append(pl.id)

            pools.append(pl.id)

        # delete pool by port
        models.VipRequestPortPool.objects.filter(
            vip_request_port=pt
        ).exclude(
            id__in=pools
        ).delete()

    # delete port
    ports_ids = [port.get('port') for port in ports]
    models.VipRequestPort.objects.filter(
        vip_request_id=vip_request_id
    ).exclude(
        port__in=ports_ids
    ).delete()


def _create_option(options, vip_request_id):
    """create options"""

    for option in options:
        opt = models.VipRequestOptionVip()
        opt.vip_request_id = vip_request_id
        opt.optionvip_id = option
        opt.save()

    dsrl3 = OptionVip.objects.filter(
        nome_opcao_txt='DSRL3',
        tipo_opcao='Retorno de trafego'
    ).values('id')
    if dsrl3:
        if dsrl3[0]['id'] in options:
            dscp = _dscp(vip_request_id)
            vip_dscp = models.VipRequestDSCP()
            vip_dscp.vip_request_id = vip_request_id
            vip_dscp.dscp = dscp
            vip_dscp.save()


def _delete_option(options, vip_request_id):
    """Deletes options"""
    models.VipRequestOptionVip.objects.filter(
        vip_request=vip_request_id,
        optionvip__in=options
    ).delete()


def get_vip_request_by_search(search=dict()):

    vip_requests = models.VipRequest.objects.filter()

    vip_map = build_query_to_datatable_v3(vip_requests, search)

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
        vip_request['options']['dscp'] = models.VipRequestDSCP.objects.get(
            vip_request=vip_request['id']
        ).dscp
    except:
        vip_request['options']['dscp'] = None
        pass

    for idx, port in enumerate(vip_request['ports']):
        for i, pl in enumerate(port['pools']):

            pool = get_pool_by_id(pl['server_pool'])
            pool_serializer = PoolV3Serializer(pool)

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

    vips = models.VipRequest.objects.filter(id__in=ids)
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

        vip_request = copy.deepcopy(vip)

        vip_old = models.VipRequest.get_by_pk(vip.get('id'))
        serializer_vips = VipRequestSerializer(
            vip_old,
            many=False
        )
        serializer_vips_data = copy.deepcopy(serializer_vips.data)

        validate_save(vip, True)
        update_vip_request(vip, user)

        ids_port_old = [port.get('id') for port in serializer_vips_data.get('ports')]
        ids_port_upt = [port.get('id') for port in vip_request.get('ports') if port.get('id')]
        ids_port_to_del = list(set(ids_port_old) - set(ids_port_upt))

        # ports to change and insert
        for idx_port, port in enumerate(vip_request.get('ports')):
            # change port
            if port.get('id'):

                # idx port old
                idx_port_old = ids_port_old.index(port.get('id'))
                # port old
                port_old = serializer_vips_data.get('ports')[idx_port_old]
                # ids pools old
                ids_pool_old = [pool.get('id') for pool in port_old.get('pools')]

                # ids pools changed
                ids_pool_cur = [pool.get('id') for pool in port.get('pools') if pool.get('id')]

                # ids to delete
                ids_pool_to_del = list(set(ids_pool_old) - set(ids_pool_cur))

                # pools to delete in port
                for id_pool in ids_pool_to_del:
                    # idx pool to delete
                    idx_pool_del = ids_pool_old.index(id_pool)

                    # pool to delete
                    pool_del = copy.deepcopy(port_old.get('pools')[idx_pool_del])
                    pool_del['delete'] = True
                    vip_request['ports'][idx_port]['pools'].append(pool_del)

        # ports to delete
        for id_port in ids_port_to_del:
            # idx pool to delete
            idx_port_del = ids_port_old.index(id_port)

            # port to delete
            port_del = copy.deepcopy(serializer_vips_data.get('ports')[idx_port_del])
            port_del['delete'] = True
            vip_request['ports'].append(port_del)

        load_balance = prepare_apply(
            load_balance, vip_request, created=True, user=user)

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
        ServerPool.objects.filter(id__in=pools_ids_ins).update(pool_created=True)

    if pools_ids_del:
        pools_ids_del = list(set(pools_ids_del))
        ServerPool.objects.filter(id__in=pools_ids_del).update(pool_created=False)


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

    vips = models.VipRequest.objects.filter(id__in=ids)
    vips.update(created=False)

    for vip in vips:
        syncs.new_to_old(vip)

    if pools_ids:
        pools_ids = list(set(pools_ids))
        ServerPool.objects.filter(id__in=pools_ids).update(pool_created=False)


#############
# helpers
#############
def create_lock(vip_requests):
    """
    Create locks to vips list
    """
    locks_list = list()
    for vip_request in vip_requests:
        if isinstance(vip_request, dict):
            lock = distributedlock(LOCK_VIP % vip_request['id'])
        else:
            lock = distributedlock(LOCK_VIP % vip_request)
        lock.__enter__()
        locks_list.append(lock)

    return locks_list


def destroy_lock(locks_list):
    """
    Destroy locks by vips list
    """
    for lock in locks_list:
        lock.__exit__('', '', '')


def validate_save(vip_request, permit_created=False):

    has_identifier = models.VipRequest.objects.filter(
        environmentvip=vip_request['environmentvip']
    )

    # validate ipv4
    if vip_request['ipv4']:
        has_identifier = has_identifier.filter(ipv4=vip_request['ipv4'])

        vips = EnvironmentVip.objects.filter(
            networkipv4__ip=vip_request['ipv4']
        ).filter(
            id=vip_request['environmentvip']
        )
        if not vips:
            raise exceptions.IpNotFoundByEnvironment(vip_request['name'])

    # validate ipv6
    if vip_request['ipv6']:
        has_identifier = has_identifier.filter(ipv6=vip_request['ipv6'])
        vips = EnvironmentVip.objects.filter(
            networkipv6__ipv6=vip_request['ipv6']
        ).filter(
            id=vip_request['environmentvip']
        )
        if not vips:
            raise exceptions.IpNotFoundByEnvironment(vip_request['name'])

    # validate change info when vip created
    if vip_request.get('id'):
        vip = models.VipRequest.get_by_pk(vip_request.get('id'))
        if vip.created:
            if not permit_created:
                raise exceptions.CreatedVipRequestValuesException()

            if vip.environmentvip_id != vip_request['environmentvip']:
                raise exceptions.CreatedVipRequestValuesException(
                    'Environment vip of vip request id: %s' % (vip_request.get('id')))

            # cannot change ip
            if vip.ipv4:
                if vip.ipv4.id != vip_request['ipv4']:
                    raise exceptions.CreatedVipRequestValuesException(
                        'Ipv4 of vip request id: %s' % (vip_request.get('id')))
            if vip.ipv6:
                if vip.ipv6.id != vip_request['ipv6']:
                    raise exceptions.CreatedVipRequestValuesException(
                        'Ipv6 of vip request id: %s' % (vip_request.get('id')))

            # change traffic return
            options = [op.optionvip.id for op in vip.viprequestoptionvip_set.all()]
            if vip_request['options']['traffic_return'] not in options:
                raise exceptions.CreatedVipRequestValuesException(
                    'Traffic Return of vip request id: %s' % (vip_request.get('id')))

            for port in vip_request.get('ports'):
                if port.get('id'):
                    # cannot change options of port

                    port_obj = vip.viprequestport_set.get(id=port.get('id'))

                    options_obj_l4 = port_obj.viprequestportoptionvip_set.filter(
                        optionvip=port.get('options').get('l4_protocol'))
                    options_obj_l7 = port_obj.viprequestportoptionvip_set.filter(
                        optionvip=port.get('options').get('l7_protocol'))

                    if not options_obj_l4 or not options_obj_l7:
                        raise exceptions.CreatedVipRequestValuesException(
                            'Options of port %s of vip request id: %s' % (port['port'], vip_request.get('id')))

        has_identifier = has_identifier.exclude(id=vip_request.get('id'))

    # has_identifier = has_identifier.distinct()
    # if has_identifier.count() > 0:
    #     raise exceptions.AlreadyVipRequestException()

    # validate option vip assoc with environment vip
    opts = list()
    for option in vip_request['options']:
        opt = dict()
        if option == 'cache_group' and vip_request['options'].get(option) is not None:
            opt['id'] = vip_request['options'].get(option)
            opt['tipo_opcao'] = 'cache'
        elif option == 'persistence' and vip_request['options'].get(option) is not None:
            opt['id'] = vip_request['options'].get(option)
            opt['tipo_opcao'] = 'Persistencia'
        elif option == 'traffic_return' and vip_request['options'].get(option) is not None:
            opt['id'] = vip_request['options'].get(option)
            opt['tipo_opcao'] = 'Retorno de trafego'
        elif option == 'timeout' and vip_request['options'].get(option) is not None:
            opt['id'] = vip_request['options'].get(option)
            opt['tipo_opcao'] = 'timeout'
        if opt:
            opts.append(opt)

    for opt in opts:
        try:
            option = OptionVip.objects.get(
                Q(**opt),
                optionvipenvironmentvip__environment__id=vip_request[
                    'environmentvip']
            )
        except:
            raise Exception(
                'Invalid option %s:%s,viprequest:%s, \
                because environmentvip is not associated to options or not exists' % (
                    opt['tipo_opcao'], opt['id'], vip_request['name'])
            )

    # validate pools associates
    for port in vip_request.get('ports'):

        opts = list()
        for option in port['options']:
            opt = dict()
            if option == 'l4_protocol' and port['options'].get(option) is not None:
                opt['id'] = port['options'].get(option)
                opt['tipo_opcao'] = 'l4_protocol'
            elif option == 'l7_protocol' and port['options'].get(option) is not None:
                opt['id'] = port['options'].get(option)
                opt['tipo_opcao'] = 'l7_protocol'
            if opt:
                opts.append(opt)

        for opt in opts:
            try:
                option = OptionVip.objects.get(
                    Q(**opt),
                    optionvipenvironmentvip__environment__id=vip_request[
                        'environmentvip']
                )
            except:
                raise Exception(
                    u'Invalid option %s:%s,port:%s,viprequest:%s, \
                    because environmentvip is not associated to options or not exists' % (
                        opt['tipo_opcao'], opt['id'], port['port'], vip_request['name'])
                )

        dsrl3 = OptionVip.objects.filter(
            nome_opcao_txt='DSRL3',
            tipo_opcao='Retorno de trafego',
            id=vip_request['options']['traffic_return'],
        )

        # validate dsrl3: 1 pool by port
        if dsrl3 and len(port['pools']) > 1:
            raise Exception(
                u'Vip %s has DSRL3 and can not to have L7' % (vip_request['name'])
            )

        count_l7_opt = 0
        for pool in port['pools']:

            # validate option vip(l7_rule) assoc with environment vip
            try:
                l7_rule_opt = OptionVip.objects.get(
                    id=pool['l7_rule'],
                    tipo_opcao='l7_rule',
                    optionvipenvironmentvip__environment__id=vip_request[
                        'environmentvip']
                )
            except:
                raise Exception(
                    u'Invalid option l7_rule:%s,pool:%s,port:%s,viprequest:%s, \
                    because environmentvip is not associated to options or not exists' % (
                        pool['l7_rule'], pool['server_pool'], port['port'], vip_request['name'])
                )

            # control to validate l7_rule "default_vip" in one pool by port
            if l7_rule_opt.nome_opcao_txt == 'default_vip':
                count_l7_opt += 1

            # validate dsrl3: pool assoc only vip and no l7 rules
            if dsrl3:
                # Vip with dscp(dsrl3) cannot L7 rules
                if l7_rule_opt.nome_opcao_txt != 'default_vip':
                    raise Exception(
                        u'Option Vip of pool {} of Vip Request {} must be default_vip'.format(
                            pool['server_pool'], vip_request['name'])
                    )

                pool_assoc_vip = get_vip_request_by_pool(pool['server_pool'])
                if vip_request.get('id'):
                    pool_assoc_vip = pool_assoc_vip.exclude(id=vip_request.get('id'))

                if pool_assoc_vip:
                    raise Exception(
                        u'Pool {} must be associated to a only vip request, \
                        when vip request has dslr3 option'.format(
                            pool['server_pool']))

            try:
                sp = ServerPool.objects.get(id=pool['server_pool'])
            except Exception, e:
                log.error(e)
                raise exceptions_pool.PoolDoesNotExistException(
                    pool['server_pool'])

            # validate dsrl3: Pool must have same port of vip
            if dsrl3:
                if int(sp.default_port) != int(port['port']):
                    raise Exception(
                        u'Pool {} must have same port of vip {}'.format(
                            pool['server_pool'], vip_request['name'])
                    )

            spms = ServerPoolMember.objects.filter(
                server_pool=pool['server_pool'])
            for spm in spms:
                # validate dsrl3: Pool Members must have same port of vip
                if dsrl3:
                    if int(spm.port_real) != int(port['port']):
                        ip_mb = spm.ip if spm.ip else spm.ipv6
                        raise Exception(
                            u'Pool Member {} of Pool {} must have same port of vip {}'.format(
                                ip_mb, pool['server_pool'], vip_request['name'])
                        )

                if spm.ip:

                    vips = EnvironmentVip.objects.filter(
                        environmentenvironmentvip__environment__vlan__networkipv4__ip=spm.ip
                    ).filter(
                        id=vip_request['environmentvip']
                    )
                    if not vips:
                        raise exceptions.ServerPoolMemberDiffEnvironmentVipException(
                            spm.identifier)
                if spm.ipv6:

                    vips = EnvironmentVip.objects.filter(
                        environmentenvironmentvip__environment__vlan__networkipv6__ipv6=spm.ipv6
                    ).filter(
                        id=vip_request['environmentvip']
                    )
                    if not vips:
                        raise exceptions.ServerPoolMemberDiffEnvironmentVipException(
                            spm.identifier)

        if count_l7_opt < 1:
            raise Exception(
                u'Port {} of Vip Request {} must have one pool with l7_rule equal "default_vip"'.format(
                    port['port'], vip_request['name'])
            )

        if count_l7_opt > 1:
            raise Exception(
                u'Port {} of Vip Request {} must have only pool with l7_rule equal "default_vip"'.format(
                    port['port'], vip_request['name'])
            )


def _dscp(vip_request_id):
    members = ServerPoolMember.objects.filter(
        server_pool__viprequestportpool__vip_request_port__vip_request__id=vip_request_id)
    eqpts = [member.equipment.id for member in members]

    members = models.VipRequestDSCP.objects.filter(
        vip_request__viprequestport__viprequestportpool__server_pool__serverpoolmember__in=ServerPoolMember.objects.filter(
            ip__ipequipamento__equipamento__in=eqpts
        )
    ).distinct().values('dscp')

    mb = [i.get('dscp') for i in members]
    perm = range(3, 64)
    perm_new = list(set(perm) - set(mb))
    if perm_new:
        return perm_new[0]
    else:
        raise Exception(
            'Can\'t use pool because pool members have dscp is sold out')


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

    equips = Equipamento.objects.filter(
        equipamentoambiente__ambiente__vlan__networkipv4__ambient_vip__id=vip_request[
            'environmentvip'],
        maintenance=0,
        tipo_equipamento__tipo_equipamento=u'Balanceador').distinct()

    # does not implemented yet
    # equips = Equipamento.objects.filter(
    #     equipamentoambiente__ambiente__vlan__networkipv6__ambient_vip__id=vip_request['environmentvip'],
    #     maintenance=0,
    #     tipo_equipamento__tipo_equipamento=u'Balanceador').distinct()

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


# PERMS
def create_groups_permissions(groups_permissions, vip_id, user):
    """Creates permissions to access for vips"""

    group_adm = {
        'group': True,
        'read': True,
        'write': True,
        'delete': True,
        'change_config': True,
    }
    _create_group_permission(group_adm, vip_id)

    if groups_permissions:
        for group_permission in groups_permissions:
            if group_permission['group'] != 1:
                _create_group_permission(group_permission, vip_id)
    else:
        for group in UsuarioGrupo.list_by_user_id(user.id):
            group_id = int(group.ugrupo.id)
            if group_id != 1:
                _create_group_permission({
                    'group': group_id,
                    'read': True,
                    'write': True,
                    'delete': True,
                    'change_config': True,
                }, vip_id)


def update_groups_permissions(groups_permissions, vip_id, user, replace_permissions=False):
    """Creates permissions to access for vips"""

    # groups default
    if not groups_permissions:
        for group in UsuarioGrupo.list_by_user_id(user.id):
            group_id = int(group.ugrupo.id)
            if group_id != 1:
                groups_permissions.append({
                    'group': group_id,
                    'read': True,
                    'write': True,
                    'delete': True,
                    'change_config': True,
                })

    groups_perms = models.VipRequestGroupPermission.objects.filter(vip_request=vip_id)

    groups_permissions_idx = [gp['group'] for gp in groups_permissions]
    groups_perm_idx = [gp.user_group_id for gp in groups_perms]

    for group_perm in groups_perms:

        # change or delete group != 1(ADM)
        if group_perm.user_group_id != 1:
            # update perms
            if group_perm.user_group_id in groups_permissions_idx:
                idx = groups_permissions_idx.index(group_perm.user_group_id)
                _update_group_permission(groups_permissions[idx], group_perm.id)
            # delete perms
            elif replace_permissions is True:

                models.VipRequestGroupPermission.objects.filter(
                    id=group_perm.id).delete()

    for group_permission in groups_permissions:

        # change or delete group != 1(ADM)
        if group_permission['group'] != 1:
            # insert perms
            if group_permission['group'] not in groups_perm_idx:
                _create_group_permission(group_permission, vip_id)


def _create_group_permission(group_permission, vip_id):
    """Creates permissions to access for vips"""

    vip_perm = models.VipRequestGroupPermission()
    vip_perm.vip_request_id = vip_id
    vip_perm.user_group_id = group_permission['group']
    vip_perm.read = group_permission['read']
    vip_perm.write = group_permission['write']
    vip_perm.delete = group_permission['delete']
    vip_perm.change_config = group_permission['change_config']
    vip_perm.save()


def _update_group_permission(group_permission, obj_id):
    """Updates permissions to access for vips"""

    vip_perm = models.VipRequestGroupPermission.objects.get(id=obj_id)
    vip_perm.user_group_id = group_permission['group']
    vip_perm.read = group_permission['read']
    vip_perm.write = group_permission['write']
    vip_perm.delete = group_permission['delete']
    vip_perm.change_config = group_permission['change_config']
    vip_perm.save()


def get_vip_request_by_pool(pool_id):
    pool_assoc_vip = models.VipRequest.objects.filter(
        viprequestport__viprequestportpool__server_pool__id=pool_id
    )
    return pool_assoc_vip
