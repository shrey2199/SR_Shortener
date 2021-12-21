# -*- coding: utf-8 -*-

from helpers.database import db_createtable
import subprocess

# DATABASE
db_createtable()

# SUBPROCESS
alive = subprocess.Popen(['python3', 'alive.py'])

# Stop Python File From Closing
while True:
    pass