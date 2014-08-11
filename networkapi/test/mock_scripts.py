# encoding: utf-8

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

import tempfile
import os.path
import stat
from networkapi.test import log
from networkapi.infrastructure import script_utils
from django.conf import settings

# funções disponiveis via bash para os script mocks de testes
FUNCTIONS = u"""
function consulta_banco() {
    tabela=$1
    coluna=$2
    where=$3
    RESULT=$(echo "select $coluna from $tabela where $3" | mysql %(DB_USER)s %(DB_PASS)s %(DB_NAME)s -r --skip-column-names)
}

function consulta_variaveis_requisicaovip() {
    requisicao_id=$1
    variavel=$2
    consulta_banco 'requisicao_vips' 'variaveis' id_requisicao_vips=$requisicao_id
    RESULT="`echo "$RESULT" | grep "$variavel" | cut -d "=" -f 2`"
}
""" % {
    'DB_USER': "-u" + settings.DATABASES['default']['USER'],
    'DB_PASS': "-p" + settings.DATABASES['default']['PASSWORD'] if settings.DATABASES['default']['PASSWORD'] != "" else "",
    'DB_NAME': settings.DATABASES['default']['NAME'],
}


def script_path_counter(script_path):
    return '%s-counter' % script_path


class ScriptSavedState():

    """ Classe necessária para salvar o estado do módulo script_utils e restaurá-lo após o contexto "with" """

    def __init__(self, restore_dir, script_dir, script_name, ensure_running_times=1):
        self.original_dir = restore_dir
        self.script_dir = script_dir
        self.script_name = script_name
        self.ensure_running_times = ensure_running_times

    @property
    def script_path(self):
        return os.path.join(self.script_dir, self.script_name)

    @property
    def functions_path(self):
        return os.path.join(self.script_dir, 'functions.sh')

    def __exit__(self, exc_type, exc_value, traceback):
        log.debug(
            'restaurando diretório de scripts para %s', self.original_dir)

        times_called = self.times_called()

        # apaga o diretório e script criados
        # os.remove(self.script_path)
        # os.remove(self.functions_path)
        # if os.path.isfile(script_path_counter(self.script_path)):
        # os.remove(script_path_counter(self.script_path))
        # os.rmdir(script_utils.SCRIPTS_DIR)

        script_utils.SCRIPTS_DIR = self.original_dir

        # valida se foi chamado o número desejado de vezes
        if self.ensure_running_times:
            assert times_called == self.ensure_running_times, u'Era necessário ao teste executar o script %d vezes, mas ele rodou %d' % (
                self.ensure_running_times, times_called)

        # propaga a exception em caso de erro no bloco executado
        return False

    def times_called(self):
        if not os.path.isfile(script_path_counter(self.script_path)):
            return 0

        with open(script_path_counter(self.script_path), 'r') as f:
            string_times = f.read()
            return int(string_times)

    def __enter__(self):
        return self


def mock_script(script, exitcode=0, out="", err="", code=None, times=1):

    # cria um diretório temporário
    script_dir = tempfile.mkdtemp(suffix='networkapi_testes')
    log.debug('Preparando diretorio de execução de script: %s', script_dir)

    # cria o script
    if code == None:
        code = """
echo "%s" 1>&2
echo "%s"
exit %d""" % (out, err, exitcode)

    old = script_utils.SCRIPTS_DIR
    # troca o diretório na aplicação
    script_utils.SCRIPTS_DIR = script_dir

    script_state = ScriptSavedState(old, script_dir, script, times)
    write_script(script_state.script_path, __build_script(
        code, script_state.script_path, script_state.script_dir))
    write_script(script_state.functions_path, FUNCTIONS)

    return script_state


def write_script(file_path, content):
    f = open(file_path, 'w')
    f.write(content)
    f.close()
    os.chmod(file_path, stat.S_IRWXU)
    print "Escrito arquivo '%s' com conteudo:\n%s\n\n" % (file_path, content)


def __build_script(base, script_path, script_dir):

    template = """#!/bin/bash
SCRIPT_PATH_COUNTER=%(script_path_counter)s
if [ -f $SCRIPT_PATH_COUNTER ]; then
    let COUNTER=`cat $SCRIPT_PATH_COUNTER`
else
    let COUNTER=0
fi
let COUNTER++
echo -n $COUNTER > $SCRIPT_PATH_COUNTER

# O codigo do script propriamente esta abaixo
%(script)s
    """

    if base.startswith('#!'):
        interpreter = base.splitlines()[0][2:].strip()
        code = base[len(interpreter) + 3:].strip()
        script = u"""%s << FiNaLiZaCAO
        %s
        FiNaLiZaCAO""" % (interpreter, code,)
    else:
        script = u"""
        . %s/functions.sh
        %s""" % (script_dir, base.strip(),)

    args = {'script_path': script_path,
            'script_dir': script_dir,
            'script_path_counter': script_path_counter(script_path),
            'script': script,
            }

    script = template % args
    return script
