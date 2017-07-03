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
import commands
import logging
import os


class CVSError(Exception):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        msg = u'%s' % (self.error)
        return msg.encode('utf-8', 'replace')


class CVSCommandError(CVSError):

    def __init__(self, error):
        CVSError.__init__(self, error)


logger = logging.getLogger(__name__)


class Cvs():

    @classmethod
    def remove(cls, archive):
        """Execute command remove in cvs

        @param archive: file to be remove

        @raise CVSCommandError: Failed to execute command
        """
        try:

            erro = os.system('cvs remove %s' % archive)

        except Exception, e:
            logger.error(e)

        finally:

            if (erro):
                msg = 'CVS error: remove the file %s' % archive
                logger.error(msg)
                raise CVSCommandError(msg)

    @classmethod
    def add(cls, archive):
        """Execute command add in cvs

        @param archive: file to be add

        @raise CVSCommandError: Failed to execute command
        """
        try:

            erro = os.system('cvs add %s' % archive)

        except Exception, e:
            logger.error(e)

        finally:

            if (erro):
                msg = 'CVS error: add the file %s' % archive
                logger.error(msg)
                raise CVSCommandError(msg)

    @classmethod
    def commit(cls, archive, comment):
        """Execute command commit in cvs

        @param archive: file to be committed
        @param comment: comments

        @raise CVSCommandError: Failed to execute command
        """
        try:

            erro = os.system("cvs commit -m '%s' %s" % (comment, archive))

        except Exception, e:
            logger.error(e)

        finally:

            if (erro):
                msg = 'CVS error: commit the file %s' % archive
                logger.error(msg)
                raise CVSCommandError(msg)

    @classmethod
    def synchronization(cls):
        """Execute command update in cvs

        @raise CVSCommandError: Failed to execute command
        """
        try:
            (status, output) = commands.getstatusoutput('cvs update')

        except Exception, e:
            logger.error(e)

        finally:

            if (status):
                msg = 'CVS error: synchronization cvs: %s' % output
                logger.error(msg)
                raise CVSCommandError(msg)
