from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from flask_restful import Api, Resource
import spotipy
import spotipy.oauth2 as oauth2
import os

app = Flask(__name__)
app.secret_key = '8c12a131e8964aa8874bc0f5fe4560e8'  # Replace with a secret key for session management

SPOTIPY_CLIENT_ID = "8dd947abb4a341f3a58073753636b4bf"
SPOTIPY_CLIENT_SECRET = "8c12a131e8964aa8874bc0f5fe4560e8"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
scope = 'user-top-read'

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope, show_dialog=True)

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info  # Update the session with the refreshed token

    return token_info['access_token']

@app.route('/')
def login():
    login_url = sp_oauth.get_authorize_url()
    return render_template('login.html', login_url=login_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        session['token_info'] = token_info
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

def get_prof_pic(sp):
    range = 'short_term'
    results = sp.current_user_top_artists(time_range=range, limit=20)
    imgs = [(item['images'][0]['url'], item['name']) for item in results['items']]
    return imgs

def get_top_songs(sp):
    range = 'short_term'
    results = sp.current_user_top_tracks(time_range=range, limit=30)
    songs = [(item['name'], item['artists'][0]['name']) for item in results['items']]
    return songs

@app.route('/home')
def home():
    token = get_token()
    if not token:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token)
    imgs = get_prof_pic(sp)
    songs = get_top_songs(sp)
    return render_template('home.html', imgs=imgs, list=songs)

# REST API Endpoints
api = Api(app)

class TopArtistsAPI(Resource):
    def get(self):
        token = get_token()
        if not token:
            return {'error': 'Unauthorized'}, 401

        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_top_artists(time_range='short_term', limit=20)
        artists = [{'name': item['name'], 'image_url': item['images'][0]['url']} for item in results['items']]
        return artists

class TopTracksAPI(Resource):
    def get(self):
        token = get_token()
        if not token:
            return {'error': 'Unauthorized'}, 401

        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_top_tracks(time_range='short_term', limit=30)
        tracks = [{'name': item['name'], 'artist': item['artists'][0]['name']} for item in results['items']]
        return tracks

api.add_resource(TopArtistsAPI, '/api/top_artists')
api.add_resource(TopTracksAPI, '/api/top_tracks')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)
