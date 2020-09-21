#Basic flask app
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def home():
    return 'This is a home page'


@app.route('/login')
def show_login():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return "Don't have an account Signup here!"
