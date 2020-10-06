"""
Use example:
python networkapi/plugins/Juniper/JUNOS/samples/sample_standalone_responses.py -device 'HOST' -user 'SSH_USER' -password 'SSH_USER_PASSWORD'
"""

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, ConfigLoadError
from lxml import etree
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

try:

    print("\nOpen connection ... dev.open()")
    dev = Device(host=device, user=user, password=password, gather_facts=False)
    open_result = dev.open()
    print(open_result.connected)  # True/False

    conf = Config(dev)
    data = 'set interfaces gr-0/0/0 description "Some description 3 for gr-0/0/0"'

    print("\nLock configuration ... conf.lock();")
    lock_response = conf.lock()
    print(lock_response)

    print("\nRollback configuration ... conf.rollback()")
    rollback_response = conf.rollback()  # True/False
    print(rollback_response)

    print("\nLoad configuration ... conf.load(data")
    load_result = conf.load(data, format='set')
    print(etree.tostring(load_result, encoding='unicode', pretty_print=True))  # XML

    print("Commit check configuration ... conf.commit_check()")
    commit_check_result = conf.commit_check()
    print(commit_check_result)  # True/False

    print("\nCommit configuration ... conf.commit()")
    commit_result = conf.commit()
    print(commit_result)  # True/False

    print("\nUnlock configuration  ... conf.unlock()")
    unlock_response = conf.unlock()
    print(unlock_response)

    print("\nClose connection ... .close()")
    close_response = dev.close()
    print(close_response)  # None
    # print(open_result.connected)  # False/True

except ConnectError as err:
    print("Cannot connect to device: {0}".format(err))
    dev.close()
except ConfigLoadError as err:
    print("Cannot load configuration: {0}".format(err))
    dev.close()
except Exception as err:
    print("Some error occurred: {0}".format(err))
    dev.close()
