from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'This is a home page'

@app.route('/login')
def login():
    return (5+9);

@app.route('/signup')
def signup():
    return "Don't have an account Signup here!"
