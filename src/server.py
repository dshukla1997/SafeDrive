#Basic flask app
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def home():
    return 'This is a home page'


@app.route('/login')
def login(name=None):
    return render_template('index.html', name=name)

@app.route('/signup')
def signup():
    return "Don't have an account Signup here!"
