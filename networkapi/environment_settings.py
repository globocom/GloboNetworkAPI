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


import logging

import os.path
from networkapi.log import Log

# Configuração do arquivo de log do projeto.
LOG_FILE = '/tmp/networkapi.log'
LOG_LEVEL = logging.DEBUG
LOG_DAYS = 10
LOG_SHOW_SQL = False
LOG_USE_STDOUT = True

VLAN_CACHE_TIME = None
EQUIPMENT_CACHE_TIME = None

# Inicialização do log
# O primeiro parâmetro informa o nome do arquivo de log a ser gerado.
# O segundo parâmetro é o número de dias que os arquivos ficarão mantidos.
# O terceiro parâmetro é o nível de detalhamento do Log.
Log.init_log(LOG_FILE, LOG_DAYS, LOG_LEVEL, use_stdout=LOG_USE_STDOUT)


# Configurações de banco de dados
# 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'telecom'      # Or path to database file if using sqlite3.
DATABASE_USER = 'root'         # Not used with sqlite3.
DATABASE_PASSWORD = 'root'         # Not used with sqlite3.
# Set to empty string for localhost. Not used with sqlite3.
DATABASE_HOST = 'localhost'
# Set to empty string for default. Not used with sqlite3.
DATABASE_PORT = '3306'
DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB"}

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'HOST': DATABASE_HOST,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'PORT': DATABASE_PORT,
        'OPTIONS': DATABASE_OPTIONS
    }
}


# Aplicação rodando em modo Debug
DEBUG = True

# CONFIGURAÇÃO DO MEMCACHED
CACHE_BACKEND = 'memcached://localhost:11211/'

# Diretório dos arquivos dos scripts
SCRIPTS_DIR = os.path.abspath(os.path.join(__file__, '../../scripts'))

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
