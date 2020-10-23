"""
How to use:
python sample_command_line.py -device 'HOST' -user 'SSH_USER_NAME' -password 'SSH_USER_PASSWORD' -command 'COMMAND'
"""

from lxml import etree
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-device', help='Input host', type=str)
parser.add_argument('-user', help='Input user name', type=str)
parser.add_argument('-password', help='Input password', type=str)
parser.add_argument('-command', help='Input command', type=str)
args, unknown = parser.parse_known_args()

device = args.device
user = args.user
password = args.password
command = args.command

try:

    dev = Device(host=device, user=user, password=password, gather_facts=False)
    open_result = dev.open()
    print("Open connection ... {}".format(open_result.connected))

    conf = Config(dev)
    print("Load config  ...")

    lock_response = conf.lock()
    print("Locking config ... {}".format(lock_response))

    rollback_response = conf.rollback()
    print("Rollback config ... {}".format(rollback_response))

    load_result = conf.load(command, format='set')
    load_result_tostring = etree.tostring(load_result, encoding='unicode', pretty_print=True)
    print("Load command ... \n{}".format(load_result_tostring))

    commit_check_result = conf.commit_check()
    print("Check result ... {}".format(commit_check_result))

    commit_result = conf.commit()
    print("Commit  ... {}".format(commit_result))

    unlock_response = conf.unlock()
    print("Unlocking config ... {}".format(unlock_response))

    close_response = dev.close()
    print("Close connection ... {}".format("Success" if not open_result.connected else "Failed"))

    print ("DONE")

except Exception, e:

    print(e)
    close_response = dev.close()
    print("Closed connection? {}".format(not open_result.connected))
