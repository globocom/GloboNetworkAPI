import hashlib
import logging

from django.core.cache import cache as memcache

from networkapi.distributedlock import distributedlock

log = logging.getLogger(__name__)


DEFAULT_CACHE_TIMEOUT = 86400

ENVIRONMENT_CACHE_ENTRY = "CACHE_ENV_LIST"


def get_cached_search(prefix, search):

    try:
        search_md5 = hashlib.md5(str(search)).hexdigest()
        key = prefix+search_md5
        data = memcache.get(key)
        if data:
            log.debug("Got cached data for key %s" % key)
        return data
    except Exception as e:
        log.error(e)
        return None


def set_cache_search_with_list(prefix, search, data, timeout=DEFAULT_CACHE_TIMEOUT):

    with distributedlock(prefix):
        try:
            search_md5 = hashlib.md5(str(search)).hexdigest()
            key = prefix+search_md5
            memcache.set(key, data, timeout)

            cached_search_md5_list = memcache.get(prefix)
            if not cached_search_md5_list:
                cached_search_md5_list = []

            if search_md5 not in cached_search_md5_list:
                cached_search_md5_list.append(search_md5)

            log.debug("Caching key %s in list %s ..." % (key, prefix))
            key = prefix
            memcache.set(key, cached_search_md5_list, timeout)
        except Exception as e:
            log.error(e)


def delete_cached_searches_list(prefix):

    with distributedlock(prefix):
        try:
            cached_search_md5_list = memcache.get(prefix)
            if cached_search_md5_list:
                for cached_search_md5 in cached_search_md5_list:
                    key = str(prefix)+str(cached_search_md5)
                    log.debug("Deleting cache entry %s ... " % key)
                    memcache.delete(key)
                log.debug("Deleting cache list entry %s ..." % prefix)
                memcache.delete(prefix)
        except Exception as e:
            log.error(e)
            raise e

        return True
