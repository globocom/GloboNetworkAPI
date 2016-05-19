import os

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


# Chooses the number of workers accordingly to the number os CPU cores


def numCPUs():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

try:
    import multiprocessing
    workers = multiprocessing.cpu_count() * 2 + 1
except ImportError:
    workers = numCPUs() * 2 + 1
    pass

# Configure your log directory
LOGDIR = "/tmp/"

PIDFILE = "%s/gunicorn-networkapi.pid" % LOGDIR
accesslog = "%s/gunicorn-networkapi_access.log" % LOGDIR
errorlog = "%s/gunicorn-networkapi_error.log" % LOGDIR
loglevel = "debug"

# Choose user/group to run the server if daemon=true
daemon = True
# user="www-data"
# group="www-data"

# IP and Port to listen
bind = "0.0.0.0:8000"

backlog = 2048
preload_app = True
pidfile = PIDFILE

timeout = 300
