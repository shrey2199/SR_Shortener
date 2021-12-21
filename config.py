import os
from urllib.parse import quote

class Config(object):
    DATABASE_URI = os.environ.get('DATABASE_URL', '')
    WEBSITE_URL = os.environ.get('WEBSITE_URL', '')
    ADMIN_PASS = os.environ.get('ADMIN_PASS', '')
    UNIVERSAL_API = os.environ.get('UNIVERSAL_API', '')