import re


class LoggingMiddleware(object):

    def process_exception(self, request, exception):
        """ HIDE PASSWORD VALUES"""

        # Get POST value
        post_values = request.POST.copy()

        for values in post_values:
            r = re.compile('<password>(.*?)</password>')
            m = r.search(post_values[values])
            if m:
                password = m.group(1)
                msg = re.sub(password, "****", post_values[values])

            post_values[values] = msg

        request.POST = post_values

        if(post_values.has_key('password')):

            # Change PASSWORD value to '*'
            post_values['password'] = '****'
            request.POST = post_values

        # Get META value
        meta_values = request.META.copy()

        if(meta_values.has_key('HTTP_NETWORKAPI_PASSWORD')):

            # Change HTTP_NETWORKAPI_PASSWORD value to '*'
            meta_values['HTTP_NETWORKAPI_PASSWORD'] = '****'
            request.META = meta_values
