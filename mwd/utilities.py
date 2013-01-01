
""" http://stackoverflow.com/a/4581997 """

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


""" http://stackoverflow.com/a/9011133 """

import random
import string

def random_string(length):
    pool = string.letters + string.digits
    return ''.join(random.choice(pool) for i in xrange(length))
