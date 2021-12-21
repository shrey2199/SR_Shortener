from config import Config
import psycopg2
from datetime import datetime
import pytz
from random import *

# CONFIG
from config import Config

DATABASE_URI = Config.DATABASE_URI

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

'''DATABASE FUNCTIONS'''

def db_get_urls_by_id(id):
    '''Connecting with URI'''
    conn = psycopg2.connect(DATABASE_URI)

    '''Creating Cursor'''
    cur = conn.cursor()

    '''Fetch Data From Table'''
    cmd = f"SELECT * FROM urls WHERE tg_id = '{id}'"
    cur.execute(cmd)
    rows = cur.fetchall()
    rows_list = [list(row) for row in rows]

    '''Close Cursor'''
    cur.close()

    return rows_list

def db_createtable():
    '''Connecting with URI'''
    conn = psycopg2.connect(DATABASE_URI)

    '''Creating Cursor'''
    cur = conn.cursor()

    '''Create A Table accounts'''
    cmd = "create table if not exists accounts(serial_id SERIAL PRIMARY KEY, tg_id VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL, username VARCHAR, password VARCHAR, api VARCHAR, datetime VARCHAR)"
    cur.execute(cmd)
    conn.commit()

    '''Create A Table urls'''
    cmd = "create table if not exists urls(serial_id SERIAL , tg_id VARCHAR(255) NOT NULL, datetime VARCHAR, url VARCHAR, shorturl VARCHAR, views VARCHAR)"
    cur.execute(cmd)
    conn.commit()

    '''Close Cursor'''
    cur.close()

def db_register(username, password, name):
    dt = datetime.now(pytz.timezone('Asia/Kolkata'))

    '''Connecting with URI'''
    conn = psycopg2.connect(DATABASE_URI)

    '''Creating Cursor'''
    cur = conn.cursor()

    '''Insert Data In Table'''
    api_key = "".join(choice(charset) for x in range(randint(10, 15)))
    tg_id = "".join(choice(username+password) for x in range(randint(10, 15)))
    cmd = "INSERT INTO accounts(tg_id, name, username, password, api, datetime) VALUES(%s,%s,%s,%s,%s,%s)"
    cur.execute(cmd, (tg_id, name, username, password, api_key, str(dt)))
    conn.commit()

    '''Close Cursor'''
    cur.close()

def db_get_api(id):
    '''Connecting with URI'''
    conn = psycopg2.connect(DATABASE_URI)

    '''Creating Cursor'''
    cur = conn.cursor()

    '''Fetch Data From Table'''
    cmd = f"SELECT api FROM accounts WHERE tg_id = '{id}'"
    cur.execute(cmd)
    rows = cur.fetchone()

    '''Close Cursor'''
    cur.close()

    return rows[0]

def db_check_api(api):
    '''Connecting with URI'''
    conn = psycopg2.connect(DATABASE_URI)

    '''Creating Cursor'''
    cur = conn.cursor()

    '''Fetch Data From Table'''
    cmd = f"SELECT api FROM accounts WHERE api = '{api}'"
    cur.execute(cmd)
    rows = cur.fetchall()
    rows_list = [list(row) for row in rows]

    '''Close Cursor'''
    cur.close()

    '''Return Values'''
    if len(rows_list) != 0:
        return 1
    else:
        return 0

def db_add_url_by_api(api, url, shorturl):
    dt = datetime.now(pytz.timezone('Asia/Kolkata'))

    '''Connecting with URI'''
    conn = psycopg2.connect(DATABASE_URI)

    '''Creating Cursor'''
    cur = conn.cursor()
    
    '''Fetch Data From Table'''
    cmd = f"SELECT tg_id FROM accounts WHERE api = '{api}'"
    cur.execute(cmd)
    rows = cur.fetchone()

    tg_id = rows[0]

    '''Close Cursor'''
    cur.close()

    '''Creating Cursor'''
    cur = conn.cursor()  

    '''Insert Data In Table'''
    cmd = "INSERT INTO urls(tg_id, datetime, url, shorturl, views) VALUES(%s,%s,%s,%s,%s)"
    cur.execute(cmd, (tg_id, str(dt), str(url), str(shorturl), 0))
    conn.commit()

    '''Close Cursor'''
    cur.close()

def db_add_url_by_id(id, url, shorturl):
    dt = datetime.now(pytz.timezone('Asia/Kolkata'))
    
    tg_id = id

    '''Connecting with URI'''
    conn = psycopg2.connect(DATABASE_URI)

    '''Creating Cursor'''
    cur = conn.cursor()

    '''Insert Data In Table'''
    cmd = "INSERT INTO urls(tg_id, datetime, url, shorturl, views) VALUES(%s,%s,%s,%s,%s)"
    cur.execute(cmd, (tg_id, str(dt), str(url), str(shorturl), 0))
    conn.commit()

    '''Close Cursor'''
    cur.close()