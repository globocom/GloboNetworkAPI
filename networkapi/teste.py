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

from networkapi.infrastructure.ipaddr import IPv4Network, IPv6Network, IPv6Address, IPNetwork

net4 = IPv4Network('192.168.0.0/16')
net4_sub = IPv4Network('192.168.1.0/24')
nets4 = (IPv4Network('192.168.1.0/24'), IPv4Network('192.168.2.0/24'),
         IPv4Network('192.168.3.0/24'), IPv4Network('192.168.4.0/24'), IPv4Network('192.168.5.0/24'))

print net4.supernet()

"""
for x in net4.iter_subnets(new_prefix = 24):
    if x not in nets4:
        print str(x)

net6 = IPv6Network('2001:db8:afe:14::0/64')
for x in net6.iter_subnets(new_prefix = 96):
    print str(x)
"""
"""
net6 = IPv6Network('2001:db8:afe:14::0/127')
print net6.numhosts
print net6.broadcast
print net6.network
print net6.netmask

ips = [IPv6Address('2001:db8::1'), IPv6Address('2001:db8::2'), IPv6Address('2001:db8::4'), IPv6Address('2001:db8::5'), IPv6Address('2001:db8::6')]
count = 0
for x in net6.iterhosts():
    count = count + 1
    if x not in ips:
        print str(count) + ' - ' + str(x)
"""
