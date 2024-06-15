import flask
from flask import Flask, render_template, request

app = Flask(__name__)

# Home endpoint
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    artists = request.args.get('127.0.0.1:5000/artists')
    tracks = request.args.get('127.0.0.1:5000/songs')
    return render_template('home.html', imgs=artists, list=tracks)

app.run(port=8888, debug=True, host='localhost')