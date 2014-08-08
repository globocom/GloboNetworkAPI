# -*- coding:utf-8 -*-

'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

import logging

import os.path
from networkapi.log import Log

# Configuração do arquivo de log do projeto.
LOG_FILE = '/tmp/logs/networkapi/networkapi.log'
LOG_LEVEL = logging.DEBUG
LOG_DAYS = 10
LOG_SHOW_SQL = True
LOG_USE_STDOUT = True

VLAN_CACHE_TIME = None
EQUIPMENT_CACHE_TIME = None

# Inicialização do log
# O primeiro parâmetro informa o nome do arquivo de log a ser gerado.
# O segundo parâmetro é o número de dias que os arquivos ficarão mantidos.
# O terceiro parâmetro é o nível de detalhamento do Log.
Log.init_log(LOG_FILE, LOG_DAYS, LOG_LEVEL, use_stdout=LOG_USE_STDOUT)


# Configurações de banco de dados
DATABASE_ENGINE = 'mysql'      # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'telecom'      # Or path to database file if using sqlite3.
DATABASE_USER = 'telecom'      # Not used with sqlite3.
DATABASE_PASSWORD = 'telecom'  # Not used with sqlite3.
DATABASE_HOST = 'dev.mysql.globoi.com'    # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '3306'         # Set to empty string for default. Not used with sqlite3.
DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB"}


# Aplicação rodando em modo Debug
DEBUG = True

# CONFIGURAÇÃO DO MEMCACHED
CACHE_BACKEND = 'memcached://localhost:11211/'

# Diretório dos arquivos dos scripts
SCRIPTS_DIR=os.path.abspath(os.path.join(__file__, '../../scripts'))
print SCRIPTS_DIR