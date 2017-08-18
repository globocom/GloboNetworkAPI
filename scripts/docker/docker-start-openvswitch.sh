#
# SCRIPT TO START AND CONFIGURE OPENVSWITCH
#

# Enables Job control
set -m;

# Sleep time to wait for ODL to start
SLEEP_TIME=5

# Maximum retry attempts
MAX_RETRY=30

# Runs openvswitch managed by supervisord as background process
/usr/bin/supervisord &

# Waits for openvswitch ready state, then add a bridge
sleep ${SLEEP_TIME} && ovs-vsctl add-br br0

# Remote controller IP address
REMOTE_CTRL=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $3}')

echo "Setting remote controller..."
ovs-vsctl set-controller br0 tcp:${REMOTE_CTRL}:6653

echo "Setting remote manager..."
ovs-vsctl set-manager tcp:${REMOTE_CTRL}:6633

# List openvswitch configuration
ovs-vsctl show

# Bring supervisord to foreground
fg %1
