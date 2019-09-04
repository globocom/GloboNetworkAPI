import hashlib
import logging

from django.core.cache import cache as djangocache

from networkapi.distributedlock import distributedlock
from networkapi.system.facade import get_value


log = logging.getLogger(__name__)


DEFAULT_CACHE_TIMEOUT = 86400
ENVIRONMENT_CACHE_ENTRY = "CACHE_ENV_LIST"


def cache_enabled():
    try:
        if int(get_value('use_cache')):
            return 1
        return 0
    except Exception as e:
        return 0


def get_cached_search(prefix, search):

    if cache_enabled():
        try:
            search_md5 = hashlib.md5(str(search)).hexdigest()
            key = prefix+search_md5
            data = djangocache.get(key)
            if data:
                log.debug("Got cached data for key %s" % key)
            return data
        except Exception as e:
            log.error(e)
            return None


def set_cache_search_with_list(prefix, search, data, timeout=DEFAULT_CACHE_TIMEOUT):

    if cache_enabled():
        with distributedlock(prefix):
            try:
                search_md5 = hashlib.md5(str(search)).hexdigest()
                key = prefix+search_md5
                djangocache.set(key, data, timeout)

                cached_search_md5_list = djangocache.get(prefix)
                if not cached_search_md5_list:
                    cached_search_md5_list = []

                if search_md5 not in cached_search_md5_list:
                    cached_search_md5_list.append(search_md5)

                log.debug("Caching key %s in list %s with timeout %s..." %
                          (key, prefix, timeout))
                key = prefix
                djangocache.set(key, cached_search_md5_list, timeout)
            except Exception as e:
                log.error(e)


def delete_cached_searches_list(prefix):

    if cache_enabled():
        with distributedlock(prefix):
            try:
                cached_search_md5_list = djangocache.get(prefix)
                if cached_search_md5_list:
                    for cached_search_md5 in cached_search_md5_list:
                        key = str(prefix)+str(cached_search_md5)
                        log.debug("Deleting cache entry %s ... " % key)
                        djangocache.delete(key)
                    log.debug("Deleting cache list entry %s ..." % prefix)
                    djangocache.delete(prefix)
            except Exception as e:
                log.error(e)
                raise e

            return True
