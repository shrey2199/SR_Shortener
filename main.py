# -*- coding: utf-8 -*-

import re
from flask import Flask, render_template, request, redirect, url_for, session
from flask_talisman import Talisman
import psycopg2
from urllib.parse import quote
from config import Config
from random import *
from helpers.database import db_register

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

app = Flask(__name__)
Talisman(app, content_security_policy=None)
app.secret_key = 'jkshefdhvjshvdf9w8erwuerhv'

# Import Routes
from api import shorten
from api import delete

# DATABASE
DATABASE_URI = Config.DATABASE_URI
conn = psycopg2.connect(DATABASE_URI)
cur = conn.cursor()

# http://localhost:5000/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
        # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'], api_key=session['api'])
    else:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username" and "password" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']

            cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
            account = cur.fetchone()
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[1]
                session['username'] = account[3]
                session['api'] = account[5]
                # Redirect to home page
                return render_template('home.html', username=session['username'], api_key=session['api'])
            else:
                # Account doesn't exist or username/password incorrect
                msg = 'Incorrect username/password!'
        return render_template('index.html', msg=msg)

# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('api', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'], api_key=session['api'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:

        # We need all the account info for the user so we can display it on the profile page
        cur.execute('SELECT * FROM accounts WHERE username = %s', (session['username'],))
        account = cur.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/myurls - this will be the my urls page, only accessible for loggedin users
@app.route('/myurls')
def myurls():
    # Check if user is loggedin
    if 'loggedin' in session:
        
        cur.execute('SELECT * FROM urls WHERE tg_id = %s', (session['id'],))
        myurls = cur.fetchall()
        url_list = [list(row) for row in myurls]

        # Show the myurls page with myurls table
        return render_template('myurls.html', myurls=url_list, root_url=Config.WEBSITE_URL, username=session['username'], api_key=session['api'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Redirect Route - http://localhost:5000/<shorturl> - this will be the short url redirect
@app.route('/<shorturl>')
def redirect_shorturl(shorturl):
    cur.execute('SELECT url FROM urls WHERE shorturl = %s', (shorturl,))
    url = cur.fetchone()
    if url:
        # URL is valid, redirect to long url
        return redirect(url[0])
    else:
        # URL is not valid, show error page
        return f"<h1>URL not found</h1><p>The URL you are looking for does not exist.</p>"

# Registration Route - http://localhost:5000/register - this will be the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "name" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'name' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']

        # Check if account exists using MySQL
        cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cur.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Username Already Taken!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not name:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            db_register(username, password, name)
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# Admin Route - http://localhost:5000/admin - this will be the admin page
@app.route('/admin')
def admin():
    # Show Admin Login page
    return render_template('admin.html')

# Admin Home Route - http://localhost:5000/admin/home - this will be the admin home page
@app.route('/admin/home', methods=['GET', 'POST'])
def admin_home():
        # Check if admin is loggedin
    if 'admin_loggedin' in session:
        # User is loggedin show them the home page
        return render_template('admin_home.html', api_key=session['admin_api'])
    else:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username" and "password" POST requests exist (user submitted form)
        if request.method == 'POST' and 'admin_pass' in request.form:
            # Create variables for easy access
            admin_pass = request.form['admin_pass']

            if admin_pass == Config.ADMIN_PASS:
                # Create session data for admin
                session['admin_loggedin'] = True
                session['admin_api'] = Config.UNIVERSAL_API

                # Redirect to admin home page
                return render_template('admin_home.html', api_key=session['admin_api'])
            else:
                # Account doesn't exist or username/password incorrect
                msg = 'Incorrect Password !'
        return render_template('admin.html', msg=msg)

# Admin Accounts Route - http://localhost:5000/admin/accounts - this will be the admin accounts page
@app.route('/admin/accounts')
def admin_accounts():
    # Check if admin is loggedin
    if 'admin_loggedin' in session:
        # We need all the account info for all users so we can display it on the accounts page
        cur.execute('SELECT * FROM accounts')
        accounts = cur.fetchall()
        acc_list = [list(row) for row in accounts]
        # Show the profile page with account info
        return render_template('admin_accounts.html', accounts=acc_list)
    # User is not loggedin redirect to login page
    return redirect(url_for('admin_login'))

# DEBUG SERVER
if __name__ == '__main__':
    app.run(debug=True, port=5000)