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
from networkapi.plugins.base import BasePlugin
import re
from time import sleep
import unicodedata, string

log = Log(__name__)

class Generic(BasePlugin):

	ADMIN_PRIVILEGES = 15

	def copyTftpToConfig (filename, use_vrf=None, destination="running-config"):
		'''
		Copy file from TFTP server to destination
		By default, plugin should apply file in running configuration (active)
		'''

		if vrf is None:
			command = "copy tftp://%s/%s %s\n\n" %(self.tftpserver, filename, destination)
		else:
			command = "copy tftp://%s/%s %s %s\n\n" %(self.tftpserver, filename, destination, use_vrf)

		log.info("sending command: %s" % command)

		self.channel.send("%s\n" % command)
		recv = self.waitString(channel, VALID_TFTP_PUT_MESSAGE)

		return recv

	def ensure_privilege_level(channel, privilege_level=ADMIN_PRIVILEGES):

		recv = self.waitString(channel, ">|#")
		self.channel.send("show privilege\n")
		recv = self.waitString(channel, "Current privilege level is")
		level = re.search('Current privilege level is ([0-9]+?).*', recv, re.DOTALL ).group(1)

		level = (level.split(' '))[-1]
		if int(level) < privilege_level:
			self.channel.send("enable\n")
			recv = self.waitString(self.channel, "Password:")
			self.channel.send("%s\n" % self.equipment_access.enable_pass)
			recv = self.waitString(self.channel, "#")
