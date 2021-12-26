from main import app
from flask import request, jsonify, render_template, redirect, url_for, session
import psycopg2
from config import Config
from random import *
from helpers.database import db_check_api, db_get_urls_by_api

# DATABASE
DATABASE_URI = Config.DATABASE_URI
conn = psycopg2.connect(DATABASE_URI)
cur = conn.cursor()

# JSONIFY urls
def jsonify_urls(urls):
    urls_json = []
    for url in urls:
        urls_json.append({
            'account_id': url[1],
            'url': url[3],
            'shorturl': url[4],
            'date-time': url[2],
            'visits': url[5]
        })
    return urls_json

# http://localhost:5000/api/myurls - this will be the MyURLs endpoint for the API
@app.route('/api/myurls', methods=['GET'])
def api_myurls():
    if 'api' in request.form:
        # Check if API is valid
        if db_check_api(request.form['api']):
            # API is valid
            urls = jsonify_urls(db_get_urls_by_api(request.form['api']))
            res = {'success': True, 'urls': urls}
            return jsonify(res)
        else:
            # API is not valid
            res = {'success': False, 'message': f"API Key {request.form['api']} is not valid !", 'status': 'api not valid'}
            return jsonify(res)
    else:
        res = {'success': True, 'status': 'active', 'message': 'This is The API Endpoint of The Shorten URL Service'}
        return jsonify(res)