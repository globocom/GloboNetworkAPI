# encoding: utf-8
import time
import uuid
from networkapi.log import Log

log = Log('MemcachedLock')

__all__ = ['MemcachedLock']


class MemcachedLock(object):

    """
    Try to do same as threading.Lock, but using Memcached to store lock instance to do a distributed lock
    """

    def __init__(self, key, client, timeout=60):
        self.key = "lock:%s" % key
        self.client = client
        self.timeout = timeout

        # When you use threading.Lock object, instance references acts as ID of the object. In memcached
        # we have a key to identify lock, but to identify which machine/instance/thread has lock is necessary
        # put something in memcached value to identify it. So, each MemcachedLock instance has a random value to
        # identify who has the lock
        self.instance_id = uuid.uuid1().hex

    def acquire(self, blocking=True):
        while True:
            added = self.client.add(self.key, self.instance_id, self.timeout)
            log.warning("Added=%s" % repr(added))
            if added:
                break

            if added == 0 and not (added is False):
                raise RuntimeError(
                    u"Error calling memcached add! Is memcached up and configured? memcached_client.add returns %s" %
                    repr(added))

            if not blocking:   # and not added
                return False

            log.warning('Waiting locking for "%s"', self.key)
            time.sleep(1)
        return True

    def release(self):
        value = self.client.get(self.key)
        if value == self.instance_id:
            # Avoid short timeout, because if key expires, after GET, and another lock occurs, memcached remove
            # below can delete another lock! There is no way to solve this in
            # memcached
            self.client.delete(self.key)
        else:
            log.warning(
                "I've no lock to release. Increase TIMEOUT of lock operations")
