"""
Use example:
python networkapi/plugins/Junos/samples/sample_standalone.py -device 'HOST' -user 'SSH_USER' -password 'SSH_USER_PASSWORD'
"""

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, ConfigLoadError, ConnectClosedError
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-device', help='Input host name', type=str)
parser.add_argument('-user', help='Input user name', type=str)
parser.add_argument('-password', help='Input password', type=str)
args, unknown = parser.parse_known_args()

device = args.device
user = args.user
password = args.password

dev = None
conf = None

print ("Open connection ...")
try:
    dev = Device(host=device, user=user, password=password, gather_facts=False)
    dev.open()
except ConnectError as err:
    print("Cannot connect: {0}".format(err))
    exit()

print ("Load configuration ...")
try:
    conf = Config(dev)
    data = 'set interfaces gr-0/0/0 description "Some description 3 for gr-0/0/0"'
    conf.load(data, format='set')  # If has syntax error it will be catch and connection will be closed
except ConfigLoadError as err:
    print("Cannot load configuration: {0}".format(err))
    dev.close()
    exit()

print ("Check and commit configuration ...")
try:
    if conf.commit_check():
        conf.commit()
    else:
        print("Error - rollback configuration")
        conf.rollback()
except Exception as err:
    print("Some error occurred: {0}".format(err))

print ("Close connection ...")
try:
    dev.close()
except ConnectClosedError as err:
    print("Unable to close connection: {0}".format(err))

print ("DONE")

