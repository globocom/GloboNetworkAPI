# -*- coding:utf-8 -*-
import logging

log = logging.getLogger(__name__)

# files have "#SYNC_VIP" to find where have migrations


def old_to_new(vip_request):

    from networkapi.ambiente.models import EnvironmentVip
    from networkapi.api_vip_request.models import VipRequest, VipRequestDSCP, VipRequestOptionVip, \
        VipRequestPort, VipRequestPortOptionVip, VipRequestPortPool
    from networkapi.requisicaovips.models import DsrL3_to_Vip, OptionVip, OptionVipEnvironmentVip, \
        VipPortToPool

    mp = vip_request.variables_to_map()
    try:

        try:
            ev = EnvironmentVip().get_by_values(mp['finalidade'], mp['cliente'], mp['ambiente'])
        except:
            ev = EnvironmentVip()
            ev.finalidade_txt = mp['finalidade']
            ev.cliente_txt = mp['cliente']
            ev.ambiente_p44_txt = mp['ambiente']
            ev.description = '%s - %s - %s' % (mp['finalidade'], mp['cliente'], mp['ambiente'])
            ev.save()
        finally:

            vp = VipRequest()
            vp.environmentvip = ev
            vp.id = vip_request.id
            vp.name = mp['host'] if mp.get('host') else None
            vp.business = mp['areanegocio'] if mp.get('areanegocio') else vp.name
            vp.service = mp['nome_servico'] if mp.get('nome_servico') else vp.name
            vp.ipv4 = vip_request.ip if vip_request.ip else None
            vp.ipv6 = vip_request.ipv6 if vip_request.ipv6 else None
            vp.created = vip_request.vip_criado
            vp.save()

            if mp.get('persistencia'):
                persistencia = mp['persistencia']
            else:
                persistencia = '(nenhum)'

            try:
                op = OptionVip.objects.filter(tipo_opcao=u'Persistencia', nome_opcao_txt=persistencia)[0]
                try:
                    opv = OptionVipEnvironmentVip.objects.get(option=op, environment=ev)
                except:
                    opv = OptionVipEnvironmentVip()
                    opv.option = op
                    opv.environment = ev
                    opv.save()
            except:
                op = OptionVip()
                op.tipo_opcao = u'Persistencia'
                op.nome_opcao_txt = persistencia
                op.save()
                opv = OptionVipEnvironmentVip()
                opv.option = op
                opv.environment = ev
                opv.save()
            finally:
                try:
                    vro = VipRequestOptionVip.objects.filter(optionvip=op, vip_request=vp)[0]
                except:
                    vro = VipRequestOptionVip()
                    vro.optionvip = op
                    vro.vip_request = vp
                    vro.save()

            if mp.get('timeout'):
                timeout = mp['timeout']
            else:
                timeout = '5'

            try:
                op = OptionVip.objects.filter(tipo_opcao=u'timeout', nome_opcao_txt=timeout)[0]
                try:
                    opv = OptionVipEnvironmentVip.objects.get(option=op, environment=ev)
                except:
                    opv = OptionVipEnvironmentVip()
                    opv.option = op
                    opv.environment = ev
                    opv.save()
            except:
                op = OptionVip()
                op.tipo_opcao = u'timeout'
                op.nome_opcao_txt = timeout
                op.save()
                opv = OptionVipEnvironmentVip()
                opv.option = op
                opv.environment = ev
                opv.save()
            finally:
                try:
                    vro = VipRequestOptionVip.objects.get(optionvip=op, vip_request=vp)[0]
                except:
                    vro = VipRequestOptionVip()
                    vro.optionvip = op
                    vro.vip_request = vp
                    vro.save()

            if mp.get('trafficreturn'):
                trafficreturn = mp['trafficreturn']
            else:
                trafficreturn = 12

            try:
                op = OptionVip.objects.filter(tipo_opcao=u'Retorno de trafego', id=trafficreturn)[0]
                try:
                    opv = OptionVipEnvironmentVip.objects.get(option=op, environment=ev)
                except:
                    opv = OptionVipEnvironmentVip()
                    opv.option = op
                    opv.environment = ev
                    opv.save()
            except:
                op = OptionVip()
                op.tipo_opcao = u'Retorno de trafego'
                op.nome_opcao_txt = trafficreturn
                op.save()
                opv = OptionVipEnvironmentVip()
                opv.option = op
                opv.environment = ev
                opv.save()
            finally:
                try:
                    vro = VipRequestOptionVip.objects.get(optionvip=op, vip_request=vp)[0]
                except:
                    vro = VipRequestOptionVip()
                    vro.optionvip = op
                    vro.vip_request = vp
                    vro.save()

            if int(trafficreturn) == 48:
                dsrl3 = DsrL3_to_Vip.get_by_vip_id(vip_request.id)

                try:
                    vp_dsrl3 = VipRequestDSCP.objects.get(vip_request=vp)
                except:
                    vp_dsrl3 = VipRequestDSCP()
                    vp_dsrl3.vip_request = vp

                vp_dsrl3.dscp = dsrl3.id_dsrl3 / 4
                vp_dsrl3.save()
            else:
                try:
                    vp_dsrl3 = VipRequestDSCP.objects.get(vip_request=vp)
                    vp_dsrl3.delete()
                except:
                    pass

            if mp.get('cache'):
                cache = mp['cache']
            else:
                cache = '(nenhum)'

            try:
                op = OptionVip.objects.filter(tipo_opcao=u'cache', nome_opcao_txt=cache)[0]
                try:
                    opv = OptionVipEnvironmentVip.objects.get(option=op, environment=ev)
                except:
                    opv = OptionVipEnvironmentVip()
                    opv.option = op
                    opv.environment = ev
                    opv.save()
            except:
                op = OptionVip()
                op.tipo_opcao = u'cache'
                op.nome_opcao_txt = cache
                op.save()
                opv = OptionVipEnvironmentVip()
                opv.option = op
                opv.environment = ev
                opv.save()
            finally:

                try:
                    vro = VipRequestOptionVip.objects.get(optionvip=op, vip_request=vp)[0]
                except:
                    vro = VipRequestOptionVip()
                    vro.optionvip = op
                    vro.vip_request = vp
                    vro.save()

            pools = VipPortToPool.get_by_vip_id(vip_request.id)
            # delete old ports
            ports_current = VipRequestPort.objects.filter(vip_request=vp)
            ports_ids = [port.id for port in ports_current]
            pools_ids = [pl.id for pl in pools]
            ids_to_del = list(set(ports_ids) - set(pools_ids))
            ports_current.filter(id__in=ids_to_del).delete()

            for pool in pools:

                # saving ports of vip

                vrp = VipRequestPort()
                vrp.id = pool.id
                vrp.vip_request = vp
                vrp.port = pool.port_vip
                vrp.save()

                # descobre protocolo l7 e l4
                tipo_opcao = 'l7_rule'
                nome_opcao_txt = '(nenhum)'
                l4_protocol = 'TCP'
                l7_protocol = 'Outros'
                if mp.get('healthcheck_type') == 'HTTP':
                    tipo_opcao = 'l7_rule'
                    nome_opcao_txt = 'default'
                    l4_protocol = 'TCP'
                    l7_protocol = 'HTTP'

                if mp.get('healthcheck_type') == 'TCP':
                    l4_protocol = 'TCP'
                    l7_protocol = 'Outros'

                if mp.get('healthcheck_type') == 'UDP':
                    l4_protocol = 'UDP'
                    l7_protocol = 'Outros'

                if pool.port_vip == 20 or pool.port_vip == 21:
                    l4_protocol = 'TCP'
                    l7_protocol = 'FTP'

                if pool.port_vip == 443:
                    l4_protocol = 'TCP'
                    l7_protocol = 'HTTPS'

                # l4_protocol
                try:
                    op_l4 = OptionVip.objects.filter(tipo_opcao='l4_protocol', nome_opcao_txt=l4_protocol)[0]
                    try:
                        opv = OptionVipEnvironmentVip.objects.get(option=op_l4, environment=ev)
                    except:
                        opv = OptionVipEnvironmentVip()
                        opv.option = op_l4
                        opv.environment = ev
                        opv.save()
                except:
                    op_l4 = OptionVip()
                    op_l4.tipo_opcao = u'l4_protocol'
                    op_l4.nome_opcao_txt = l4_protocol
                    op_l4.save()
                    opv = OptionVipEnvironmentVip()
                    opv.option = op_l4
                    opv.environment = ev
                    opv.save()
                finally:
                    try:
                        vro = VipRequestPortOptionVip.objects.filter(optionvip=op_l4, vip_request_port=vrp)[0]
                    except:
                        vro = VipRequestPortOptionVip()
                        vro.optionvip = op_l4
                        vro.vip_request_port = vrp
                        vro.save()

                # l7_protocol
                try:
                    op_l7 = OptionVip.objects.filter(tipo_opcao='l7_protocol', nome_opcao_txt=l7_protocol)[0]
                    try:
                        opv = OptionVipEnvironmentVip.objects.get(option=op_l7, environment=ev)
                    except:
                        opv = OptionVipEnvironmentVip()
                        opv.option = op_l7
                        opv.environment = ev
                        opv.save()
                except:
                    op_l7 = OptionVip()
                    op_l7.tipo_opcao = u'l7_protocol'
                    op_l7.nome_opcao_txt = l7_protocol
                    op_l7.save()
                    opv = OptionVipEnvironmentVip()
                    opv.option = op_l7
                    opv.environment = ev
                    opv.save()
                finally:
                    try:
                        vro = VipRequestPortOptionVip.objects.filter(optionvip=op_l7, vip_request_port=vrp)[0]
                    except:
                        vro = VipRequestPortOptionVip()
                        vro.optionvip = op_l7
                        vro.vip_request_port = vrp
                        vro.save()

                # saving pools of port
                try:
                    op = OptionVip.objects.filter(tipo_opcao=tipo_opcao, nome_opcao_txt=nome_opcao_txt)[0]
                    try:
                        opv = OptionVipEnvironmentVip.objects.get(option=op, environment=ev)
                    except:
                        opv = OptionVipEnvironmentVip()
                        opv.option = op
                        opv.environment = ev
                        opv.save()
                except:
                    op = OptionVip()
                    op.tipo_opcao = tipo_opcao
                    op.nome_opcao_txt = nome_opcao_txt
                    op.save()
                    opv = OptionVipEnvironmentVip()
                    opv.option = op
                    opv.environment = ev
                    opv.save()
                finally:
                    try:
                        vrpp = VipRequestPortPool.objects.filter(
                            server_pool=pool.server_pool, vip_request_port=vrp)[0]
                    except:
                        vrpp = VipRequestPortPool()
                        vrpp.server_pool = pool.server_pool
                        vrpp.vip_request_port = vrp
                        vrpp.optionvip = op
                        vrpp.save()

    except Exception, e:
        log.error(e)
        raise e


def new_to_old(vp):

    from networkapi.api_vip_request.models import VipRequestDSCP
    from networkapi.requisicaovips.models import DsrL3_to_Vip, \
        RequisicaoVips, VipPortToPool

    try:
        vip_map = dict()
        vip = RequisicaoVips()
        vip.id = vp.id
        vip.ip = vp.ipv4 if vp.ipv4 else None
        vip.ipv6 = vp.ipv6 if vp.ipv6 else None
        vip_map['ip'] = vp.ipv4 if vp.ipv4 else None
        vip_map['ipv6'] = vp.ipv6 if vp.ipv6 else None
        vip_map['finalidade'] = vp.environmentvip.finalidade_txt
        vip_map['cliente'] = vp.environmentvip.cliente_txt
        vip_map['ambiente'] = vp.environmentvip.ambiente_p44_txt
        for vp_optionvip in vp.viprequestoptionvip_set.all():
            if vp_optionvip.optionvip.tipo_opcao == u'Persistencia':
                vip_map['persistencia'] = vp_optionvip.optionvip.nome_opcao_txt
            if vp_optionvip.optionvip.tipo_opcao == u'timeout':
                vip_map['timeout'] = vp_optionvip.optionvip.nome_opcao_txt
            if vp_optionvip.optionvip.tipo_opcao == u'cache':
                vip_map['cache'] = vp_optionvip.optionvip.nome_opcao_txt
            if vp_optionvip.optionvip.tipo_opcao == u'Retorno de trafego':
                vip_map['trafficreturn'] = vp_optionvip.optionvip.id

        vip_map['host'] = vp.name
        vip_map['areanegocio'] = vp.business
        vip_map['nome_servico'] = vp.service
        vip_map['vip_ports_to_pools'] = list()

        ports = vp.viprequestport_set.all()

        # delete old ports
        pools_current = VipPortToPool.get_by_vip_id(vip.id)
        pools_ids = [pool.id for pool in pools_current]
        ports_ids = [pt.id for pt in ports]
        ids_to_del = list(set(pools_ids) - set(ports_ids))
        pools_current.filter(id__in=ids_to_del).delete()

        vip.vip_criado = vp.created
        vip.save()

        for port in ports:
            pools = port.viprequestportpool_set.all()

            for pool in pools:
                if pool.optionvip.nome_opcao_txt in (u'(nenhum)', u'default'):
                    vip_port = {
                        'id': port.id,
                        'requisicao_vip': vip,
                        'server_pool': pool.server_pool,
                        'port_vip': port.port
                    }
                    vip_map['vip_ports_to_pools'].append(vip_port)

                    vip_port_obj = VipPortToPool(**vip_port)
                    vip_port_obj.save()

        if int(vip_map['trafficreturn']) == 48:
            dsrl3 = VipRequestDSCP.objects.get(vip_request=vp)

            try:
                vp_dsrl3 = DsrL3_to_Vip.get_by_vip_id(vip.id)
            except:
                vp_dsrl3 = DsrL3_to_Vip()
                vp_dsrl3.requisicao_vip_id = vip.id

            vp_dsrl3.id_dsrl3 = dsrl3.dscp * 4
            vp_dsrl3.save()
        else:
            try:
                vp_dsrl3 = DsrL3_to_Vip.get_by_vip_id(vip.id)
                vp_dsrl3.delete()
            except:
                pass

        vip.set_new_variables(vip_map)
        vip.save()

    except Exception, e:
        log.error(e)
        raise e


def delete_old(ids):

    from networkapi.requisicaovips.models import RequisicaoVips
    try:
        if isinstance(ids, list):
            RequisicaoVips.objects.filter(id__in=ids).delete()
        else:
            RequisicaoVips.objects.filter(id=ids).delete()

    except Exception, e:
        log.error(e)
        # raise e


def delete_new(ids):
    from networkapi.api_vip_request.models import VipRequest
    try:
        if isinstance(ids, list):
            VipRequest.objects.filter(id__in=ids).delete()
        else:
            VipRequest.objects.filter(id=ids).delete()
    except Exception, e:
        log.error(e)
        # raise e
