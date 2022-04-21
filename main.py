from importlib.resources import path
from flask import Flask, render_template, request, session, redirect, flash, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json
import os
import math
from datetime import datetime
import glob


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.realpath(__file__))+'/upload'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pptx','docx','xlsx']

@app.route("/", methods=['GET', 'POST'])
def home():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method=='POST':
            f = request.files['file']
            file = glob.glob(app.config['UPLOAD_FOLDER']+"/*.*")
            file = [os.path.split(x)[1] for x in file]
            if f.filename == '':
                flash('No selected file.')
            elif allowed_file(f.filename):
                if secure_filename(f.filename) in file:
                    flash ("File with same name already exists, please change the name.")
                else:
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
                    flash ('Uploaded successfully!')
            else:
                flash("Only pptx, docx & xlsx file extensions allowed")
        return render_template('upload.html')

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            #set the session variable
            session['user'] = username
            return render_template('upload.html')

    return render_template('login.html')


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    return redirect(url_for('home'))


@app.route("/download", methods=['GET', 'POST'])
def download():
    files = glob.glob(app.config['UPLOAD_FOLDER']+"/*.*")
    files = [os.path.split(x)[1] for x in files]
    if ('user' in session and session['user'] == params['admin_user']):
        return render_template('download.html',files=files)

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            #set the session variable
            session['user'] = username
            return render_template('download.html',files=files)

    return render_template('login.html')


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def downloadfile(filename):
    # Returning file from appended path
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=filename)


@app.route("/login", methods=['GET', 'POST'])
def login():
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect(url_for('home'))

app.run(debug=True)
