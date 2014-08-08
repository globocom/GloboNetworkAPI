# -*- coding:utf-8 -*-

'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.log import Log

class SQLLogMiddleware(object):

    log = Log('SQLLogMiddleware')

    """Loga os SQLs executados em uma requisição."""
    def process_response (self, request, response): 
        from django.db import connection
        for q in connection.queries:
            self.log.debug(u'Consulta: %s, Tempo gasto: %s', q['sql'], q['time'])
        return response