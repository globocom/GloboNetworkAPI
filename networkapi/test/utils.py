#encoding: utf-8
import logging
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi import environment_settings
from networkapi.log import Log

log = Log('testing')

def show_sql(sql=True):
    """ Habilita ou desabilida a exibição das queries no django """
    
    if sql:
        logging.getLogger('django.db.backends').level = logging.DEBUG
        environment_settings.LOG_SHOW_SQL = True
    else:
        logging.getLogger('django.db.backends').level = logging.INFO
        environment_settings.LOG_SHOW_SQL = False

def xml2dict(x):
    """ Converte o XML com pai <networkapi>  para um dicionario. O elemento raiz não é retornado """
    d = loads(x)
    return d[0]['networkapi']


def dict2xml(x):
    return dumps_networkapi(x)


# CASOS = [
#         {'finalidade': 'Producao', 'cliente': 'Usuario WEB', 'ambiente':'Portal FE','cache': '(nenhum)', 'status_code': 200},
#         {'finalidade': 'Producao', 'cliente': 'Usuario WEB', 'ambiente':'Portal FE','cache': 'CACHOS-PORTAL-DSR', 'status_code': 200},

#[ { cliente: '', }, { 'cliente', '' }]


def permute(**kargs):
    """ permute(finalidade=['Producao', 'Homologacao'], cliente=['Usuario Web', 'Usuario Interno'], ...) """
    
    if len(kargs) == 0:
        return [{}]
        
    possibilidades = []
    
    # as possibilidades disponiveis são calculadas usando o primeiro item da lista com todos os valores, combinado
    # com a possibilidades do restante (recursivo)
    chave, valores = kargs.popitem()
    
    permutacoes_rabo = permute(**kargs) # o primeiro elemento já havia sido removido

    for valor in valores:
        for permutacao_rabo in permutacoes_rabo:
            possibilidade = dict()
            possibilidade.update(permutacao_rabo)
            possibilidade[chave] = valor
            possibilidades.append(possibilidade)

    return possibilidades

# map(lambda t: dict(t.items() + [('status', t in v)]), p)


