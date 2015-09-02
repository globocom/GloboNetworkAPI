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

log = Log(__name__)

def copyScriptFileToConfig(remote_conn,tftpserver,filename, vpn_instance="vpn-instance management"):
	try:
		stdin, stdout, stderr = remote_conn.exec_command('tftp %s get %s %s' %(tftpserver,filename, vpn_instance))
		switch_output=stdout.readlines()
	except:
		log.error("Error copying config file to equipment.", stderr)
		raise api_exceptions.NetworkAPIException()

	try:
		local_filename = re.split('\/', file)[-1]
		stdin, stdout, stderr = remote_conn.exec_command('execute %s' %(local_filename))
		switch_output+=stdout.readlines()
	except:
		log.error("Error executing config file in equipment.", stderr)
		raise api_exceptions.NetworkAPIException()

	return switch_output
