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
import math
import re


def network_mask_from_cidr_mask(cidr_mask):
    """Calcula a máscara de uma rede a partir do número do bloco do endereço.

    @param cidr_mask: Valor do bloco do endereço.

    @return: Tuple com o octeto 1, 2, 3, 4 da máscara: (oct1,oct2,oct3,oct4).
    """
    address = 0xFFFFFFFF
    address = address << (32 - cidr_mask)
    return ((address >> 24) & 0xFF, (address >> 16) & 0xFF, (address >> 8) & 0xFF, (address >> 0) & 0xFF)


def _applyNetmask(host, mask):

    return (host[0] & mask[0], host[1] & mask[1], host[2] & mask[2], host[3] & mask[3])


def is_subnetwork(network_address_01, network_address_02):
    """Verifica se o endereço network_address_01 é sub-rede do endereço network_address_02.

    @param network_address_01: Uma tuple com os octetos do endereço, formato: (oct1, oct2, oct3, oct5)
    @param network_address_02: Uma tuple com os octetos do endereço e o bloco, formato: (oct1, oct2, oct3, oct5, bloco)

    @return: True se network_address_01 é sub-rede de network_address_02. False caso contrário.

    """
    if network_address_01 is None or network_address_02 is None:
        return False

    if len(network_address_01) < 4 or len(network_address_02) != 5:
        return False

    network_mask_02 = network_mask_from_cidr_mask(network_address_02[4])

    return network_address_02[0:4] == _applyNetmask(network_address_01, network_mask_02)


def is_valid_ip(address):
    """Verifica se address é um endereço ip válido."""

    if address is None:
        return address

    pattern = r'\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return re.match(pattern, address)


# ========================================================================
# Function to calculate num_hosts by prefix:
#
#    IPV4:
#            2^(32-p) = num_hosts
#    IPV6:
#            2^(128-p) = num_hosts
#
#    where 'p' is, for example, 24, 32 (x.x.x.x/32)...
#
#    so, to calculate prefix by number of hosts:
#
#        IPV4:
#            32 - logarithm(num_hosts, 2) = p
#        IPV6:
#            128 - logarithm(num_hosts, 2) = p
#
#    where 'num_hosts' is the number of hosts expected
# ========================================================================

MAX_IPV4_HOSTS = 4294967296
MAX_IPV6_HOSTS = 340282366920938463463374607431768211456


def get_prefix_IPV4(num_hosts):

    prefix = int(32 - math.log(float(num_hosts), 2))
    return prefix


def get_prefix_IPV6(num_hosts):

    prefix = int(128 - math.log(float(num_hosts), 2))
    return prefix


if __name__ == '__main__':

    print get_prefix_IPV4(17)
    print get_prefix_IPV4(33)
    print get_prefix_IPV4(255)

    # IPV4
    # ========================================================================
    # /0 : 4294967296    /11 : 2097152    /22 : 1024
    # /1 : 2147483648    /12 : 1048576    /23 : 512
    # /2 : 1073741824    /13 : 524288     /24 : 256
    # /3 : 536870912     /14 : 262144     /25 : 128
    # /4 : 268435456     /15 : 131072     /26 : 64
    # /5 : 134217728     /16 : 65536      /27 : 32
    # /6 : 67108864      /17 : 32768      /28 : 16
    # /7 : 33554432      /18 : 16384      /29 : 8
    # /8 : 16777216      /19 : 8192       /30 : 4
    # /9 : 8388608       /20 : 4096       /31 : 2
    # /10 : 4194304      /21 : 2048       /32 : 1
    # ========================================================================

    # IPV6
    # ========================================================================
    # /0 : 340282366920938463463374607431768211456  /11 : 166153499473114484112975882535043072  /22 : 81129638414606681695789005144064
    # /1 : 170141183460469231731687303715884105728  /12 : 83076749736557242056487941267521536   /23 : 40564819207303340847894502572032
    # /2 : 85070591730234615865843651857942052864   /13 : 41538374868278621028243970633760768   /24 : 20282409603651670423947251286016
    # /3 : 42535295865117307932921825928971026432   /14 : 20769187434139310514121985316880384   /25 : 10141204801825835211973625643008
    # /4 : 21267647932558653966460912964485513216   /15 : 10384593717069655257060992658440192   /26 : 5070602400912917605986812821504
    # /5 : 10633823966279326983230456482242756608   /16 : 5192296858534827628530496329220096    /27 : 2535301200456458802993406410752
    # /6 : 5316911983139663491615228241121378304    /17 : 2596148429267413814265248164610048    /28 : 1267650600228229401496703205376
    # /7 : 2658455991569831745807614120560689152    /18 : 1298074214633706907132624082305024    /29 : 633825300114114700748351602688
    # /8 : 1329227995784915872903807060280344576    /19 : 649037107316853453566312041152512     /30 : 316912650057057350374175801344
    # /9 : 664613997892457936451903530140172288     /20 : 324518553658426726783156020576256     /31 : 158456325028528675187087900672
    # /10 : 332306998946228968225951765070086144    /21 : 162259276829213363391578010288128     /32 : 79228162514264337593543950336
    #
    # /33 : 39614081257132168796771975168           /44 : 19342813113834066795298816            /55 : 9444732965739290427392
    # /34 : 19807040628566084398385987584           /45 : 9671406556917033397649408             /56 : 4722366482869645213696
    # /35 : 9903520314283042199192993792            /46 : 4835703278458516698824704             /57 : 2361183241434822606848
    # /36 : 4951760157141521099596496896            /47 : 2417851639229258349412352             /58 : 1180591620717411303424
    # /37 : 2475880078570760549798248448            /48 : 1208925819614629174706176             /59 : 590295810358705651712
    # /38 : 1237940039285380274899124224            /49 : 604462909807314587353088              /60 : 295147905179352825856
    # /39 : 618970019642690137449562112             /50 : 302231454903657293676544              /61 : 147573952589676412928
    # /40 : 309485009821345068724781056             /51 : 151115727451828646838272              /62 : 73786976294838206464
    # /41 : 154742504910672534362390528             /52 : 75557863725914323419136               /63 : 36893488147419103232
    # /42 : 77371252455336267181195264              /53 : 37778931862957161709568               /64 : 18446744073709551616
    # /43 : 38685626227668133590597632              /54 : 18889465931478580854784               /65 : 9223372036854775808
    #
    # /66 : 4611686018427387904     /77 : 2251799813685248      /88 : 1099511627776     /99 : 536870912
    # /67 : 2305843009213693952     /78 : 1125899906842624      /89 : 549755813888      /100 : 268435456
    # /68 : 1152921504606846976     /79 : 562949953421312       /90 : 274877906944      /101 : 134217728
    # /69 : 576460752303423488      /80 : 281474976710656       /91 : 137438953472      /102 : 67108864
    # /70 : 288230376151711744      /81 : 140737488355328       /92 : 68719476736       /103 : 33554432
    # /71 : 144115188075855872      /82 : 70368744177664        /93 : 34359738368       /104 : 16777216
    # /72 : 72057594037927936       /83 : 35184372088832        /94 : 17179869184       /105 : 8388608
    # /73 : 36028797018963968       /84 : 17592186044416        /95 : 8589934592        /106 : 4194304
    # /74 : 18014398509481984       /85 : 8796093022208         /96 : 4294967296        /107 : 2097152
    # /75 : 9007199254740992        /86 : 4398046511104         /97 : 2147483648        /108 : 1048576
    # /76 : 4503599627370496        /87 : 2199023255552         /98 : 1073741824        /109 : 524288
    #
    # /110 : 262144     /122 : 64
    # /111 : 131072     /123 : 32
    # /112 : 65536      /124 : 16
    # /113 : 32768      /125 : 8
    # /114 : 16384      /126 : 4
    # /115 : 8192       /127 : 2
    # /116 : 4096       /128 : 1
    # /117 : 2048
    # /118 : 1024
    # /119 : 512
    # /120 : 256
    # /121 : 128
    # ========================================================================
