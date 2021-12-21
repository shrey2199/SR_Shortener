import time
import requests
import os

WEB_URL = os.environ.get('WEBSITE_URL', '')

if len(WEB_URL) == 0:
    WEB_URL = None

if WEB_URL is not None:
    while True:
        time.sleep(600)
        status = requests.get(WEB_URL).status_code