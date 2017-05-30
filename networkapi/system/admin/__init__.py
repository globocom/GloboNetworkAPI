# -*- coding: utf-8 -*-
from django.contrib import admin

from .variable import VariableAdmin
from networkapi.system.models import Variable

admin.site.register(Variable, VariableAdmin)
