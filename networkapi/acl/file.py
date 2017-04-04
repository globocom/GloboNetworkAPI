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
import os


class FileError(Exception):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        msg = u'%s' % (self.error)
        return msg.encode('utf-8', 'replace')


logger = logging.getLogger(__name__)


class File():

    @classmethod
    def read(cls, file_name):
        """Reading File

        @param file_name: File name

        @raise FileError: Failed to reading file
        """
        try:

            file_name = './%s' % file_name

            file_acl = open(file_name, 'r')
            content = file_acl.read()
            file_acl.close()

            return content

        except Exception, e:
            logger.error(e)
            raise FileError(e)

    @classmethod
    def write(cls, file_name, content):
        """Writing File

        @param file_name: File name
        @param content: File content

        @raise FileError: Failed to writing file
        """
        try:

            file_name = './%s' % file_name

            file_acl = open(file_name, 'w')
            file_acl.write(content)
            file_acl.close()

        except Exception, e:
            logger.error(e)
            raise FileError(e)

    @classmethod
    def create(cls, file_name):
        """Creating File

        @param file_name: File name

        @raise FileError: Failed to creating file
        """
        try:

            file_name = './%s' % file_name

            file_acl = open(file_name, 'w')
            file_acl.close()

        except Exception, e:
            logger.error(e)
            raise FileError(e)

    @classmethod
    def remove(cls, file_name):
        """Removing File

        @param file_name: File name

        @raise FileError: Failed to removing file
        """
        try:

            file_name = './%s' % file_name

            erro = os.system('rm %s' % file_name)

        except Exception, e:
            logger.error(e)
            raise FileError(e)
