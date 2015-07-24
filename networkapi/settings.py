# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import logging

from networkapi.log import Log

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# Configurações de banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'NAME': 'telecom',
        'USER': 'root',
        'PASSWORD': 'password',
        'PORT': '3306',
        'OPTIONS': {"init_command": "SET storage_engine=INNODB"}
    }
}

from networkapi.models.models_signal_receiver import *

# Aplicação rodando em modo Debug
DEBUG = True

# CONFIGURAÇÃO DO MEMCACHED
CACHE_BACKEND = 'memcached://localhost:11211/'

# Diretório dos arquivos dos scripts
SCRIPTS_DIR = os.path.abspath(os.path.join(__file__, '../../scripts'))

# Armazena a raiz do projeto.
SITE_ROOT = os.path.realpath(__file__ + "/../../../../")

TEMPLATE_DEBUG = DEBUG

API_VERSION = '15.96'

# On create group will associate the 'authenticate' permission
# automatically if 'True'
ASSOCIATE_PERMISSION_AUTOMATICALLY = True
ID_AUTHENTICATE_PERMISSION = 5

ADMINS = (
    ('Suporte Telecom', 'suptel@corp.globo.com'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {

    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'networkapi.log.CommonAdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}


MANAGERS = ADMINS

DEFAULT_CHARSET = 'utf-8'  # Set the encoding to database data

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211'
        ]
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-BR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ry@zgop%w80_nu83#!tbz)m&7*i@1)d-+ki@5^d#%6-&^216sg'

# Configuração do arquivo de log do projeto.
LOG_FILE = '/tmp/networkapi.log'
LOG_LEVEL = logging.DEBUG
LOG_DAYS = 10
LOG_SHOW_SQL = False
LOG_USE_STDOUT = False
LOG_SHOW_TRACEBACK = True

VLAN_CACHE_TIME = None
EQUIPMENT_CACHE_TIME = None

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #     'django.template.loaders.eggs.load_template_source',
)

if LOG_SHOW_SQL:
    MIDDLEWARE_CLASSES = (
        'networkapi.extra_logging.middleware.ExtraLoggingMiddleware',
        'django.middleware.common.CommonMiddleware',
        #        'django.contrib.sessions.middleware.SessionMiddleware',
        #        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'networkapi.SQLLogMiddleware.SQLLogMiddleware',
        'networkapi.processExceptionMiddleware.LoggingMiddleware',
    )
else:
    MIDDLEWARE_CLASSES = (
        'networkapi.extra_logging.middleware.ExtraLoggingMiddleware',
        'django.middleware.common.CommonMiddleware',
        'networkapi.processExceptionMiddleware.LoggingMiddleware',
        #        'django.contrib.sessions.middleware.SessionMiddleware',
        #        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

ROOT_URLCONF = 'networkapi.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'templates')
)

INSTALLED_APPS = (
    #    'django.contrib.auth',
    #    'django.contrib.contenttypes',
    #    'django.contrib.sessions',
    #    'django.contrib.sites',
    'networkapi.ambiente',
    'networkapi.equipamento',
    'networkapi.eventlog',
    'networkapi.grupo',
    'networkapi.healthcheckexpect',
    'networkapi.interface',
    'networkapi.ip',
    'networkapi.requisicaovips',
    'networkapi.roteiro',
    'networkapi.tipoacesso',
    'networkapi.usuario',
    'networkapi.vlan',
    'networkapi.grupovirtual',
    'networkapi.models',
    'networkapi.filter',
    'networkapi.filterequiptype',
    'networkapi.blockrules',
    'networkapi.config',
    'networkapi.rack',
    'rest_framework',
    'networkapi.snippets',
    'networkapi.api_pools',
)


"""Rest Configuration
"""
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'networkapi.api_rest.authentication.BasicAuthentication',
    ),
}


NETWORKAPI_VERSION = "1.0"

# Intervals to calculate the vlan_num in POST request /vlan/.
MIN_VLAN_NUMBER_01 = 2
MAX_VLAN_NUMBER_01 = 1001
MIN_VLAN_NUMBER_02 = 1006
MAX_VLAN_NUMBER_02 = 4094

# Intervals to calculate the oct4 of the IP in POST request /ip/.
MIN_OCT4 = 5
MAX_OCT4 = 250

TEST_RUNNER = 'django_pytest.test_runner.TestRunner'

##########
# Scripts

# VLAN
VLAN_REMOVE = 'navlan -i %d --remove'
VLAN_CREATE = 'navlan -I %d -L2 --cria'

# REDE
NETWORKIPV4_CREATE = 'navlan -I %d --IPv4 --cria'
NETWORKIPV6_CREATE = 'navlan -I %d --IPv6 --cria'
NETWORKIPV4_REMOVE = 'navlan -I %d --IPv4 --remove'
NETWORKIPV6_REMOVE = 'navlan -I %d --IPv6 --remove'

VIP_CREATE = 'gerador_vips -i %d --cria'
VIP_REMOVE = 'gerador_vips -i %d --remove'

"""
 Manager Scripts Pool
"""
POOL_CREATE = 'gerador_vips --pool %s --cria'
POOL_REMOVE = 'gerador_vips --pool %s --remove'
POOL_HEALTHCHECK = 'gerador_vips --pool %s --healthcheck'
POOL_REAL_CREATE = 'gerador_vips --pool %s --id_ip %s --port_ip %s --add'
POOL_REAL_REMOVE = 'gerador_vips --pool %s --id_ip %s --port_ip %s --del'
POOL_REAL_ENABLE = 'gerador_vips -p %s --id_ip %s --port_ip %s --ena'
POOL_REAL_DISABLE = 'gerador_vips -p %s --id_ip %s --port_ip %s --dis'
POOL_REAL_CHECK = 'gerador_vips -p %s --id_ip %s --port_ip %s --chk'
POOL_REAL_CHECK_BY_POOL = 'gerador_vips --pool %s --check_status'
POOL_REAL_CHECK_BY_VIP = 'gerador_vips --vip %s --check_status'

# Script to Managemant Status Pool Members
POOL_MANAGEMENT_MEMBERS_STATUS = "gerador_vips --pool %s --apply_status"

# Script to Managemant Status Pool Members
POOL_MANAGEMENT_LB_METHOD = "gerador_vips --pool %s --lb_method"
POOL_MANAGEMENT_LIMITS = "gerador_vips --pool %s --maxconn"


# VIP REAL
VIP_REAL_v4_CREATE = 'gerador_vips -i %s --real %s --ip %s --add'
VIP_REAL_v6_CREATE = 'gerador_vips -i %s --real %s --ipv6 %s --add'
VIP_REAL_v4_REMOVE = 'gerador_vips -i %s --real %s --ip %s --del'
VIP_REAL_v6_REMOVE = 'gerador_vips -i %s --real %s --ipv6 %s --del'
VIP_REAL_v4_ENABLE = 'gerador_vips -i %s --real %s --ip %s --ena'
VIP_REAL_v6_ENABLE = 'gerador_vips -i %s --real %s --ipv6 %s --ena'
VIP_REAL_v4_DISABLE = 'gerador_vips -i %s --real %s --ip %s --dis'
VIP_REAL_v6_DISABLE = 'gerador_vips -i %s --real %s --ipv6 %s --dis'
VIP_REAL_v4_CHECK = 'gerador_vips -i %s --real %s --ip %s --chk'
VIP_REAL_v6_CHECK = 'gerador_vips -i %s --real %s --ipsv6 %s --chk'

# VIP REAL - new calls
VIP_REALS_v4_CREATE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --add'
VIP_REALS_v6_CREATE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --add'
VIP_REALS_v4_REMOVE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --del'
VIP_REALS_v6_REMOVE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --del'
VIP_REALS_v4_ENABLE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --ena'
VIP_REALS_v6_ENABLE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --ena'
VIP_REALS_v4_DISABLE = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --dis'
VIP_REALS_v6_DISABLE = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --dis'
VIP_REALS_v4_CHECK = 'gerador_vips -i %s --id_ip %s --port_ip %s --port_vip %s --chk'
VIP_REALS_v6_CHECK = 'gerador_vips -i %s --id_ipv6 %s --port_ip %s --port_vip %s --chk'



##################################
#       QUEUE SETTINGS
##################################
QUEUE_DESTINATION = u"/topic/networkapi_queue"
QUEUE_BROKER_URI = u"failover:(tcp://localhost:61613,tcp://server2:61613,tcp://server3:61613)?randomize=falsa,startupMaxReconnectAttempts=2,maxReconnectAttempts=1e"
QUEUE_BROKER_CONNECT_TIMEOUT = 2

###################################
#    PATH ACLS
###################################

PATH_ACL = os.path.join(PROJECT_ROOT_PATH, 'ACLS/')
import sys
reload(sys)

sys.setdefaultencoding('utf-8')

# Inicialização do log
# O primeiro parâmetro informa o nome do arquivo de log a ser gerado.
# O segundo parâmetro é o número de dias que os arquivos ficarão mantidos.
# O terceiro parâmetro é o nível de detalhamento do Log.
Log.init_log(LOG_FILE, LOG_DAYS, LOG_LEVEL, use_stdout=LOG_USE_STDOUT)

###################################
# PATH RACKS
###################################
#### HARDCODED - MUDA SEMPRE QE ATUALIZARMOS O SO DO TOR
KICKSTART_SO_LF="n6000-uk9-kickstart.7.1.0.N1.1b.bin"
IMAGE_SO_LF="n6000-uk9.7.1.0.N1.1b.bin"
#### <<<<<

PATH_TO_GUIDE = "/vagrant/networkapi/rack/roteiros/"
PATH_TO_CONFIG = "/vagrant/networkapi/rack/configuracao/"

PATH_TO_MV = "/vagrant/networkapi/rack/delete/"
LEAF = "LF-CM"
OOB = "OOB-CM"
SPN = "SPN-CM"
FORMATO = ".cfg"

DIVISAODC_MGMT="NA"
AMBLOG_MGMT="NA"
GRPL3_MGMT="REDENOVODC"

### FOREMAN
USE_FOREMAN=False
FOREMAN_URL="http://foreman_server"
FOREMAN_USERNAME="admin"
FOREMAN_PASSWORD="password"
FOREMAN_HOSTS_ENVIRONMENT_ID=1
