# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

import os

from subprocess import Popen, PIPE, STDOUT

from networkapi.environment_settings import SCRIPTS_DIR


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
    except OSError as o:
        return o.args[0], '', o.args[1]
    except ValueError as v:
        raise ScriptError(v, u'Falha ao executar o comando %s.' % command)


if __name__ == '__main__':

    print os.path.realpath(__file__ + "/../../../../scripts/") + os.sep + 'gerador_vips'

    code, stdout, stderr = exec_script('configurador teste')
    print code
    print 'out=' + stdout
    print 'err=' + stderr
