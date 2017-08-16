#!/bin/bash

# NETAPI_ODL

echo "Waiting for ODL to go up"

MAX_RETRY=18
SLEEP_TIME=10

for i in $(seq 1  ${MAX_RETRY}); do

    docker exec ovs1 ovs-vsctl show | grep is_connected > /dev/null

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

echo "ODL server is up"
