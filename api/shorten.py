from main import app
from flask import request, jsonify, render_template, redirect, url_for, session
import psycopg2
from config import Config
import re
from random import *
from helpers.database import db_add_url_by_api, db_check_api, db_add_url_by_id

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# DATABASE
DATABASE_URI = Config.DATABASE_URI
conn = psycopg2.connect(DATABASE_URI)
cur = conn.cursor()

# http://localhost:5000/shorten - this will be the shortener endpoint, only accessible for loggedin users
@app.route('/shorten', methods=['GET', 'POST'])
def shorten():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        if request.method == 'POST' and 'url' in request.form:
            url = request.form['url']

            # Check if API is valid
            if db_check_api(request.form['api']):
                # Check if url is valid
                if re.match(r'^(?:http|ftp)s?://', url) is not None:
                    # Check if url is already in database
                    cur.execute('SELECT * FROM urls WHERE url = %s', (url,))
                    url_in_db = cur.fetchone()
                    if url_in_db:
                        # URL is already in database
                        return render_template('home.html',msg="---- URL Already Shortened ----", url=f"{Config.WEBSITE_URL}/{url_in_db[4]}", api_key=session['api'])
                    else:
                        if request.form['shorturl'] == "":
                            # Generate random short url
                            shorturl = ''.join(choice(charset) for i in range(6))
                            # Insert url into database
                            db_add_url_by_id(session['id'], url, shorturl)
                            # Redirect to home page
                            return render_template('home.html', msg="----- URL Shortened -----", url=f"{Config.WEBSITE_URL}/{shorturl}", api_key=session['api'])
                        else:
                            # Check if shorturl is already in database
                            cur.execute('SELECT * FROM urls WHERE shorturl = %s', (request.form['shorturl'],))
                            shorturl_in_db = cur.fetchone()
                            if shorturl_in_db:
                                # Shorturl is already in database
                                return render_template('home.html', msg="--- Short URL Already Taken ---", url=f"{Config.WEBSITE_URL}/{shorturl_in_db[4]}", api_key=session['api'])
                            else:
                                # Insert url into database
                                db_add_url_by_id(session['id'], url, request.form['shorturl'])
                                # Redirect to home page
                                return render_template('home.html', msg="----- URL Shortened -----", url=f"{Config.WEBSITE_URL}/{request.form['shorturl']}", api_key=session['api'])
                else:
                    # URL is not valid
                    return render_template('home.html', url=url, msg='------ Invalid URL ------', api_key=session['api'])
            else:
                # API is not valid
                return f"API Key {request.form['api']} is not valid !"
        else:
            # Show form to enter url
            return render_template('home.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/api/shorten - this will be the shorten endpoint of api
@app.route('/api/shorten', methods=['GET', 'POST'])
def apishorten():
    if request.method == 'POST' and 'url' in request.form:
        url = request.form['url']

        # Check if API is valid
        if db_check_api(request.form['api']):
            # Check if url is valid
            if re.match(r'^(?:http|ftp)s?://', url) is not None:
                # Check if url is already in database
                cur.execute('SELECT * FROM urls WHERE url = %s', (url,))
                url_in_db = cur.fetchone()
                if url_in_db:
                    # URL is already in database
                    res = {'success': False, 'status': 'already shortened', 'message': 'URL Already Shortened !', 'shortened_url': f"{Config.WEBSITE_URL}/{url_in_db[4]}"}
                    return jsonify(res)
                else:
                    if request.form['shorturl'] == "":
                        # Generate random short url
                        shorturl = ''.join(choice(charset) for i in range(6))
                        # Insert url into database
                        db_add_url_by_api(request.form['api'], url, shorturl)
                        # Response
                        res = {'success': True, 'status': 'shortened', 'message': 'URL Shortened !', 'shortened_url': f"{Config.WEBSITE_URL}/{shorturl}"}
                        return jsonify(res)
                    else:
                        # Check if shorturl is already in database
                        cur.execute('SELECT * FROM urls WHERE shorturl = %s', (request.form['shorturl'],))
                        shorturl_in_db = cur.fetchone()
                        if shorturl_in_db:
                            # Shorturl is already in database
                            res = {'success': False, 'status': 'keyword taken', 'message': 'Short URL Already Taken !', 'shortened_url': f"{Config.WEBSITE_URL}/{shorturl_in_db[4]}"}
                            return jsonify(res)
                        else:
                            # Insert url into database
                            db_add_url_by_api(request.form['api'], url, request.form['shorturl'])
                            # Response
                            res = {'success': True, 'status': 'shortened', 'message': 'URL Shortened !', 'shortened_url': f"{Config.WEBSITE_URL}/{request.form['shorturl']}"}
                            return jsonify(res)
            else:
                # URL is not valid
                res = {'success': False, 'status': 'invalid url', 'message': 'Invalid URL !'}
                return jsonify(res)
        else:
            # API is not valid
            res = {'success': False, 'status': 'api not valid', 'message': f"API Key {request.form['api']} is not valid"}
            return jsonify(res)
    else:
        res = {'success': True, 'status': 'active', 'message': 'This is The API Endpoint of The Shorten URL Service'}
        return jsonify(res)