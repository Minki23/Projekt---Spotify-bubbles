import flask
from flask import Flask, render_template

app = Flask(__name__)

# Home endpoint
@app.route('/')
def start():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

app.run(port=8888)