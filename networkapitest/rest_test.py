# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from urllib2 import *
from httplib import *
from urlparse import urlparse

class RestError(Exception):
    """Representa um erro ocorrido durante uma requisão REST."""
    def __init__(self, cause, message):
        self.cause = cause
        self.message = message
        
    def __str__(self):
        msg = u'Erro ao realizar requisição REST: Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class RestClient:
    """Classe utilitária para chamada de webservices REST
        
    Implementa métodos utilitários para realizações de chamadas a webservices
    REST. 
    """
    
    def __init__(self):
        proxy_support = ProxyHandler({})
        opener = build_opener(proxy_support)
        install_opener(opener)

    
    def get(self, url, auth_map=None):
        """Envia uma requisição GET para a url informada.
        
        Retorna uma tupla contendo:
        (<código de resposta http>, <corpo da resposta>). 
        """
        try:
            request = Request(url)
            if auth_map is None:
                request.add_header('NETWORKAPI_USERNAME', 'ORQUESTRACAO')
                request.add_header('NETWORKAPI_PASSWORD', '93522a36bf2a18e0cc25857e06bbfe8b')
            else:
                for key,value in auth_map.iteritems():
                    request.add_header(key, value)
            content = urlopen(request).read()
            response_code = 200
            return response_code, content
        except HTTPError, e:
            response_code = e.code
            content = e.read()
            return response_code, content
        except Exception, e:
            raise RestError(e, e.message)
    
    def post(self, url, request_data, content_type=None, auth_map=None):
        """Envia uma requisição POST.
        
        Envia o parâmetro request_data no corpo da requisição e 
        retorna uma tupla contendo: 
        (<código de resposta http>, <corpo da resposta>).
        """
        try:
            request = Request(url);
            request.add_data(request_data)
            if auth_map is None:
                request.add_header('NETWORKAPI_USERNAME', 'ORQUESTRACAO')
                request.add_header('NETWORKAPI_PASSWORD', '93522a36bf2a18e0cc25857e06bbfe8b')
            else:
                for key,value in auth_map.iteritems():
                    request.add_header(key, value)
            
            if content_type != None:
                request.add_header('Content-Type', content_type)
                
            content = urlopen(request).read()
            response_code = 200
            return response_code, content
        except HTTPError, e:
            response_code = e.code
            content = e.read()
            return response_code, content
        except Exception, e:
            raise RestError(e, e.message)
    
    def delete(self, url, request_data=None, content_type=None, auth_map=None):
        """Envia uma requisição DELETE para a url informada.
        
        Retorna uma tupla contendo: 
        (<código de resposta http>, <corpo da resposta>).
        """
        try:
            parsed_url = urlparse(url)
            connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
            headers_map = dict()
            if auth_map is None:
                headers_map['NETWORKAPI_USERNAME'] = 'ORQUESTRACAO'
                headers_map['NETWORKAPI_PASSWORD'] = '93522a36bf2a18e0cc25857e06bbfe8b'
            else:
                headers_map.update(auth_map)
            
            if content_type is not None:
                headers_map['Content-Type'] = content_type
            
            connection.request("DELETE", parsed_url.path, request_data, headers_map)
            
            response = connection.getresponse()
            return response.status, response.read()
        except Exception, e:
            raise RestError(e, e.message)
        finally:
            connection.close()

    def put(self, url, request_data, content_type=None, auth_map=None):
        """Envia uma requisição PUT.
        
        Envia o parâmetro request_data no corpo da requisição e 
        retorna uma tupla contendo: 
        (<código de resposta http>, <corpo da resposta>).
        """
        try:
            parsed_url = urlparse(url)
            connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
            headers_map = dict()
            if auth_map is None:
                headers_map['NETWORKAPI_USERNAME'] = 'ORQUESTRACAO'
                headers_map['NETWORKAPI_PASSWORD'] = '93522a36bf2a18e0cc25857e06bbfe8b'
            else:
                headers_map.update(auth_map)
            
            if content_type is not None:
                headers_map['Content-Type'] = content_type
                
            connection.request("PUT", parsed_url.path, request_data, headers_map)
            
            response = connection.getresponse()
            return response.status, response.read()
        except Exception, e:
            raise RestError(e, e.message)
        finally:
            connection.close()


def allocate_vlan():
    xml = '<?xml version="1.0" encoding="UTF-8"?><networkapi versao="1.0">' \
        '<vlan>' \
        '<nome>Teste Geovana11</nome>' \
        '<id_ambiente>18</id_ambiente>' \
        '<id_tipo_rede>9</id_tipo_rede>' \
        '</vlan>' \
        '</networkapi>'
    
#    xml = '<?xml version="1.0" encoding="UTF-8"?><networkapi versao="1.0">' \
#    '<vlan><nome>Teste6</nome><id_tipo_rede>9</id_tipo_rede><id_ambiente>11</id_ambiente><descricao>nada</descricao></vlan></networkapi>'

    status, response = RestClient().post('http://localhost:8888/vlan/', xml, 'text/plain')
    print status 
    print response

def insert_equipment():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<equipamento> '\
    '<id_tipo_equipamento>10</id_tipo_equipamento>' \
    '<id_modelo>3</id_modelo>' \
    '<nome>s05</nome>' \
    '<id_grupo>1</id_grupo>' \
    '</equipamento>' \
    '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/equipamento/', xml, 'text/plain')
    print status 
    print response
    
def insert_equipment_group():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<equipamento_grupo> '\
    '<id_grupo>2</id_grupo>' \
    '<id_equipamento>1</id_equipamento>' \
    '</equipamento_grupo>' \
    '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/equipamentogrupo/', xml, 'text/plain')
    print status 
    print response
    
def remove_equipment_group():
    status, response = RestClient().delete('http://localhost:8888/equipamentogrupo/equipamento/19/egrupo/3/')
    print status 
    print response
    
    
def search_vlans_by_environment():
    status, response = RestClient().get('http://localhost:8888/vlan/ambiente/4/')
    print status 
    print response

   
def search_all_network_type():
    status, response = RestClient().get('http://localhost:8888/tiporede/')
    print status 
    print response
    
    
def search_all_environments():
    #status, response = RestClient().get('http://localhost:8888/ambiente/')
    status, response = RestClient().get('http://localhost:8888/ambiente/divisao_dc/21/ambiente_logico/11/')
    print status 
    print response

def insert_environment():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<ambiente> '\
    '<id_grupo_l3>26</id_grupo_l3>' \
    '<id_ambiente_logico>10</id_ambiente_logico>' \
    '<id_divisao>21</id_divisao>' \
   ' <link>Teste</link>' \
    '</ambiente>' \
    '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/ambiente/', xml, 'text/plain')
    print status 
    print response

def update_environment():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<ambiente> '\
    '<id_grupo_l3>26</id_grupo_l3>' \
    '<id_ambiente_logico>10</id_ambiente_logico>' \
    '<id_divisao>1234</id_divisao>' \
   ' <link>Link</link>' \
    '</ambiente>' \
    '</networkapi>'
    
    status, response = RestClient().put('http://localhost:8888/ambiente/61/', xml, 'text/plain')
    print status 
    print response

def remove_environment():
    status, response = RestClient().delete('http://localhost:8888/ambiente/61/')
    print status 
    print response        
    
def insert_ip_equipment():
    status, response = RestClient().put('http://localhost:8888/ip/8781/equipamento/2010/', None)
    #status, response = RestClient().put('http://localhost:8888/ip/2/equipamento/4/', None)
    print status 
    print response    


def insert_ip():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<ip> '\
        '<id_vlan>292</id_vlan>' \
        '<id_equipamento></id_equipamento>' \
        '<descricao></descricao>' \
        '</ip>' \
        '</networkapi>'
    
#    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
#    '<networkapi versao="1.0">' \
#    '<ip> '\
#    '<id_vlan>908</id_vlan>' \
#    '<descricao></descricao>' \
#    '<id_equipamento>1</id_equipamento>' \
#    '</ip>' \
#    '</networkapi>'
        
    status, response = RestClient().post('http://localhost:8888/ip/', xml, 'text/plain')
    print status 
    print response

def search_equipment_by_type_environment():
    status, response = RestClient().get('http://localhost:8888/equipamento/tipoequipamento/1/ambiente/5/')
    #status, response = RestClient().get('http://localhost:8888/equipamento/tipoequipamento/3/ambiente/44/')
    print status
    print response    

def get_equipment_by_name():
    status, response = RestClient().get('http://localhost:8888/equipamento/nome/XXX/')
    print status 
    print response

def remove_ip_equipment():
    #status, response = RestClient().delete('http://localhost:8888/ip/963/equipamento/632/')
    status, response = RestClient().delete('http://localhost:8888/ip/8780/equipamento/2010/')
    print status
    print response 

def search_healthcheckexpect_by_environment():
    status, response = RestClient().get('http://localhost:8888/healthcheckexpect/ambiente/51/')
    print status
    print response 
 
def insert_vip():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<vip>' \
    '<id_ip>8890</id_ip>' \
    '<id_healthcheck_expect></id_healthcheck_expect>' \
    '<finalidade>Homologacao</finalidade>' \
    '<cliente>Usuario Interno</cliente>' \
    '<ambiente>Homologacao FE</ambiente>' \
    '<cache>(nenhum)</cache>' \
    '<metodo_bal>least-conn</metodo_bal>' \
    '<persistencia>(nenhum)</persistencia>' \
    '<healthcheck_type>HTTP</healthcheck_type>' \
    '<healthcheck></healthcheck>' \
    '<timeout>5</timeout>' \
    '<host>S05</host>' \
    '<maxcon>4</maxcon>' \
    '<dsr>dsr</dsr>' \
    '<bal_ativo></bal_ativo>' \
    '<transbordos>' \
    '<transbordo>10.0.0.2</transbordo>' \
    '</transbordos>' \
    '<reals>' \
    '<real>' \
    '<real_name>Teste</real_name>' \
    '<real_ip>10.0.0.1</real_ip>' \
    '</real>' \
    '</reals>' \
    '<portas_servicos>' \
    '<porta>34</porta>' \
    '<porta>80</porta>' \
    '</portas_servicos>' \
    '</vip>' \
    '</networkapi>'
        
#    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
#    '<networkapi versao="1.0">' \
#    '<vip>' \
#    '<id_ip>8511</id_ip>' \
#    '<id_healthcheck_expect></id_healthcheck_expect>' \
#    '<finalidade>Producao</finalidade>' \
#    '<cliente>Usuario WEB</cliente>' \
#    '<ambiente>Streaming FE</ambiente>' \
#    '<cache></cache>' \
#    '<metodo_bal>least-conn</metodo_bal>' \
#    '<persistencia>source-ip</persistencia>' \
#    '<healthcheck_type>TCP</healthcheck_type>' \
#    '<healthcheck></healthcheck>' \
#    '<timeout>5</timeout>' \
#    '<host>S05</host>' \
#    '<maxcon>4</maxcon>' \
#    '<dsr>dsr</dsr>' \
#    '<bal_ativo></bal_ativo>' \
#    '<transbordos>' \
#    '<transbordo>10.0.0.2</transbordo>' \
#    '</transbordos>' \
#    '<reals>' \
#    '<real>' \
#    '<real_name>teste</real_name>' \
#    '<real_ip>10.0.0.1</real_ip>' \
#    '</real>' \
#    '</reals>' \
#    '<portas_servicos>' \
#    '<porta>34</porta>' \
#    '<porta>80</porta>' \
#    '</portas_servicos>' \
#    '</vip>' \
#    '</networkapi>'
            
    status, response = RestClient().post('http://localhost:8888/vip/', xml, 'text/plain')
    print status 
    print response

def update_vip():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<vip>' \
    '<id_ip>8511</id_ip>' \
    '<id_healthcheck_expect></id_healthcheck_expect>' \
    '<validado>1</validado>' \
    '<vip_criado>1</vip_criado>' \
    '<finalidade>Producao</finalidade>' \
    '<cliente>Usuario WEB</cliente>' \
    '<ambiente>Aplicativos FE</ambiente>' \
    '<cache>(nenhum)</cache>' \
    '<metodo_bal>least-conn</metodo_bal>' \
    '<persistencia>source-ip</persistencia>' \
    '<healthcheck_type>TCP</healthcheck_type>' \
    '<healthcheck></healthcheck>' \
    '<timeout>5</timeout>' \
    '<host>S05</host>' \
    '<maxcon>4</maxcon>' \
    '<dsr>dsr</dsr>' \
    '<bal_ativo></bal_ativo>' \
    '<transbordos>' \
    '<transbordo>10.0.0.2</transbordo>' \
    '</transbordos>' \
    '<reals>' \
    '<real>' \
    '<real_name>teste</real_name>' \
    '<real_ip>10.0.0.5</real_ip>' \
    '</real>' \
    '</reals>' \
    '<portas_servicos>' \
    '<porta>34</porta>' \
    '<porta>80</porta>' \
    '</portas_servicos>' \
    '</vip>' \
    '</networkapi>'
    status, response = RestClient().put('http://localhost:8888/vip/41/', xml, 'text/plain')
    print status 
    print response
    
def get_environment_by_equipname_ip():
    status, response = RestClient().get('http://localhost:8888/ambiente/equipamento/XXXX/ip/10.249.35.11/')
    print status 
    print response
    
def get_vlan_by_id():
    status, response = RestClient().get('http://localhost:8888/vlan/900/')
    print status 
    print response

def remove_equipment_by_pk():
    status, response = RestClient().delete('http://localhost:8888/equipamento/11/')
    print status 
    print response

def add_real_vip():
    status, response = RestClient().post('http://localhost:8888/real/equip/631/vip/15/ip/962/', '', 'text/plain')
    print status 
    print response

def del_real_vip():
    status, response = RestClient().delete('http://localhost:8888/real/equip/481/vip/1/ip/20/')
    print status 
    print response
    
def enable_disable_real_vip():
    status, response = RestClient().put('http://localhost:8888/real/disable/equip/481/vip/1/ip/19/', '', 'text/plain')
    print status 
    print response
            
def create_vlan():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<equipamentos>' \
        '<id_equipamento>1928</id_equipamento>' \
        '</equipamentos>' \
        '</networkapi>'
        
#    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
#        '<networkapi versao="1.0">' \
#        '<equipamentos>' \
#        '<id_equipamento></id_equipamento>' \
#        '<id_equipamento></id_equipamento>' \
#        '</equipamentos>' \
#        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/vlan/900/criar/', xml, 'text/plain')
    print status 
    print response

def validate_vlan():
    status, response = RestClient().put('http://localhost:8888/vlan/300/validar/', None)
    print status 
    print response 

def create_vlan_l2():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<equipamentos>' \
        '<id_equipamento>1928</id_equipamento>' \
        '</equipamentos>' \
        '</networkapi>'
        
#    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
#        '<networkapi versao="1.0">' \
#        '<equipamentos>' \
#        '<id_equipamento></id_equipamento>' \
#        '<id_equipamento></id_equipamento>' \
#        '</equipamentos>' \
#        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/vlanl2/900/criar/', xml, 'text/plain')
    print status 
    print response

def add_vlan_trunk():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<equipamento>' \
        '<nome>RIOVLD68</nome>' \
        '<nome_interface>XTESTE5</nome_interface>' \
        '</equipamento>' \
        '</networkapi>'
        
#    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
#        '<networkapi versao="1.0">' \
#        '<equipamento>' \
#        '<nome>1</nome>' \
#        '<nome_interface></nome_interface>' \
#        '</equipamento>' \
#        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/vlan/900/add/', xml, 'text/plain')
    print status 
    print response
    
def del_vlan_trunk():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<equipamento>' \
        '<nome>RIOVLD68</nome>' \
        '<nome_interface>XTESTE1</nome_interface>' \
        '</equipamento>' \
        '</networkapi>'
        
#    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
#        '<networkapi versao="1.0">' \
#        '<equipamento>' \
#        '<nome>1</nome>' \
#        '<nome_interface></nome_interface>' \
#        '</equipamento>' \
#        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/vlan/900/del/', xml, 'text/plain')
    print status 
    print response    

def check_vlan_trunk():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<equipamento>' \
        '<nome>RIOVLD68</nome>' \
        '<nome_interface>XTESTE1</nome_interface>' \
        '</equipamento>' \
        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/vlan/900/check/', xml, 'text/plain')
    print status 
    print response 

def list_vlan_trunk():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<equipamento>' \
        '<nome>RIOVLD68</nome>' \
        '<nome_interface>XTESTE1</nome_interface>' \
        '</equipamento>' \
        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/vlan/list/', xml, 'text/plain')
    print status 
    print response 
       
def remove_virtual_group():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<equipamentos>' \
    '</equipamentos>' \
    '<vips>' \
        '<vip>' \
            '<id_ip>3655</id_ip>' \
            '<balanceadores>' \
                '<id_equipamento>80</id_equipamento>' \
                '<id_equipamento>81</id_equipamento>' \
            '</balanceadores>' \
        '</vip>' \
    '</vips>' \
    '</networkapi>'

    status, response = RestClient().delete('http://localhost:8888/grupovirtual/', xml, 'text/plain')
    print status 
    print response

def insert_virtual_group():
    # XML para Inserir Novo
#    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
#    '<networkapi versao="1.0">' \
#    '<equipamentos>' \
#        '<equipamento>' \
#                '<id_tipo_equipamento>10</id_tipo_equipamento>' \
#                '<id_modelo>18</id_modelo>' \
#                '<prefixo>S</prefixo>' \
#                '<id_grupo>1</id_grupo>' \
#                '<ip>' \
#                '<id_vlan>900</id_vlan>' \
#                '<descricao>Test Insert Virtual Group</descricao>' \
#                '</ip>' \
#        '</equipamento>' \
#        '<equipamento>' \
#                '<id_tipo_equipamento>10</id_tipo_equipamento>' \
#                '<id_modelo>18</id_modelo>' \
#                '<prefixo>S</prefixo>' \
#                '<id_grupo>1</id_grupo>' \
#                '<ip>' \
#                '<id_vlan>900</id_vlan>' \
#                '<descricao>Test Insert Virtual Group</descricao>' \
#                '</ip>' \
#        '</equipamento>' \
#    '</equipamentos>' \
#    '<vips>' \
#        '<vip>' \
#        '<id>2</id>' \
#        '<real_name_sufixo>A</real_name_sufixo>' \
#        '<ip_real><id_vlan>900</id_vlan><descricao></descricao></ip_real>' \
#        '<ip>' \
#        '<id_vlan>900</id_vlan>' \
#        '<descricao>Test Insert Virtual Group</descricao>' \
#        '</ip>' \
#        '<balanceadores>' \
#        '<id_equipamento>1950</id_equipamento>' \
#        '<id_equipamento>1951</id_equipamento>' \
#        '</balanceadores>' \
#        '<id_healthcheck_expect></id_healthcheck_expect>' \
#        '<finalidade>Homologacao</finalidade>' \
#        '<cliente>Usuario Interno</cliente>' \
#        '<ambiente>Homologacao BE</ambiente>' \
#        '<cache></cache>' \
#        '<metodo_bal>least-conn</metodo_bal>' \
#        '<persistencia>(nenhum)</persistencia>' \
#        '<healthcheck_type>TCP</healthcheck_type>' \
#        '<healthcheck></healthcheck>' \
#        '<timeout>5</timeout>' \
#        '<host>S05</host>' \
#        '<maxcon>0</maxcon>' \
#        '<dsr></dsr>' \
#        '<bal_ativo></bal_ativo>' \
#        '<transbordos>' \
#        '<transbordo>10.0.0.2</transbordo>' \
#        '</transbordos>' \
#        '<portas_servicos>' \
#        '<porta>80</porta>' \
#        '</portas_servicos>' \
#        '</vip>' \
#        '<vip>' \
#        '<id>1</id>' \
#        '<real_name_sufixo>B</real_name_sufixo>' \
#        '<ip_real><id_vlan>900</id_vlan><descricao></descricao></ip_real>' \
#        '<ip>' \
#        '<id_vlan>900</id_vlan>' \
#        '<descricao>Test Insert Virtual Group</descricao>' \
#        '</ip>' \
#        '<balanceadores>' \
#        '<id_equipamento>1950</id_equipamento>' \
#        '<id_equipamento>1951</id_equipamento>' \
#        '</balanceadores>' \
#        '<id_healthcheck_expect></id_healthcheck_expect>' \
#        '<finalidade>Homologacao</finalidade>' \
#        '<cliente>Usuario Interno</cliente>' \
#        '<ambiente>Homologacao BE</ambiente>' \
#        '<cache></cache>' \
#        '<metodo_bal>least-conn</metodo_bal>' \
#        '<persistencia>(nenhum)</persistencia>' \
#        '<healthcheck_type>TCP</healthcheck_type>' \
#        '<healthcheck></healthcheck>' \
#        '<timeout>5</timeout>' \
#        '<host>S05</host>' \
#        '<maxcon>0</maxcon>' \
#        '<dsr></dsr>' \
#        '<bal_ativo></bal_ativo>' \
#        '<transbordos>' \
#        '<transbordo>10.0.0.2</transbordo>' \
#        '</transbordos>' \
#        '<portas_servicos>' \
#        '<porta>80</porta>' \
#        '</portas_servicos>' \
#        '</vip>' \
#    '</vips>' \
#    '</networkapi>'
    
    # XML para Alterar
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<equipamentos>' \
        '<equipamento>' \
                '<id_tipo_equipamento>10</id_tipo_equipamento>' \
                '<id_modelo>18</id_modelo>' \
                '<prefixo>S</prefixo>' \
                '<id_grupo>1</id_grupo>' \
                '<ip>' \
                '<id_vlan>900</id_vlan>' \
                '<descricao>Test Insert Virtual Group</descricao>' \
                '</ip>' \
        '</equipamento>' \
        '<equipamento>' \
                '<id_tipo_equipamento>10</id_tipo_equipamento>' \
                '<id_modelo>18</id_modelo>' \
                '<prefixo>S</prefixo>' \
                '<id_grupo>1</id_grupo>' \
                '<ip>' \
                '<id_vlan>900</id_vlan>' \
                '<descricao>Test Insert Virtual Group</descricao>' \
                '</ip>' \
        '</equipamento>' \
    '</equipamentos>' \
    '<vips>' \
        '<vip>' \
        '<id>2</id>' \
        '<requisicao_vip><id>41</id></requisicao_vip>' \
        '<real_name_sufixo>A</real_name_sufixo>' \
        '<ip_real><id_vlan>900</id_vlan><descricao></descricao></ip_real>' \
        '<id_healthcheck_expect></id_healthcheck_expect>' \
        '<finalidade>Homologacao</finalidade>' \
        '<cliente>Usuario Interno</cliente>' \
        '<ambiente>Homologacao BE</ambiente>' \
        '<cache></cache>' \
        '<metodo_bal>least-conn</metodo_bal>' \
        '<persistencia>(nenhum)</persistencia>' \
        '<healthcheck_type>TCP</healthcheck_type>' \
        '<healthcheck></healthcheck>' \
        '<timeout>5</timeout>' \
        '<host>S05</host>' \
        '<maxcon>0</maxcon>' \
        '<dsr></dsr>' \
        '<bal_ativo></bal_ativo>' \
        '<transbordos>' \
        '<transbordo>10.0.0.2</transbordo>' \
        '</transbordos>' \
        '<portas_servicos>' \
        '<porta>80</porta>' \
        '</portas_servicos>' \
        '<reals>' \
        '<real><real_name>S16A</real_name><real_ip>1.1.1.12</real_ip></real>' \
        '<real><real_name>S17A</real_name><real_ip>1.1.1.15</real_ip></real>' \
        '</reals>' \
        '</vip>' \
        '<vip>' \
        '<id>1</id>' \
        '<requisicao_vip><id>42</id></requisicao_vip>' \
        '<real_name_sufixo>B</real_name_sufixo>' \
        '<ip_real><id_vlan>900</id_vlan><descricao></descricao></ip_real>' \
        '<id_healthcheck_expect></id_healthcheck_expect>' \
        '<finalidade>Homologacao</finalidade>' \
        '<cliente>Usuario Interno</cliente>' \
        '<ambiente>Homologacao BE</ambiente>' \
        '<cache></cache>' \
        '<metodo_bal>least-conn</metodo_bal>' \
        '<persistencia>(nenhum)</persistencia>' \
        '<healthcheck_type>TCP</healthcheck_type>' \
        '<healthcheck></healthcheck>' \
        '<timeout>5</timeout>' \
        '<host>S05</host>' \
        '<maxcon>0</maxcon>' \
        '<dsr></dsr>' \
        '<bal_ativo></bal_ativo>' \
        '<transbordos>' \
        '<transbordo>10.0.0.2</transbordo>' \
        '</transbordos>' \
        '<portas_servicos>' \
        '<porta>80</porta>' \
        '</portas_servicos>' \
        '<reals>' \
        '<real><real_name>S16B</real_name><real_ip>1.1.1.13</real_ip></real>' \
        '<real><real_name>S17B</real_name><real_ip>1.1.1.16</real_ip></real>' \
        '</reals>' \
        '</vip>' \
    '</vips>' \
    '</networkapi>'

    status, response = RestClient().post('http://localhost:8888/grupovirtual/', xml, 'text/plain')
    print status
    print response
    

def list_equipment_type():
    status, response = RestClient().get('http://localhost:8888/tipoequipamento/')
    print status 
    print response  


def get_request_vip_by_pk():
    status, response = RestClient().get('http://localhost:8888/vip/23/')
    print status 
    print response
    
def check_ip_belong_environment():
    status, response = RestClient().get('http://localhost:8888/ip/172.16.0.31/ambiente/15/')
    #status, response = RestClient().get('http://localhost:8888/ip/10.0.114.75/ambiente/16/')
    print status 
    print response

def search_brand():
    status, response = RestClient().get('http://localhost:8888/marca/')
    print status 
    print response              

def get_tipo_acesso():
    status, response = RestClient().get('http://localhost:8888/tipoacesso/')
    print status 
    print response

def post_tipo_acesso():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<tipo_acesso> '\
    '<protocolo>TESTE</protocolo>' \
    '</tipo_acesso>' \
    '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/tipoacesso/', xml, 'text/plain')
    print status 
    print response

def put_tipo_acesso():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<tipo_acesso> '\
    '<protocolo>TESTE</protocolo>' \
    '</tipo_acesso>' \
    '</networkapi>'
    
    status, response = RestClient().put('http://localhost:8888/tipoacesso/4/', xml, 'text/plain')
    print status 
    print response

def delete_tipo_acesso():
    status, response = RestClient().delete('http://localhost:8888/tipoacesso/4/')
    print status 
    print response

def get_equipamento_acesso():
    status, response = RestClient().get('http://localhost:8888/equipamentoacesso/')
    print status 
    print response
      
def post_equipamento_acesso():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
            '<networkapi versao="1.0">' \
            '<equipamento_acesso>' \
            '<id_equipamento>2</id_equipamento>' \
            '<fqdn>asdf</fqdn>' \
            '<user>sadf</user>' \
            '<pass>sdaf</pass>' \
            '<id_tipo_acesso>3</id_tipo_acesso>' \
            '<enable_pass></enable_pass>' \
            '</equipamento_acesso>' \
            '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/equipamentoacesso/', xml, 'text/plain')
    print status 
    print response

def put_equipamento_acesso():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
            '<networkapi versao="1.0">' \
            '<equipamento_acesso>' \
            '<fqdn>fqn</fqdn>' \
            '<user>user</user>' \
            '<pass>senha</pass>' \
            '<enable_pass>enable</enable_pass>' \
            '</equipamento_acesso>' \
            '</networkapi>'
    
    status, response = RestClient().put('http://localhost:8888/equipamentoacesso/45/3/', xml, 'text/plain')
    print status 
    print response
    
def delete_equipamento_acesso():
    status, response = RestClient().delete('http://localhost:8888/equipamentoacesso/2/3/')
    print status 
    print response

def create_brand():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<marca>' \
        '<nome>Teste1</nome>' \
        '</marca>' \
        '</networkapi>'
    status, response = RestClient().post('http://localhost:8888/marca/', xml, 'text/plain')
    print status 
    print response

def update_brand():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<marca>' \
        '<nome>Teste2</nome>' \
        '</marca>' \
        '</networkapi>'
    status, response = RestClient().put('http://localhost:8888/marca/9/', xml, 'text/plain')
    print status 
    print response                     

def search_insert_script_type():
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<tipo_roteiro>' \
                '<tipo>Teste1</tipo>' \
                '<descricao>Descricao</descricao>' \
            '</tipo_roteiro>' \
        '</networkapi>'
        
    status, response = RestClient().get('http://localhost:8888/tiporoteiro/')
    #status, response = RestClient().post('http://localhost:8888/tiporoteiro/', xml, 'text/plain')

    print status 
    print response
    
def update_remove_script_type():
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<tipo_roteiro>' \
                '<tipo>Teste11</tipo>' \
                '<descricao>Descricao1</descricao>' \
            '</tipo_roteiro>' \
        '</networkapi>'
        
    #status, response = RestClient().put('http://localhost:8888/tiporoteiro/105/', xml, 'text/plain')
    status, response = RestClient().delete('http://localhost:8888/tiporoteiro/105/')

    print status 
    print response  

 
def search_insert_script():
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<roteiro>' \
                '<id_tipo_roteiro>2</id_tipo_roteiro>' \
                '<nome>Teste1</nome>' \
                '<descricao>Descricao1</descricao>' \
            '</roteiro>' \
        '</networkapi>'
        
    #status, response = RestClient().get('http://localhost:8888/roteiro/')
    status, response = RestClient().post('http://localhost:8888/roteiro/', xml, 'text/plain')

    print status 
    print response
    
def update_remove_script():
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<roteiro>' \
                '<id_tipo_roteiro>3</id_tipo_roteiro>' \
                '<nome>Teste2</nome>' \
                '<descricao>Descricao2</descricao>' \
            '</roteiro>' \
        '</networkapi>'
        
    #status, response = RestClient().put('http://localhost:8888/roteiro/108/', xml, 'text/plain')
    status, response = RestClient().delete('http://localhost:8888/roteiro/108/')

    print status 
    print response  

def search_script_by_type():
    status, response = RestClient().get('http://localhost:8888/roteiro/tiporoteiro/345345/')
    print status 
    print response 
  
def search_script_by_equip():
    status, response = RestClient().get('http://localhost:8888/roteiro/equipamento/5/')
    print status 
    print response
    
def search_insert_equip_scripts():
    
      
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<equipamento_roteiro>' \
                '<id_equipamento>1</id_equipamento>' \
                '<id_roteiro>2</id_roteiro>' \
            '</equipamento_roteiro>' \
        '</networkapi>'
        
    #status, response = RestClient().get('http://localhost:8888/equipamentoroteiro/')   
    status, response = RestClient().post('http://localhost:8888/equipamentoroteiro/', xml, 'text/plain')

    print status 
    print response
    
def remove_equip_scripts():
    status, response = RestClient().delete('http://localhost:8888/equipamentoroteiro/1/234234/')
    print status 
    print response
          
    
def delete_brand():
    status, response = RestClient().delete('http://localhost:8888/marca/9/')
    print status 
    print response

def search_model():
    status, response = RestClient().get('http://localhost:8888/modelo/')   
    print status 
    print response

def search_model_by_brand():
    status, response = RestClient().get('http://localhost:8888/modelo/marca/3/')   
    print status 
    print response

def update_model():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<modelo>' \
        '<nome>Modelo1</nome>' \
        '<id_marca>1</id_marca>' \
        '</modelo>' \
        '</networkapi>'
    status, response = RestClient().put('http://localhost:8888/modelo/20/', xml, 'text/plain')
    print status 
    print response  

def delete_model():
    status, response = RestClient().delete('http://localhost:8888/modelo/21/')
    print status 
    print response

def search_front_back_interfaces():
    status, response = RestClient().get('http://localhost:8888/interface/00:00:AE:FF:56:FA/equipamento/1959/')   
    print status 
    print response

def create_model():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<modelo>' \
        '<nome>Modelo2</nome>' \
        '<id_marca>2</id_marca>' \
        '</modelo>' \
        '</networkapi>'

    status, response = RestClient().post('http://localhost:8888/modelo/', xml, 'text/plain')
    print status 
    print response

def search_dc_division():
    status, response = RestClient().get('http://localhost:8888/divisaodc/')   
    print status 
    print response

def create_dc_division():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<divisao_dc>' \
        '<nome>Teste</nome>' \
        '</divisao_dc>' \
        '</networkapi>'

    status, response = RestClient().post('http://localhost:8888/divisaodc/', xml, 'text/plain')
    print status 
    print response

def update_dc_division():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<divisao_dc>' \
        '<nome>teste</nome>' \
        '</divisao_dc>' \
        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/divisaodc/25/', xml, 'text/plain')
    print status 
    print response

def remove_dc_division():
    status, response = RestClient().delete('http://localhost:8888/divisaodc/25/')   
    print status 
    print response

def create_vip():
    status, response = RestClient().put('http://localhost:8888/vip/18/criar/', None)
    print status 
    print response
    

def get_tipo_rede():
    status, response = RestClient().get('http://localhost:8888/tiporede/')
    print status 
    print response

def post_tipo_rede():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<tipo_rede> '\
    '<nome>Teste3</nome>' \
    '</tipo_rede>' \
    '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/tiporede/', xml, 'text/plain')
    print status 
    print response    
        
def put_tipo_rede():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<tipo_rede> '\
    '<nome>TESTE2</nome>' \
    '</tipo_rede>' \
    '</networkapi>'
    
    status, response = RestClient().put('http://localhost:8888/tiporede/20/', xml, 'text/plain')
    print status 
    print response    

def delete_tipo_rede():
    status, response = RestClient().delete('http://localhost:8888/tiporede/21/')
    print status 
    print response

def get_interface_equipamento():
    status, response = RestClient().get('http://localhost:8888/interface/equipamento/1950/')
    print status 
    print response

def post_interface_equipamento():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<interface>' \
    '<nome>Nome2</nome>' \
    '<protegida>1</protegida>' \
    '<descricao></descricao>' \
    '<id_ligacao_front></id_ligacao_front>' \
    '<id_ligacao_back></id_ligacao_back>' \
    '<id_equipamento>1</id_equipamento>' \
    '</interface>' \
    '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/interface/', xml, 'text/plain')
    print status 
    print response    
        
def put_interface_equipamento():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
    '<interface>' \
    '<nome>Nome2</nome>' \
    '<protegida>0</protegida>' \
    '<descricao>Descricao</descricao>' \
    '<id_ligacao_front>12</id_ligacao_front>' \
    '<id_ligacao_back>12</id_ligacao_back>' \
    '</interface>' \
    '</networkapi>'
    
    status, response = RestClient().put('http://localhost:8888/interface/42/', xml, 'text/plain')
    print status 
    print response    

def delete_interface_equipamento():
    status, response = RestClient().delete('http://localhost:8888/interface/15/')
    print status 
    print response
 
def search_insert_user():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<usuario>' \
                '<user>TESTE1</user>' \
                '<pwd>teste</pwd>' \
                '<nome>geovana</nome>' \
                '<email>email</email>' \
            '</usuario>' \
        '</networkapi>'
        
    #status, response = RestClient().get('http://localhost:8888/usuario/')
    status, response = RestClient().post('http://localhost:8888/usuario/', xml, 'text/plain')

    print status 
    print response
    
def update_remove_user():
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<usuario>' \
                '<user>teste2</user>' \
                '<pwd>teste1</pwd>' \
                '<nome>geovana1</nome>' \
                '<email>email1</email>' \
                '<ativo>1</ativo>' \
            '</usuario>' \
        '</networkapi>'
        
    #status, response = RestClient().put('http://localhost:8888/usuario/35/', xml, 'text/plain')
    status, response = RestClient().delete('http://localhost:8888/usuario/1/')

    print status 
    print response  


def search_logic_environment():
    status, response = RestClient().get('http://localhost:8888/ambientelogico/')   
    print status 
    print response

def create_logic_environment():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<ambiente_logico>' \
        '<nome>homologacao</nome>' \
        '</ambiente_logico>' \
        '</networkapi>'

    status, response = RestClient().post('http://localhost:8888/ambientelogico/', xml, 'text/plain')
    print status 
    print response

def update_logic_environment():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<ambiente_logico>' \
        '<nome>TESTE1</nome>' \
        '</ambiente_logico>' \
        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/ambientelogico/23/', xml, 'text/plain')
    print status 
    print response

def remove_logic_environment():
    status, response = RestClient().delete('http://localhost:8888/ambientelogico/14/')   
    print status 
    print response

def insert_user_group():

    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<usuario_grupo>' \
                '<id_usuario>1</id_usuario>' \
                '<id_grupo>2</id_grupo>' \
            '</usuario_grupo>' \
        '</networkapi>'
        
    status, response = RestClient().post('http://localhost:8888/usuariogrupo/', xml, 'text/plain')
    print status 
    print response

def remove_user_group():
    status, response = RestClient().delete('http://localhost:8888/usuariogrupo/usuario/1/ugrupo/2/')
    print status 
    print response
    
    
def search_ugroup():
    status, response = RestClient().get('http://localhost:8888/ugrupo/')
    
    print status 
    print response

def insert_ugroup():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<grupo>' \
        '<nome>TESTE1</nome>' \
        '<leitura>S</leitura>' \
        '<escrita>N</escrita>' \
        '<edicao>S</edicao>' \
        '<exclusao>N</exclusao>' \
        '</grupo>' \
        '</networkapi>'
        
    status, response = RestClient().post('http://localhost:8888/ugrupo/', xml, 'text/plain')
    
    print status 
    print response
        
def update_ugroup():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<grupo>' \
        '<nome>TESTE</nome>' \
        '<leitura>N</leitura>' \
        '<escrita>S</escrita>' \
        '<edicao>N</edicao>' \
        '<exclusao>S</exclusao>' \
        '</grupo>' \
        '</networkapi>'
        
    status, response = RestClient().put('http://localhost:8888/ugrupo/8/', xml, 'text/plain')
    
    print status 
    print response  
    
def remove_ugroup():
    status, response = RestClient().delete('http://localhost:8888/ugrupo/8/')
    
    print status 
    print response              

def search_egroup():
    status, response = RestClient().get('http://localhost:8888/egrupo/')
    
    print status 
    print response

def insert_egroup():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<grupo>' \
        '<nome>TESTE</nome>' \
        '</grupo>' \
        '</networkapi>'
        
    status, response = RestClient().post('http://localhost:8888/egrupo/', xml, 'text/plain')
    
    print status 
    print response
        
def update_egroup():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<grupo>' \
        '<nome>Switches Core Producao</nome>' \
        '</grupo>' \
        '</networkapi>'
        
    status, response = RestClient().put('http://localhost:8888/egrupo/6/', xml, 'text/plain')
    
    print status 
    print response  
    
def remove_egroup():
    status, response = RestClient().delete('http://localhost:8888/egrupo/4/')
    
    print status 
    print response

def search_l3_group():
    status, response = RestClient().get('http://localhost:8888/grupol3/')   
    print status 
    print response

def create_l3_group():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<grupo_l3>' \
        '<nome>teste</nome>' \
        '</grupo_l3>' \
        '</networkapi>'

    status, response = RestClient().post('http://localhost:8888/grupol3/', xml, 'text/plain')
    print status 
    print response

def update_l3_group():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<grupo_l3>' \
        '<nome>acesso BAL. CACHES > BAL. VIPS</nome>' \
        '</grupo_l3>' \
        '</networkapi>'

    status, response = RestClient().put('http://localhost:8888/grupol3/47/', xml, 'text/plain')
    print status 
    print response

def remove_l3_group():
    status, response = RestClient().delete('http://localhost:8888/grupol3/13/')   
    print status 
    print response

    
def insert_equipment_environment():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<networkapi versao="1.0">' \
        '<equipamento_ambiente> '\
            '<id_equipamento>1</id_equipamento>' \
            '<id_ambiente>12</id_ambiente>' \
        '</equipamento_ambiente>' \
    '</networkapi>'
    
    status, response = RestClient().post('http://localhost:8888/equipamentoambiente/', xml, 'text/plain')
    print status 
    print response
    
def remove_equipment_environment():
    status, response = RestClient().delete('http://localhost:8888/equipamentoambiente/equipamento/1/ambiente/12/')
    print status 
    print response
    
    
def search_insert_permission():
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<permissao_administrativa>' \
                '<funcao>teste</funcao>' \
                '<leitura>0</leitura>' \
                '<escrita>1</escrita>' \
                '<grupos_id>1</grupos_id>' \
            '</permissao_administrativa>' \
        '</networkapi>'
        
    #status, response = RestClient().get('http://localhost:8888/perms/')
    status, response = RestClient().post('http://localhost:8888/perms/', xml, 'text/plain')

    print status 
    print response
    
def update_remove_permission():
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
            '<permissao_administrativa>' \
                '<funcao>TESTE</funcao>' \
                '<leitura>1</leitura>' \
                '<escrita>0</escrita>' \
                '<grupos_id>1</grupos_id>' \
            '</permissao_administrativa>' \
        '</networkapi>'
        
    status, response = RestClient().put('http://localhost:8888/perms/1234123/', xml, 'text/plain')
    #status, response = RestClient().delete('http://localhost:8888/perms/70/')

    print status 
    print response  

def get_direito_grupo_equipamento():
    #status, response = RestClient().get('http://localhost:8888/direitosgrupoequipamento/')
    #status, response = RestClient().get('http://localhost:8888/direitosgrupoequipamento/2/')
    #status, response = RestClient().get('http://localhost:8888/direitosgrupoequipamento/ugrupo/2/')
    status, response = RestClient().get('http://localhost:8888/direitosgrupoequipamento/egrupo/10000/')
    print status 
    print response

def post_direito_grupo_equipamento():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<direito_grupo_equipamento>' \
        '<id_grupo_usuario>1</id_grupo_usuario>' \
        '<id_grupo_equipamento>10000</id_grupo_equipamento>' \
        '<leitura>0</leitura>' \
        '<escrita>0</escrita>' \
        '<alterar_config>0</alterar_config>' \
        '<exclusao>0</exclusao>' \
        '</direito_grupo_equipamento>' \
        '</networkapi>'
        
    status, response = RestClient().post('http://localhost:8888/direitosgrupoequipamento/', xml, 'text/plain')
    print status 
    print response

def put_direito_grupo_equipamento():
    xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<networkapi versao="1.0">' \
        '<direito_grupo_equipamento>' \
        '<leitura>0</leitura>' \
        '<escrita>1</escrita>' \
        '<alterar_config>0</alterar_config>' \
        '<exclusao>1</exclusao>' \
        '</direito_grupo_equipamento>' \
        '</networkapi>'
        
    status, response = RestClient().put('http://localhost:8888/direitosgrupoequipamento/16/', xml, 'text/plain')
    print status 
    print response

def delete_direito_grupo_equipamento():
    status, response = RestClient().delete('http://localhost:8888/direitosgrupoequipamento/16/')
    print status 
    print response

if __name__ == '__main__':
    try:
     #   allocate_vlan()
     #   insert_equipment()
     #   insert_equipment_group()
     #   remove_equipment_group()
     #   search_vlans_by_environment()
     #   search_all_network_type()
     #   search_all_environments()
     #   insert_ip()
     #   insert_ip_equipment()
     #   search_equipment_by_type_environment()
     #   get_equipment_by_name()
     #   remove_ip_equipment()
     #   search_healthcheckexpect_by_environment()
     #   get_environment_by_equipname_ip()
     #   insert_vip()
     #   get_vlan_by_id()
     #   remove_equipment_by_pk()
     #   add_real_vip()
     #   create_vlan()
     #   validate_vlan()
     #   remove_virtual_group()
     #   enable_disable_real_vip()
     #   del_real_vip()
     #   add_vlan_trunk()
     #   del_vlan_trunk()
     #   check_vlan_trunk()
     #   list_vlan_trunk()
     #   insert_virtual_group()
     #   list_equipment_type()
     #   get_request_vip_by_pk()
     #   check_ip_belong_environment()
     #   search_brand()
     #   create_brand()
     #   search_insert_script_type()
     #   update_remove_script_type()
     #   search_insert_script()
     #   update_remove_script()
     #   search_script_by_type()
     #   search_insert_equip_scripts()
     #   search_script_by_equip()
     #   remove_equip_scripts()
     #   get_tipo_acesso()
     #   post_tipo_acesso()
     #   put_tipo_acesso()
     #   delete_tipo_acesso()
     #   delete_brand()
     #   update_brand()
     #   search_model()
     #   create_vlan_l2()
     #   update_model()
     #   get_equipamento_acesso()
     #   post_equipamento_acesso()
     #   put_equipamento_acesso()
     #   delete_equipamento_acesso()
     #   delete_model()
     #   search_front_back_interfaces()
     #   create_model()
     #   search_dc_division()
     #   create_dc_division()
        update_vip()
     #   create_vip()
     #   get_tipo_rede()
     #   post_tipo_rede()
     #   put_tipo_rede()
     #   delete_tipo_rede()
     #   update_dc_division()
     #   remove_dc_division()
     #   search_insert_user()
     #   update_remove_user()
     #   search_logic_environment()
     #   create_logic_environment()
     #   update_logic_environment()
     #   remove_logic_environment()   
     #   get_interface_equipamento()
     #   post_interface_equipamento()
     #   put_interface_equipamento()
     #   delete_interface_equipamento()   
     #   insert_user_group() 
     #   remove_user_group()
     #   search_ugroup() 
     #   insert_ugroup()
     #   update_ugroup()
     #   remove_ugroup()
     #   search_egroup() 
     #   insert_egroup()
     #   update_egroup()
     #   remove_egroup()
     #   remove_l3_group()
     #   update_l3_group()
     #   create_l3_group()
     #   search_l3_group()
     #   insert_equipment_environment()
     #   remove_equipment_environment()
     #   insert_environment()
     #   update_environment()
     #   remove_environment()
     #   search_insert_permission()
     #   update_remove_permission()
     #   search_model_by_brand()
     #   get_direito_grupo_equipamento()
     #   post_direito_grupo_equipamento()
     #   put_direito_grupo_equipamento()
     #   delete_direito_grupo_equipamento()
        pass
    except Exception, e:
        print e
