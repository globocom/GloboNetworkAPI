import logging
from time import time

log = logging.getLogger(__name__)


class Timer():
    def __init__(self, debug_msg=None):
        self._start = time()
        self._laps = []
        self._last_lap = 0
        self._lap_control = self._start
        self._stopped = 0
        if debug_msg:
            log.debug(debug_msg)

    def lap(self, debug_msg=None):
        curr_time = time()
        self._last_lap = curr_time-self._lap_control
        self._lap_control = curr_time
        self._laps.append(self._last_lap)
        if debug_msg:
            log.debug(debug_msg)
        return self._last_lap

    def elapsed_time(self, debug_msg=None):
        total_time = time()-self._start
        if debug_msg:
            log.debug(debug_msg)
        return total_time

    def laps(self):
        return self._laps

    def last_lap(self):
        return self._last_lap

    def reset(self, debug_msg=None):
        self.__init__(debug_msg)
