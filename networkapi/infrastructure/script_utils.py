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

from subprocess import Popen, PIPE, STDOUT

from networkapi.settings import SCRIPTS_DIR


class ScriptError(Exception):

    """Representa um erro ocorrido durante a chamada do script."""

    def __init__(self, cause, message):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Erro ao executar o SCRIPT: Causa: %s, Mensagem: %s' % (
            self.cause, self.message)
        return msg.encode('utf-8', 'replace')


def exec_script(command):

    try:

        command = SCRIPTS_DIR + os.sep + command

        p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        child_stdout, child_stderr = p.communicate()

        child_stdout = unicode(child_stdout, 'utf-8', 'replace')
        child_stderr = unicode(child_stderr, 'utf-8', 'replace')

        return p.returncode, child_stdout, child_stderr
    except OSError, o:
        return o.args[0], '', o.args[1]
    except ValueError, v:
        raise ScriptError(v, u'Falha ao executar o comando %s.' % command)


if __name__ == '__main__':

    print os.path.realpath(__file__ + "/../../../../scripts/") + os.sep + 'gerador_vips'

    code, stdout, stderr = exec_script('configurador teste')
    print code
    print 'out=' + stdout
    print 'err=' + stderr
