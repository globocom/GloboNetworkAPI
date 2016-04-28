#  migra environmentvip[]
from django.db.transaction import commit_on_success

from networkapi.requisicaovips.models import *
from networkapi.api_vip_request.models import *
from networkapi.ambiente.models import EnvironmentVip


@commit_on_success
def run2():

    vip_requests = RequisicaoVips.objects.all()
    for vip_request in vip_requests:
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
                            vrpp = VipRequestPortPool.objects.filter(server_pool=pool.server_pool, vip_request_port=vrp)[0]
                        except:
                            vrpp = VipRequestPortPool()
                            vrpp.server_pool = pool.server_pool
                            vrpp.vip_request_port = vrp
                            vrpp.optionvip = op
                            vrpp.save()

        except Exception, e:
            print '%s, %s' % (e, vip_request.id)


def run():
    run2()
