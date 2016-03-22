#  migra environmentvip[]
from django.db.transaction import commit_on_success
from networkapi.requisicaovips.models import *
from networkapi.api_vip_request.models import *
from networkapi.ambiente.models import EnvironmentVip


def run():
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
                vp.port = 0
                vp.save()

                if mp.get('persistencia'):

                    try:
                        op = OptionVip.objects.get(tipo_opcao=u'Persistencia', nome_opcao_txt=mp['persistencia'])
                    except:
                        op = OptionVip()
                        op.tipo_opcao = u'Persistencia'
                        op.nome_opcao_txt = mp['persistencia']
                        op.save()
                        opv = OptionVipEnvironmentVip()
                        opv.option = op
                        opv.environment = ev
                        opv.save()
                    finally:
                        vro = VipRequestOptionVip()
                        vro.optionvip = op
                        vro.vip_request = vp
                        vro.save()

                if mp.get('timeout'):

                    try:
                        op = OptionVip.objects.get(tipo_opcao=u'timeout', nome_opcao_txt=mp['timeout'])
                    except:
                        op = OptionVip()
                        op.tipo_opcao = u'timeout'
                        op.nome_opcao_txt = mp['timeout']
                        op.save()
                        opv = OptionVipEnvironmentVip()
                        opv.option = op
                        opv.environment = ev
                        opv.save()
                    finally:
                        vro = VipRequestOptionVip()
                        vro.optionvip = op
                        vro.vip_request = vp
                        vro.save()

                if mp.get('trafficreturn'):

                    try:
                        op = OptionVip.objects.get(tipo_opcao=u'Retorno de trafego', id=mp['trafficreturn'])
                    except:
                        op = OptionVip()
                        op.tipo_opcao = u'Retorno de trafego'
                        op.nome_opcao_txt = mp['trafficreturn']
                        op.save()
                        opv = OptionVipEnvironmentVip()
                        opv.option = op
                        opv.environment = ev
                        opv.save()
                    finally:
                        vro = VipRequestOptionVip()
                        vro.optionvip = op
                        vro.vip_request = vp
                        vro.save()

                if mp.get('cache'):

                    try:
                        op = OptionVip.objects.get(tipo_opcao=u'cache', nome_opcao_txt=mp['cache'])
                    except:
                        op = OptionVip()
                        op.tipo_opcao = u'cache'
                        op.nome_opcao_txt = mp['cache']
                        op.save()
                        opv = OptionVipEnvironmentVip()
                        opv.option = op
                        opv.environment = ev
                        opv.save()
                    finally:
                        vro = VipRequestOptionVip()
                        vro.optionvip = op
                        vro.vip_request = vp
                        vro.save()

                pools = VipPortToPool.get_by_vip_id(vip_request.id)

                for pool in pools:

                    vrp = VipRequestPool()
                    vrp.id = pool.id
                    vrp.server_pool = pool.server_pool
                    vrp.port = pool.port_vip
                    vrp.vip_request = vp

                    try:
                        op = OptionVip.objects.get(tipo_opcao='l7_match', nome_opcao_txt='default')
                    except:
                        op = OptionVip()
                        op.tipo_opcao = u'l7_match'
                        op.nome_opcao_txt = u'default'
                        op.save()
                        opv = OptionVipEnvironmentVip()
                        opv.option = op
                        opv.environment = ev
                        opv.save()
                    finally:
                        vrp.optionvip = op
                        vrp.save()

        except:
            print 'err'


run()
