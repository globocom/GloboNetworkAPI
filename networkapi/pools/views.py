# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
def home(request):
    return Response({'message': 'success'})
