# Basic flask app
import re
from datetime import datetime
from hashlib import sha256

from cfg import config
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   session,
                   )
from flask_pymongo import PyMongo
import pymongo
from util import get_random_string
import os

# Flask App Configuration
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MONGO_URI"] = config['mongo_URI']
app.config['UPLOAD_FOLDER'] = '/home/dj/Desktop/Placement/Projects/SafeDrive/Uploads'
app.secret_key = b'nkdnkjnwknwljfnwlfnf/'
mongo = PyMongo(app)


@app.route('/')
def index():
    if not 'userToken' in session:
        session['error'] = "You must login to access this page!"
        return redirect('/login')

    # Validate user Token
    tokenDoc = mongo.db.user_tokens.find_one({"sessionHash": session['userToken']})
    if tokenDoc is None:
        session.pop('userToken', None)
        session['error'] = "You must login again to access this page!"
        return redirect('/login')

    error = ''
    if 'error' in session:
        error = session['error']
        session.pop('error', None)

    userID = tokenDoc['userID']
    user = mongo.db.users.find_one({'_id': userID})

    #print("User ID of logged in user is",str(userID))
    uploaded_files = mongo.db.files.find({'userID': userID, 'isActive': True}).sort([("createdAt", pymongo.DESCENDING)])

    return render_template('files.html', uploaded_files=uploaded_files, user=user, error=error)


@app.route('/login')
def show_login():
    if 'userToken' in session:
        # Validating user token
        tokenDoc = mongo.db.user_tokens.find_one({"sessionHash": session['userToken']})
        if tokenDoc is None:
            session.pop('userToken', None)
            session['error'] = 'You must login again to access this page!'
            return redirect('/login')

        else:
            return redirect('/')

    status = ''
    if 'status' in session:
        status = session['status']
        session.pop('status', None)

    error = ""
    if 'error' in session:
        error = session['error']
        session.pop('error', None)

    return render_template('login.html', status=status, error=error)


@app.route('/check_login', methods=['POST'])
def check_login():
    try:
        email = request.form['email']
    except KeyError:
        email = ""
    try:
        password = request.form['password']
    except KeyError:
        password = ''

    # Check if email is blank
    if not len(email) > 0:
        session['error'] = "Email is required!"
        return redirect('/login')

    # Check if password is blank
    if not len(password) > 0:
        session['error'] = 'Password is required!'
        return redirect('/login')

    # Find user document associated with entered email in database.
    userDoc = mongo.db.users.find_one({'email': email})
    # if user_doc is not found
    if userDoc is None:
        session['error'] = 'No account exists with this email address!'
        return redirect('/login')

    # Check_password
    passwordHash = sha256(password.encode('utf-8')).hexdigest()
    if userDoc['password'] != passwordHash:
        session['error'] = 'Wrong password!'
        return redirect('/login')

    # Generating Token and saving it in session
    randomString = get_random_string()
    randomSessionHash = sha256(randomString.encode('utf-8')).hexdigest()
    user_token_record = {'userID': userDoc['_id'],
                         'sessionHash': randomSessionHash,
                         'createdAt': datetime.utcnow()
                         }
    id = mongo.db.user_tokens.insert_one(user_token_record)
    session['userToken'] = randomSessionHash
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('userToken')
    session['status'] = "You are now logged out"
    return redirect('/login')


@app.route('/signup')
def signup():
    error = ''
    if 'error' in session:
        error = session['error']
        session.pop('error', None)
    return render_template('signup.html', error=error)


@app.route('/handle_signup', methods=['POST'])
def handle_signup():
    try:
        email = request.form['email']
    except KeyError:
        email = ''
    try:
        password = request.form['password']
    except KeyError:
        password = ''
    try:
        confpassword = request.form['confpassword']
    except KeyError:
        confpassword = ''

    # Check if email is blank
    if not len(email) > 0:
        session['error'] = 'Email is required!'
        return redirect('/signup')

    # check if email is valid
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if (not re.search(regex, email)):
        session['error'] = 'Email is invalid!'
        return redirect('/signup')

    # Check if password is blank
    if not len(password) > 0:
        session['error'] = 'Password is required!'
        return redirect('/signup')

    # Check if both passwords match
    if password != confpassword:
        session['error'] = 'Password didnt match!'
        return redirect('/signup')

    # Check if email already exists in database
    matching_user_count = mongo.db.users.count_documents({"email": email})
    if matching_user_count > 0:
        session['error'] = 'Email already exists!'
        return redirect('/signup')

    # Populating database
    password = sha256(password.encode('utf-8')).hexdigest()
    credentials = {'email': email,
                   'password': password,
                   'name': '',
                   'lastLoginDate': None,
                   'createdAt': datetime.utcnow(),
                   'updatedAt': datetime.utcnow()
                   }
    id = mongo.db.users.insert_one(credentials)
    session['status'] = 'Successfully Created an Account! You can Login now.'
    return redirect('/login')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config["ALLOWED_EXTENSIONS"]

@app.route('/handle_file_upload', methods=['POST'])
def handle_file_upload():
    if not 'userToken' in session:
        session['error'] = "You must login to access this page!"
        return redirect('/login')

    # Validate user Token
    tokenDoc = mongo.db.user_tokens.find_one({"sessionHash": session['userToken']})
    if tokenDoc is None:
        session.pop('userToken', None)
        session['error'] = "You must login again to access this page!"
        return redirect('/login')

    if 'uploadedFile' not in request.files:
        session['error'] = "No files uploaded!"
        return redirect('/')

    file = request.files['uploadedFile']
    print('I have got the file')
    print(file)

    if file.filename == '':
        session['error'] = "No selected file!"
        return redirect('/')

    if not allowed_file(file.filename):
        session['error'] = "File type not allowed!"
        return redirect('/')

    #File Size Check

    # User Limit CHeck

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(file.filename)
    filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filePath)

    fileInfo = {"userID": tokenDoc['userID'],
                "originalFileName": file.filename,
                "fileType": ext,
                "fileHash": "",
                "fileSize": 0,
                "filePath": filePath,
                "isActive": True,
                "createdAt": datetime.utcnow()
                }
    id = mongo.db.files.insert_one(fileInfo)



    return redirect('/')