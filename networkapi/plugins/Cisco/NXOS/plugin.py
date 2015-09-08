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
from networkapi.plugins import exceptions as base_exceptions
from networkapi.log import Log
from ...base import BasePlugin

import re
from time import sleep
import unicodedata, string

log = Log(__name__)

class NXOS(BasePlugin):

	admin_privileges = -1
	management_vrf = 'management'
	VALID_TFTP_GET_MESSAGE = 'Copy complete, now saving to disk'

	def copyScriptFileToConfig (self, filename, use_vrf=None, destination="running-config"):
		'''
		Copy file from TFTP server to destination
		By default, plugin should apply file in running configuration (active)
		'''
		if use_vrf == None:
			use_vrf = self.management_vrf

		command = 'copy tftp://%s/%s %s vrf %s\n\n' %(tftpserver, filename, destination, vrf)

		log.info("sending command: %s" % command)

		self.channel.send("%s\n" % command)
		recv = self.waitString(self.VALID_TFTP_GET_MESSAGE)

		return recv

	def ensure_privilege_level(self, privilege_level=self.admin_privileges):

		recv = self.waitString(">|#")
		channel.send("show privilege\n")
		recv = self.waitString("Current privilege level:")
		level = re.search('Current privilege level: (-[0-9]+?).*', recv, re.DOTALL ).group(1)

		level = (level.split(' '))[-1]
		if int(level) < privilege_level:
			channel.send("enable\n")
			recv = self.waitString("Password:")
			channel.send("%s\n" % enable_pass)
			recv = self.waitString("#")
