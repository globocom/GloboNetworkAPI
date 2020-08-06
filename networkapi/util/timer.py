import logging
from time import time

log = logging.getLogger(__name__)

class Timer():
    def __init__(self, debug_msg=None):
        self._start = time()
        self._laps = []
        self._last_lap = self._start
        self._stopped = 0
        if debug_msg:
            log.debug(debug_msg)
    def lap(self, debug_msg=None):
        self._last_lap = time()-self._start
        self._laps.append(self._last_lap)
        if debug_msg:
            log.debug(debug_msg)
        return self._last_lap
    def elapsed_time(self, debug_msg=None):
        total_time = time()-self._start
        if debug_msg:
            log.debug(debug_msg)
        return total_time
    def laps():
        return self._laps
    def last_lap():
        return self._last_lap
    def reset(self, debug_msg=None):
        self.__init__(debug_msg)