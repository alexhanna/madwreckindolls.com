
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








# http://www.ironzebra.com/news/30/create-random-pronounceable-passwords-in-pythondjango
#
# adaption of:
# http://stackoverflow.com/questions/5501477/any-python-password-generators-that-are-readable-and-pronounceable
# originally written by Greg Haskins

import itertools

initial_consonants = (set(string.ascii_lowercase) - set('aeiou')
                      # remove those easily confused with others
                      - set('qxc')
                      # add some crunchy clusters
                      | set(['bl', 'br', 'cl', 'cr', 'dr', 'fl',
                             'fr', 'gl', 'gr', 'pl', 'pr', 'sk',
                             'sl', 'sm', 'sn', 'sp', 'st', 'str',
                             'sw', 'tr'])
                      )

final_consonants = (set(string.ascii_lowercase) - set('aeiou')
                    # confusable
                    - set('qxcsj')
                    # crunchy clusters
                    | set(['ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt',
                           'pt', 'sk', 'sp', 'ss', 'st'])
                    )

vowels = 'aeiou' # we'll keep this simple

# each syllable is consonant-vowel-consonant "pronounceable"
syllables = map(''.join, itertools.product(initial_consonants, 
                                           vowels, 
                                           final_consonants))

# you could throw in number combinations, maybe capitalized versions... 

def gibberish(wordcount, wordlist=syllables):
    return random.sample(wordlist, wordcount)
    
def get_pronounceable_password(wordcount=2, digitcount=2):
    numbermax = 10 ** digitcount
    password = ''.join(gibberish(wordcount))
    if digitcount >= 1:
        password += str(int(random.random()*numbermax))
    return password
