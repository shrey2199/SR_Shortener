from main import app
from flask import request, jsonify, render_template, redirect, url_for, session
import psycopg2
from config import Config
import re
from random import *
from helpers.database import db_check_api, db_get_urls_by_id

# DATABASE
DATABASE_URI = Config.DATABASE_URI
conn = psycopg2.connect(DATABASE_URI)
cur = conn.cursor()

# http://localhost:5000/delete - this will be the delete endpoint, only accessible for loggedin users
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        if request.method == 'POST' and 'del_url' in request.form:
            url = request.form['del_url']

            # Check if API is valid
            if db_check_api(request.form['api']):
                # Check if shorturl is present in database
                cur.execute('SELECT * FROM urls WHERE shorturl = %s', (url,))
                url_in_db = cur.fetchone()
                if url_in_db:
                    # Delete url from database
                    cur.execute('DELETE FROM urls WHERE shorturl = %s', (url,))
                    conn.commit()
                    return render_template('myurls.html', msg="URL Deleted !", api_key=session['api'], myurls=db_get_urls_by_id(session['id']))
                else:
                    # URL is not present in database
                    return render_template('myurls.html', msg="URL Not Found !", api_key=session['api'], myurls=db_get_urls_by_id(session['id']))
            else:
                # API is not valid
                return f"API Key {request.form['api']} is not valid !"
        else:
            # User is loggedin show them the myurls page
            return render_template('myurls.html', api_key=session['api'], myurls=db_get_urls_by_id(session['id']))
    else:
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))

# http://localhost:5000/api/delete - this will be the delete endpoint of api
@app.route('/api/delete', methods=['GET', 'POST'])
def apidelete():
    if request.method == 'POST' and 'del_url' in request.form:
        url = request.form['del_url']

        # Check if API is valid
        if db_check_api(request.form['api']):
            # Check if shorturl is present in database
            cur.execute('SELECT * FROM urls WHERE shorturl = %s', (url,))
            url_in_db = cur.fetchone()
            if url_in_db:
                # Delete url from database
                cur.execute('DELETE FROM urls WHERE shorturl = %s', (url,))
                conn.commit()
                res = {'success': True, 'message': 'URL Deleted !', 'status': 'url deleted'}
                return jsonify(res)
            else:
                # URL is not present in database
                res = {'success': False, 'message': 'URL Not Found !', 'status': 'url not found'}
                return jsonify(res)
        else:
            # API is not valid
            res = {'success': False, 'message': f"API Key {request.form['api']} is not valid !", 'status': 'api not valid'}
            return jsonify(res)
    else:
        res = {'success': True, 'status': 'active', 'message': 'This is The API Endpoint of The Shorten URL Service'}
        return jsonify(res)