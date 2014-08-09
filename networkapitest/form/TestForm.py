# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.forms import *


class TestForm(Form):

    url = URLField(widget=widgets.Textarea(
        {'cols': '100', 'rows': '1'}), label=u'URL', initial='http://', required=True)
    #method = CharField(max_length=6, label=u'Método', required=True)
    method = ChoiceField(choices=[('DELETE', 'DELETE'), ('GET', 'GET'),
                                  ('POST', 'POST'), ('PUT', 'PUT')], label=u'Método', required=True)
    username = CharField(
        max_length=45, label=u'Usuário', initial='ORQUESTRACAO', required=True)
    password = CharField(max_length=45, label=u'Senha',
                         initial='93522a36bf2a18e0cc25857e06bbfe8b', required=True)
    request_xml = CharField(widget=widgets.Textarea(
        {'cols': '100', 'rows': '20'}), label=u'XML Requisição', required=False)
