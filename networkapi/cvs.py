# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
import os
import commands
import logging


class CVSError(Exception):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        msg = u"%s" % (self.error)
        return msg.encode("utf-8", "replace")


class CVSCommandError(CVSError):

    def __init__(self, error):
        CVSError.__init__(self, error)

logger = logging.getLogger(__name__)


class Cvs():

    @classmethod
    def remove(cls, archive):
        '''Execute command remove in cvs

        @param archive: file to be remove 

        @raise CVSCommandError: Failed to execute command
        '''
        try:

            erro = os.system("cvs remove %s" % archive)

        except Exception, e:
            logger.error(e)

        finally:

            if (erro):
                msg = "CVS error: remove the file %s" % archive
                logger.error(msg)
                raise CVSCommandError(msg)

    @classmethod
    def add(cls, archive):
        '''Execute command add in cvs

        @param archive: file to be add 

        @raise CVSCommandError: Failed to execute command
        '''
        try:

            erro = os.system("cvs add %s" % archive)

        except Exception, e:
            logger.error(e)

        finally:

            if (erro):
                msg = "CVS error: add the file %s" % archive
                logger.error(msg)
                raise CVSCommandError(msg)

    @classmethod
    def commit(cls, archive, comment):
        '''Execute command commit in cvs

        @param archive: file to be committed
        @param comment: comments

        @raise CVSCommandError: Failed to execute command
        '''
        try:

            erro = os.system("cvs commit -m '%s' %s" % (comment, archive))

        except Exception, e:
            logger.error(e)

        finally:

            if (erro):
                msg = "CVS error: commit the file %s" % archive
                logger.error(msg)
                raise CVSCommandError(msg)

    @classmethod
    def synchronization(cls):
        '''Execute command update in cvs

        @raise CVSCommandError: Failed to execute command
        '''
        try:
            (status, output) = commands.getstatusoutput("cvs update")

        except Exception, e:
            logger.error(e)

        finally:

            if (status):
                msg = "CVS error: synchronization cvs: %s" % output
                logger.error(msg)
                raise CVSCommandError(msg)
