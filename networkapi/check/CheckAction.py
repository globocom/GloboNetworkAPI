# -*- coding:utf-8 -*-
'''
Title: Infrastructure Orchestra
Author: globo.com / TQI
Copyright: (c) 2009 globo.com todos os direitos reservados.
'''

from django.http import HttpResponse


class CheckAction(object):

    def check(self, request):
        try:
            return HttpResponse("WORKING")
        except:
            pass  # Ignora o erro

        return HttpResponse("FAIL")
