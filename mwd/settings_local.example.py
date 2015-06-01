DEBUG = False
TEMPLATE_DEBUG = DEBUG

PRE_REG = True
REG_ENABLED = True

FROM_EMAIL = "finance@madwreckindolls.com"
DEFAULT_FROM_EMAIL = "finance@madwreckindolls.com"

REGISTRATION_DEFAULT_STATUS = "active"
REGISTRATION_INACTIVE_STATUS = "inactive"

REGISTRATION_SESSION_NAME = "Spring 2015"
REGISTRATION_BILLING_PERIOD = 26
REGISTRATION_DEADLINE = "February 20th, 2015"

REGISTRATION_PIP_INSTRUCTIONS = "Find Audi at the rink and hand her cash, check or a credit card. You can also use the lockbox at the rink!"

REGISTRATION_MAIL_INSTRUCTIONS = """Mail or drop off your check/cash, made payable to Mad Wreckin' Dolls:<br>
<br>
Address Here?
"""


PAYMENT_PREFERENCES = (
        ("pip", "Pay in Person"),
        ("mail", "Mail"),
        ("cc", "Credit Card"),
    ("gratis", "No Payment"),
)


PAYMENT_METHODS = (
        ("cash", "Cash"),
        ("check", "Check"),
        ("square", "Credit Card (Square)"),
        ("credit", "Credit Card (Online)"),
)


# LIVE STRIPE KEYS
STRIPE_SECRET = "sk_live_"
STRIPE_PUBLISHABLE = "pk_live_"

ADMINS = (
        ('Dan Silvers', 'github@silvers.net'),
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS




CRISPY_TEMPLATE_PACK = "bootstrap"

TEMPLATE_DIRS = (
    "/home/vagrant/mwd/templates/"
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/home/vagrant/mwd.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/vagrant/mwd/media/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    '/home/vagrant/mwd/mwd/static/',
)
