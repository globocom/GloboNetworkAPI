#!/bin/sh

#
# SCRIPT TO START AND CONFIGURE OPENVSWITCH
#

# Enables Job control
set -m;

# Maximum retry attempts
MAX_RETRY=30

# Sleep time for wait openvswitch ready state
SLEEP_TIME=10

# Runs openvswitch managed by supervisord as background process
/usr/bin/supervisord &

# Waits for openvswitch ready state, then add a bridge
sleep ${SLEEP_TIME} && ovs-vsctl add-br br0

# Remote controller IP address
REMOTE_CTRL=$(nslookup netapi_odl | grep Address | tail -1 | awk '{print $3}')

# Waits until a port is open and ready for connections
for i in $(seq 1..${MAX_RETRY}); do

    (echo "e") | telnet ${REMOTE_CTRL} 6653

    # If the port is open we continue with the script
    if [ "$?" -eq "0" ]; then
        break;
    fi

    # When maximum retries is achieved we exit with an error message
    if [ "$i" -eq "${MAX_RETRY}" ]; then
        echo "Max retry achieved"
        exit 1;
    fi

    echo "Retrying ${i}.."
    sleep ${SLEEP_TIME}
done

# Set remote controller
ovs-vsctl set-controller br0 tcp:${REMOTE_CTRL}:6653

# List openvswitch configuration
ovs-vsctl show

# List openvswitch flows
ovs-ofctl dump-flows br0;

# Bring supervisord to foreground
fg %1
