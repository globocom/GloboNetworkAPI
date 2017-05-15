#!/bin/sh

#
# SCRIPT TO START AND CONFIGURE OPENVSWITCH
#

# Enables Job control
set -m;

# Sleep time for wait openvswitch ready state
SLEEP_TIME=10

# Runs openvswitch managed by supervisord as background process
/usr/bin/supervisord &

# Waits for openvswitch ready state, then add a bridge
sleep ${SLEEP_TIME} && ovs-vsctl add-br br0

# Remote controller IP address
REMOTE_CTRL=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $3}')

# Set remote controller
ovs-vsctl set-controller br0 tcp:${REMOTE_CTRL}:6653

# List openvswitch configuration
ovs-vsctl show

# List openvswitch flows
ovs-ofctl dump-flows br0;

# Bring supervisord to foreground
fg %1
