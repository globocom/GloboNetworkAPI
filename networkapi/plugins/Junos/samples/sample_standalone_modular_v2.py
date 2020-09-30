"""
Use example:
python networkapi/plugins/Junos/samples/sample_standalone_modular_v2.py -device 'HOST' -user 'SSH_USER' -password 'SSH_USER_PASSWORD'
"""

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, ConfigLoadError, LockError, UnlockError, ConnectClosedError
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-device', help='Input host name', type=str)
parser.add_argument('-user', help='Input user name', type=str)
parser.add_argument('-password', help='Input password', type=str)
args, unknown = parser.parse_known_args()


class Junos:

    def __init__(self, device, username, password):

        self.device = device
        self.username = username
        self.password = password
        self.remote_conn = Device(host=device, user=username, password=password, gather_facts=False)
        self.configuration = Config(self.remote_conn)

    def connect(self):
        try:
            self.remote_conn.open()
        except ConnectError as e:
            print("Cannot connect: {0}".format(e))
        except Exception, e:
            print("An error occurred to connect: {0}".format(e))

    def exec_command(self, command):
        print("\tLocking configuration ...")
        self._lock_configuration()

        print("\tLoad configuration ...")
        self._load_configuration(data=command, format_type='set')

        print("\tCommit ...")
        self._commit()

        print("\tUnlocking configuration ...")
        self._unlock_configuration()

    def close(self):
        try:
            self.remote_conn.close()
        except ConnectClosedError, e:
            print("Cannot close connection: {0}".format(e))
        except Exception, e:
            print("An error occurred to close connect: {0}".format(e))

    def _load_configuration(self, data, format_type):
        # Ps.: If syntax error found, it will be excepted here
        try:
            self.configuration.load(data, format=format_type)
        except ConfigLoadError as err:
            print("Cannot load configuration: {0}".format(err))
            self.close()
        except Exception, e:
            print("An error occurred to load configuration: {0}".format(e))

    def _lock_configuration(self):
        try:
            # Guarantee a clean configuration (lock then clean)
            self.configuration.lock()
            self.configuration.rollback()
        except LockError as err:
            print("Unable to lock configuration: {0}".format(err))
            self.close()
        except Exception, e:
            print("An error occurred to lock configuration: {0}".format(e))

    def _unlock_configuration(self):
        try:
            self.configuration.unlock()
        except UnlockError as e:
            print("Unable to unlock configuration: {0}".format(e))
            self.close()
        except Exception, e:
            print("An error occurred to unlock configuration: {0}".format(e))

    def _commit(self):
        try:
            if self.configuration.commit_check():
                self.configuration.commit()
            else:
                self.configuration.rollback()
                print("An error occurred on commit configuration")
                raise Exception
        except Exception, e:
            print("An error occurred to commit configuration: {0}".format(e))


def main(device, username, password):

    plugin = Junos(device, username, password)

    print("Open connection ...")
    plugin.connect()  # In the future, the connect function will send an equipment (to validate maintenance)

    print("Execute configuration ...")
    plugin.exec_command(command='set interfaces gr-0/0/0 description "Some description 8 for gr-0/0/0"')

    print("Close connection ...")
    plugin.close()


if __name__ == "__main__":
    main(args.device, args.user, args.password)

