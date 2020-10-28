"""
Use example:
python networkapi/plugins/Juniper/JUNOS/samples/sample_standalone.py -device 'HOST' -user 'SSH_USER' -password 'SSH_USER_PASSWORD'
"""

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, ConfigLoadError, LockError, UnlockError, ConnectClosedError, CommitError
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-device', help='Input host name', type=str)
parser.add_argument('-user', help='Input user name', type=str)
parser.add_argument('-password', help='Input password', type=str)
args, unknown = parser.parse_known_args()

device = args.device
user = args.user
password = args.password

print("Open connection ...")
dev = Device(host=device, user=user, password=password, gather_facts=False)
dev.open()

print("Load config  ...")
conf = Config(dev)

print("Locking config ...")
conf.lock()

print("Rollback config ...")
conf.rollback()

data = 'set interfaces gr-0/0/0 description "Some description sample standalone for gr-0/0/0"'
conf.load(data, format='set')  # syntax error raises exception

print("Check  ...")
conf.commit_check()

print("Commit  ...")
conf.commit()

print("Unlocking config ...")
conf.unlock()

print("Close connection ... ")
dev.close()

print ("DONE")
