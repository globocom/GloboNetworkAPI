#!/bin/bash

#
# SCRIPT TO START OPENDAYLIGHT SDN CONTROLLER
#

# Sleep time to wait for ODL to start
SLEEP_TIME=20

# Enter the project directory
cd /opt/opendaylight/

# Runs ODL in background using Karaf
echo "Starting OpenDaylight.."
./bin/start

# Waits until ODL is up and running
sleep ${SLEEP_TIME}

# Attaches to Karaf client and install some features for ODL
echo "Installing features.."
./bin/client feature:install odl-restconf odl-l2switch-switch odl-dlux-all odl-netconf-connector-all odl-openflowplugin-flow-services

# Attaches to Karaf server as a foreground process
echo "Attaching on server.."
./bin/karaf server
