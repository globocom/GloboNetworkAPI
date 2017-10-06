# -*- coding: utf-8 -*-
"""
   Copyright 2017 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import logging
from functools import wraps

log = logging.getLogger(__name__)


########################################
# Decorators
########################################
def logger(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        log.info('%s.%s: %s,%s' %
                 (self.__class__.__name__, func.__name__, args, kwargs))
        return func(self, *args, **kwargs)

    return inner
