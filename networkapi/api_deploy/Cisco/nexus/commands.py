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
from time import sleep

log = Log(__name__)

ERROR_REGEX = '[Ee][Rr][Rr][Oo][Rr]|[Ff]ail|%|utility is occupied|'
INVALID_REGEX = '.*([Ii]nvalid)'
VALID_TFTP_PUT_MESSAGE = 'TFTP put operation was successful'

validChars = "-_.()\r\n %s%s" % (string.ascii_letters, string.digits)

def removeDisallowedChars(data):
	data = u'%s' % data
	cleanedStr = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
	return ''.join(c for c in cleanedStr if c in validChars)

def copyTftpToConfig (channel, tftpserver, filename, vrf="vrf management", destination="running-config"):
	'''
	Configuration Specific for cisco nexus - copy file from TFTP
	'''

	if vrf is None:
		command = 'copy tftp://%s/%s %s\n\n' %(tftpserver, filename, destination)
	else:
		command = 'copy tftp://%s/%s %s %s\n\n' %(tftpserver, filename, destination, vrf)

	log.info("sending command: %s" % command)

	channel.send("%s\n" % command)
	recv = _waitString(channel, VALID_TFTP_PUT_MESSAGE)

	return recv

def ensure_privilege_level(channel, enable_pass, privilege_level=-1):

	recv = _waitString(channel, ">|#")
	channel.send("show privilege\n")
	recv = _waitString(channel, "Current privilege level:")
	level = re.search('Current privilege level: (-[0-9]+?).*', recv, re.DOTALL ).group(1)

	level = (level.split(' '))[-1]
	if int(level) < privilege_level:
		channel.send("enable\n")
		recv = _waitString(channel, "Password:")
		channel.send("%s\n" % enable_pass)
		recv = _waitString(channel, "#")

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

def _waitString(channel, wait_str_ok_regex, wait_str_failed_regex=ERROR_REGEX):

	string_ok = 0
	recv_string = ''
	while not string_ok:
		while not channel.recv_ready():
			sleep(1)
		recv_string = channel.recv(9999)
		file_name_string = removeDisallowedChars(recv_string)
		if re.search(wait_str_failed_regex, recv_string, re.DOTALL ):
			raise exceptions.CommandErrorException(file_name_string)
		elif re.search(INVALID_REGEX, recv_string, re.DOTALL ):
			raise exceptions.InvalidCommandException(file_name_string)
		elif re.search(wait_str_ok_regex, recv_string, re.DOTALL ):
			string_ok = 1

	return recv_string
