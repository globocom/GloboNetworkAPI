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
import glob
import logging
import os
import re
import sys
import time
import traceback
from logging.handlers import codecs
from logging.handlers import TimedRotatingFileHandler

from django.conf import settings
from django.utils.log import AdminEmailHandler

from networkapi.extra_logging.filters import ExtraLoggingFilter

LOG = logging.getLogger(__name__)


def convert_to_utf8(object):
    """Converte o object informado para uma representação em utf-8"""
    return unicode(str(object), 'utf-8', 'replace')


def get_lock():
    """Obtém lock para evitar que várias mensagens sejam sobrepostas no log"""
    try:
        from django.core.cache import cache
        cache.default_timeout = 0

        if cache._cache and hasattr(cache._cache, 'get_stats'):
            stats = cache._cache.get_stats()
        else:
            stats = []

        if stats:
            while cache.add('logger_lock', 1, 1) == 0:
                time.sleep(0.1)
                pass

    except ImportError:
        dump_file = open('/tmp/networkapi_log_error_dump', 'a')
        traceback.print_exc(file=dump_file)
        dump_file.close()
        pass


def release_lock():
    """Obtém lock para evitar que várias mensagens sejam sobrepostas no log"""
    try:
        from django.core.cache import cache
        cache.default_timeout = 0
        cache.delete('logger_lock')
    except ImportError:
        pass


class NetworkAPILogFormatter(logging.Formatter):

    def formatException(self, ei):
        s = logging.Formatter.formatException(self, ei)
        return convert_to_utf8(s)


class MultiprocessTimedRotatingFileHandler(TimedRotatingFileHandler):

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        # evita que seja rodado o log ao mesmo tempo por dois processos.
        get_lock()
        try:
            self.stream.close()
            # get the time that this sequence started at and make it a
            # TimeTuple
            t = self.rolloverAt - self.interval
            timeTuple = time.localtime(t)
            dfn = self.baseFilename + '.' + \
                time.strftime(self.suffix, timeTuple)
            if not os.path.exists(dfn):
                os.rename(self.baseFilename, dfn)
                if self.backupCount > 0:
                    # find the oldest log file and delete it
                    s = glob.glob(self.baseFilename + '.20*')
                    if len(s) > self.backupCount:
                        s.sort()
                        os.remove(s[0])
            if self.encoding:
                self.stream = codecs.open(
                    self.baseFilename, 'a', self.encoding)
            else:
                self.stream = open(self.baseFilename, 'a')
            self.rolloverAt = self.rolloverAt + self.interval
        except Exception:
            dump_file = open('/tmp/networkapi_log_error_dump', 'a')
            traceback.print_exc(file=dump_file)
            dump_file.close()
        finally:
            release_lock()


class Log(object):

    """Classe responsável por encapsular a API de logging.
    Encapsula as funcionalidades da API de logging de forma a adicionar o
    nome do módulo nas mensagens que forem impressas.
    """

    # Define o nome do arquivo de log
    _LOG_FILE_NAME = '/tmp/networkapi.log'

    # Define o número de dias que os logs serão mantidos
    _NUMBER_OF_DAYS_TO_LOG = 10

    # Define o nível de detalhamento do log a ser utilizado
    _LOG_LEVEL = logging.DEBUG

    # Define o formato do log padrão
    _LOG_FORMAT = '%(asctime)s %(request_user)-6s %(request_path)-8s %(request_id)-6s %(levelname)-6s - %(message)s'

    _USE_STDOUT = True

    _MAX_LINE_SIZE = 2048

    _PATTERN_XML_PASSWORD = [
        '<password>(.*?)</password>', '<enable_pass>(.*?)</enable_pass>', '<pass>(.*?)</pass>']

    def __init__(self, module_name):
        """Cria um logger para o módulo informado."""
        self.module_name = module_name
        self.__init_log(Log._LOG_FILE_NAME,
                        Log._NUMBER_OF_DAYS_TO_LOG,
                        Log._LOG_LEVEL,
                        Log._LOG_FORMAT,
                        Log._USE_STDOUT,
                        Log._MAX_LINE_SIZE)

    def __is_handler_added(self, logger, handler_class):
        for handler in logger.handlers:
            if isinstance(handler, handler_class):
                return True

        return False

    def __init_log(self,
                   log_file_name,
                   number_of_days_to_log,
                   log_level,
                   log_format,
                   use_stdout,
                   max_line_size):
        """Cria o logger com os parâmetros especificados"""

        # obtém o logger
        self.logger = logging.getLogger()

        my_filter = ExtraLoggingFilter('extra_logging')

        self.logger.addFilter(my_filter)

        if len(self.logger.handlers) == 0:
            # if not self.__is_handler_added(self.logger, MultiprocessTimedRotatingFileHandler):
            # LOG.info("#### initializing handler
            # MultiprocessTimedRotatingFileHandler log...")
            log_dir = os.path.split(log_file_name)[0]
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, mode=0755)
            fh = MultiprocessTimedRotatingFileHandler(log_file_name,
                                                      'midnight',
                                                      backupCount=number_of_days_to_log,
                                                      encoding='utf-8')
            fmt = NetworkAPILogFormatter(log_format)

            fh.addFilter(my_filter)
            fh.setFormatter(fmt)
            self.logger.setLevel(log_level)
            self.logger.addHandler(fh)
            if use_stdout:
                sh = logging.StreamHandler(sys.stdout)
                sh.addFilter(my_filter)
                sh.setFormatter(fmt)
                self.logger.addHandler(sh)

    @classmethod
    def init_log(cls,
                 log_file_name=_LOG_FILE_NAME,
                 number_of_days_to_log=_NUMBER_OF_DAYS_TO_LOG,
                 log_level=_LOG_LEVEL,
                 log_format=_LOG_FORMAT,
                 use_stdout=_USE_STDOUT,
                 max_line_size=_MAX_LINE_SIZE):
        Log._LOG_FILE_NAME = log_file_name
        Log._NUMBER_OF_DAYS_TO_LOG = number_of_days_to_log
        Log._LOG_LEVEL = log_level
        Log._LOG_FORMAT = log_format
        Log._USE_STDOUT = use_stdout
        Log._MAX_LINE_SIZE = max_line_size

    def __emit(self, method, msg, args):
        """Emite uma mensagem de log"""
        try:
            get_lock()
            msg = (msg % args)
            if len(msg) > self._MAX_LINE_SIZE:
                msg = msg[0:self._MAX_LINE_SIZE] + '...'
            method(msg, extra={'module_name': self.module_name})
        finally:
            release_lock()

    def rest(self, msg, *args):
        msg = self._search_hide_password(msg)
        self.__emit(self.logger.debug, msg, args)

    def debug(self, msg, *args):
        """Imprime uma mensagem de debug no log"""
        self.__emit(self.logger.debug, msg, args)

    def info(self, msg, *args):
        """Imprime uma mensagem de informação no log"""
        self.__emit(self.logger.info, msg, args)

    def warning(self, msg, *args):
        """Imprime uma mensagem de advertência no log"""
        self.__emit(self.logger.warning, msg, args)

    def error(self, msg, *args):
        """Imprime uma mensagem de erro no log"""
        try:
            get_lock()
            msg = str(msg) % args

            show_traceback = getattr(settings, 'LOG_SHOW_TRACEBACK', True)

            self.logger.error(
                msg, extra={'module_name': self.module_name}, exc_info=show_traceback)
        finally:
            release_lock()

    def _search_hide_password(self, msg):

        for text in self. _PATTERN_XML_PASSWORD:
            r = re.compile(text)
            m = r.search(msg)
            if m:
                password = m.group(1)
                msg = msg.replace(password, '****')

        return msg


class CommonAdminEmailHandler(AdminEmailHandler):

    """An exception log handler that e-mails log entries to site admins.
    If the request is passed as the first argument to the log record,
    request data will be provided in the
    """

    def emit(self, record):
        if sys.version_info < (2, 5):
            request = record.exc_info[2].tb_frame.f_locals['request']
        else:
            request = record.request

        post_values = request.POST.copy()

        for values in post_values:
            r = re.compile('<password>(.*?)</password>')
            m = r.search(post_values[values])
            if m:
                password = m.group(1)
                msg = re.sub(
                    password, '****', post_values[values]) if password != '****' else post_values[values]

            post_values[values] = msg

        request.POST = post_values

        if(post_values.has_key('password')):

            # Change PASSWORD value to '*'
            post_values['password'] = '****'
            request.POST = post_values

        # Get META value
        meta_values = request.META.copy()

        if(meta_values.has_key('HTTP_NETWORKAPI_PASSWORD')):

            # Change HTTP_NETWORKAPI_PASSWORD value to '*'
            meta_values['HTTP_NETWORKAPI_PASSWORD'] = '****'
            request.META = meta_values

        super(CommonAdminEmailHandler, self).emit(record)

# if __name__ == '__main__':
#     Log.init_log()
#     log = Log('teste')
#     log.debug('A debug message %s', 'teste' * 501)
#     log = Log('teste2')
#     log.debug('A debug message')
#     print 'waiting...'
#     time.sleep(20)
#     log = Log('teste')
#     log.debug('A debug message')
#     log = Log('teste2')
#     log.debug('A debug message')
#     print 'done!'
