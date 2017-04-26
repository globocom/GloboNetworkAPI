# -*- coding: utf-8 -*-
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

from settings import ADMIN_MEDIA_PREFIX
from settings import ADMINS
from settings import ALLOWED_HOSTS
from settings import AMBLOG_MGMT
from settings import APPLYED_CONFIG_REL_PATH
from settings import ASSOCIATE_PERMISSION_AUTOMATICALLY
from settings import BROKER_CONNECT_TIMEOUT
from settings import BROKER_DESTINATION
from settings import BROKER_URL
from settings import CACHE_BACKEND
from settings import CACHES
from settings import CELERY_ACCEPT_CONTENT
from settings import CELERY_DEFAULT_EXCHANGE_TYPE
from settings import CELERY_DEFAULT_QUEUE
from settings import CELERY_DEFAULT_ROUTING_KEY
from settings import CELERY_QUEUES
from settings import CELERY_RESULT_PERSISTENT
from settings import CELERY_RESULT_SERIALIZER
from settings import CELERY_TASK_RESULT_EXPIRES
from settings import CELERY_TASK_SERIALIZER
from settings import CELERY_TIMEZONE
from settings import CELERYD_PREFETCH_MULTIPLIER
from settings import CONFIG_FILES_PATH
from settings import CONFIG_FILES_REL_PATH
from settings import CONFIG_TEMPLATE_PATH
from settings import DATABASES
from settings import DEBUG
from settings import DEFAULT_CHARSET
from settings import DIVISAODC_MGMT
from settings import EQUIPMENT_CACHE_TIME
from settings import FOREMAN_HOSTS_ENVIRONMENT_ID
from settings import FOREMAN_PASSWORD
from settings import FOREMAN_URL
from settings import FOREMAN_USERNAME
from settings import FORMATO
from settings import ID_AUTHENTICATE_PERMISSION
from settings import IMAGE_SO_LF
from settings import INTERFACE_CONFIG_FILES_PATH
from settings import INTERFACE_CONFIG_REL_PATH
from settings import INTERFACE_CONFIG_TEMPLATE_PATH
from settings import INTERFACE_CONFIG_TOAPPLY_REL_PATH
from settings import KICKSTART_SO_LF
from settings import LANGUAGE_CODE
from settings import LEAF
from settings import LOG_DAYS
from settings import LOG_DB_LEVEL
from settings import LOG_FILE
from settings import LOG_LEVEL
from settings import LOG_SHOW_SQL
from settings import LOG_SHOW_TRACEBACK
from settings import LOG_USE_STDOUT
from settings import LOGGING
from settings import MANAGERS
from settings import MAX_OCT4
from settings import MAX_VLAN_NUMBER_01
from settings import MAX_VLAN_NUMBER_02
from settings import MEDIA_ROOT
from settings import MEDIA_URL
from settings import MIDDLEWARE_CLASSES
from settings import MIN_OCT4
from settings import MIN_VLAN_NUMBER_01
from settings import MIN_VLAN_NUMBER_02
from settings import NETWORK_CONFIG_FILES_PATH
from settings import NETWORK_CONFIG_REL_PATH
from settings import NETWORK_CONFIG_TEMPLATE_PATH
from settings import NETWORK_CONFIG_TOAPPLY_REL_PATH
from settings import NETWORKAPI_DATABASE_HOST
from settings import NETWORKAPI_DATABASE_NAME
from settings import NETWORKAPI_DATABASE_OPTIONS
from settings import NETWORKAPI_DATABASE_PASSWORD
from settings import NETWORKAPI_DATABASE_PORT
from settings import NETWORKAPI_DATABASE_USER
from settings import NETWORKAPI_FOREMAN_PASSWORD
from settings import NETWORKAPI_FOREMAN_URL
from settings import NETWORKAPI_FOREMAN_USERNAME
from settings import NETWORKAPI_MEMCACHE_HOSTS
from settings import NETWORKAPI_SUPPORT_EMAIL
from settings import NETWORKAPI_SUPPORT_TIME
from settings import NETWORKAPI_TFTP_SERVER_ADDR
from settings import NETWORKAPI_USE_FOREMAN
from settings import NETWORKIPV4_CREATE
from settings import NETWORKIPV4_REMOVE
from settings import NETWORKIPV6_CREATE
from settings import NETWORKIPV6_REMOVE
from settings import OOB
from settings import PATH_ACL
from settings import PATH_TO_ADD_CONFIG
from settings import PATH_TO_CONFIG
from settings import PATH_TO_GUIDE
from settings import PATH_TO_MV
from settings import POOL_CREATE
from settings import POOL_HEALTHCHECK
from settings import POOL_MANAGEMENT_LB_METHOD
from settings import POOL_MANAGEMENT_LIMITS
from settings import POOL_MANAGEMENT_MEMBERS_STATUS
from settings import POOL_MEMBER_PRIORITIES
from settings import POOL_REAL_CHECK
from settings import POOL_REAL_CHECK_BY_POOL
from settings import POOL_REAL_CHECK_BY_VIP
from settings import POOL_REAL_CREATE
from settings import POOL_REAL_DISABLE
from settings import POOL_REAL_ENABLE
from settings import POOL_REAL_REMOVE
from settings import POOL_REMOVE
from settings import POOL_SERVICEDOWNACTION
from settings import PROJECT_APPS
from settings import PROJECT_ROOT_PATH
from settings import REL_PATH_TO_ADD_CONFIG
from settings import REL_PATH_TO_CONFIG
from settings import REST_FRAMEWORK
from settings import ROOT_URLCONF
from settings import SCRIPTS_DIR
from settings import SECRET_KEY
from settings import SITE_ID
from settings import SITE_ROOT
from settings import SPECS
from settings import SPN
from settings import STATIC_ROOT
from settings import STATIC_URL
from settings import TEMPLATE_CONTEXT_PROCESSORS
from settings import TEMPLATE_DEBUG
from settings import TEMPLATE_DIRS
from settings import TEMPLATE_LOADERS
from settings import TFTP_SERVER_ADDR
from settings import TFTPBOOT_FILES_PATH
from settings import TIME_ZONE
from settings import USE_FOREMAN
from settings import USE_I18N
from settings import USER_SCRIPTS_FILES_PATH
from settings import USER_SCRIPTS_REL_PATH
from settings import USER_SCRIPTS_TOAPPLY_REL_PATH
from settings import VIP_CREATE
from settings import VIP_REAL_v4_CHECK
from settings import VIP_REAL_v4_CREATE
from settings import VIP_REAL_v4_DISABLE
from settings import VIP_REAL_v4_ENABLE
from settings import VIP_REAL_v4_REMOVE
from settings import VIP_REAL_v6_CHECK
from settings import VIP_REAL_v6_CREATE
from settings import VIP_REAL_v6_DISABLE
from settings import VIP_REAL_v6_ENABLE
from settings import VIP_REAL_v6_REMOVE
from settings import VIP_REALS_v4_CHECK
from settings import VIP_REALS_v4_CREATE
from settings import VIP_REALS_v4_DISABLE
from settings import VIP_REALS_v4_ENABLE
from settings import VIP_REALS_v4_REMOVE
from settings import VIP_REALS_v6_CHECK
from settings import VIP_REALS_v6_CREATE
from settings import VIP_REALS_v6_DISABLE
from settings import VIP_REALS_v6_ENABLE
from settings import VIP_REALS_v6_REMOVE
from settings import VIP_REMOVE
from settings import VLAN_CACHE_TIME
from settings import VLAN_CREATE
from settings import VLAN_REMOVE

MIDDLEWARE_CLASSES += (
    'django_pdb.middleware.PdbMiddleware',
)

# Third party apps
INSTALLED_APPS = (
    # 'bootstrap_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_pdb',
    'rest_framework',
)

INSTALLED_APPS += PROJECT_APPS

LOGGING['loggers']['default']['level'] = logging.DEBUG
LOGGING['loggers']['django']['level'] = logging.DEBUG
LOGGING['loggers']['django.request']['level'] = logging.DEBUG
LOGGING['loggers']['bigsuds']['level'] = logging.INFO
LOGGING['loggers']['suds']['level'] = logging.INFO
LOGGING['loggers']['django.db.backends']['level'] = logging.DEBUG
LOGGING['handlers']['log_file']['level'] = logging.DEBUG
LOGGING['handlers']['console']['level'] = logging.DEBUG
