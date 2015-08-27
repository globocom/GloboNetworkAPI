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

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.log import Log
from networkapi.api_deploy import exceptions
import re

log = Log(__name__)

ERROR_REGEX = '[Ee][Rr][Rr][Oo][Rr]|[Ff]ail|%|utility is occupied|'
INVALID_REGEX = '.*([Ii]nvalid)'
VALID_TFTP_MESSAGE = 'TFTP put operation was successful'

def copyTftpToConfig (remote_conn, tftpserver, filename, vrf="vrf management", destination="running-config"):
	'''
	Configuration Specific for cisco - copy file from TFTP
	'''

	if vrf is None:
		command = 'copy tftp://%s/%s %s' %(tftpserver, filename, destination)
	else:
		command = 'copy tftp://%s/%s %s %s' %(tftpserver, filename, destination, vrf)

	return _exec_command (remote_conn, command, VALID_TFTP_MESSAGE)

def _exec_command (remote_conn, command, success_regex, invalid_regex=INVALID_REGEX, error_regex=ERROR_REGEX):
	'''
	Configuration Specific for cisco
	'''
	try:
		stdin, stdout, stderr = remote_conn.exec_command('%s' %(command))
	except:
		log.error("Error in connection. Cannot send command.", stderr)
		raise api_exceptions.NetworkAPIException

	equip_output_lines = stdout.readlines()
	output_text = ''.join(equip_output_lines)

	if re.search(INVALID_REGEX, output_text, re.DOTALL ):
		raise exceptions.InvalidCommandException(output_text)
	elif re.search(ERROR_REGEX, output_text, re.DOTALL):
		raise exceptions.CommandErrorException
	elif re.search(success_regex, output_text, re.DOTALL):
		return output_text
	else:
		raise exceptions.UnableToVerifyResponse()

