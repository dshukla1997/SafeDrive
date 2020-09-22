#Basic flask app
from flask import Flask,render_template,request
from flask_pymongo import PyMongo
from cfg import config
import json
#Flask App Configuration
app = Flask(__name__)
app.config["MONGO_URI"] = config['mongo_URI']
mongo = PyMongo(app)


@app.route('/')
def home():
    #users is our collection name
    user_docs = mongo.db.users.find({})
    user_docs=list(user_docs)
    for doc in user_docs:
        print(doc)
    return 'This is home page'


@app.route('/login')
def show_login():
    return render_template('login.html')

@app.route('/check_login',methods=['GET','POST'])
def check_login():
    email=request.form['email']
    password=request.form['password']
    return "Email is"+" "+email+'\n'+"Password is"+" "+password


@app.route('/signup')
def signup():
    return "Don't have an account Signup here!"
