#settings.py

import os

LOGGLY_API_KEY = '[API_KEY]'

# Dev server settings
LOGGLY_APP_NAME = 'hub.dev'
ENFORCE_AUTH = False
DEV_SERVER = True


if os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine'):
    # Production server settings
    LOGGLY_APP_NAME = 'hub.prod'
    ENFORCE_AUTH = False    # set this to tru to enforce auth on produciton
    DEV_SERVER = False



