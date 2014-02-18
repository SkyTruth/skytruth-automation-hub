#settings.py

import os

LOGGLY_API_KEY = 'bcd529e8-5300-4681-b496-c4143b284016'
LOGGLY_APP_NAME = 'geofeed.dev'
ENFORCE_AUTH = False
DEV_SERVER = True


if os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine'):
    LOGGLY_APP_NAME = 'geofeed.prod'
    ENFORCE_AUTH = False
    DEV_SERVER = False



