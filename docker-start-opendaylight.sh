#!/bin/bash

#
# SCRIPT TO START OPENDAYLIGHT SDN CONTROLLER
#

# Sleep time to wait for ODL to start
SLEEP_TIME=20

# Enter the project directory
cd /odl/distribution-karaf-0.5.0-Boron

# Runs ODL in background using Karaf
./bin/start

# Waits until ODL is up and running
sleep ${SLEEP_TIME}

# Attaches to Karaf client and install some features for ODL
./bin/client feature:install odl-restconf odl-l2switch-switch odl-dlux-all odl-netconf-connector-all odl-openflowplugin-flow-services

# Attaches to Karaf server as a foreground process
./bin/karaf server
