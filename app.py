import os
from pathlib import Path
from flask import Flask, make_response, render_template, request, jsonify, redirect, session, url_for
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import json
from flask_cors import CORS
import requests
from spotipy import oauth2

app = Flask(__name__)
CORS(app)
api = Api(app)
CLIENT_ID = '0689d1156c404b359ed3edd8c943df3e'
CLIENT_SECRET = '43d103e7338d4f8ebe3a6b89e04ccda7'
REDIRECT_URI = 'http://localhost:5500/'
SCOPE = 'user-read-private user-read-email user-top-read'

cache_path = os.path.join(str(Path.home()), '.cache')
os.makedirs(cache_path, exist_ok=True)

sp_oauth = oauth2.SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=os.path.join(cache_path, 'spotify_cache'),
    show_dialog=True
)

app.secret_key = 'your_secret_key'

def get_token():
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        return None
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['access_token'])
        session['token_info'] = token_info
    return token_info['access_token']

class Login(Resource):
    def get(self):
        token_info = sp_oauth.get_access_token()
        access_token = token_info.get("access_token")
        session['token_info']=access_token
        if access_token:
            return jsonify(access_token)
        else:
            app.logger.error(f"Failed to fetch access token: {token_info}")
            return {"error": "Failed to fetch access token"}, 500

    
class UserProfile(Resource):
    def get(self):
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            if profile_response.status_code == 200:
                return profile_response.json()
            else:
                return {"error": f"Failed to fetch user profile{access_token.json}"}, profile_response.status_code
        else:
            return {"error": "Authentication required"}, 401


class Pictures(Resource):
    def get(self):
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                if 'images' in profile_data and profile_data['images']:
                    return {"url": profile_data['images'][0]['url']}
                else:
                    return {"error": "No profile pictures found"}, 404
            else:
                return {"error": "Failed to fetch pictures"}, profile_response.status_code
        else:
            return {"error": "Authentication required"}, 401

class TopArtists(Resource):
    def get(self):
        number_of_artists = request.args.get('limit', 20)
        scope = request.args.get('scope', 'short_term')
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            href = f'https://api.spotify.com/v1/me/top/artists?time_range={scope}&limit={number_of_artists}'
            top_artists_response = requests.get(href, headers=headers)
            if top_artists_response.status_code == 200:
                data = top_artists_response.json()
                artists = [{"name": artist['name'], "image": artist['images'][0]['url']} for artist in data['items']]
                return jsonify(artists)
            else:
                return {"error": "Failed to fetch top artists"}, top_artists_response.status_code
        else:
            return {"error": "Authentication required"}, 401

class TopSongs(Resource):
    def get(self):
        number_of_songs = request.args.get('limit', 50)
        scope = request.args.get('scope', 'short_term')
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            href = f'https://api.spotify.com/v1/me/top/tracks?time_range={scope}&limit={number_of_songs}'
            top_songs_response = requests.get(href, headers=headers)
            if top_songs_response.status_code == 200:
                data = top_songs_response.json()
                tracks = [{"name": track['name'], "artist": track['artists'][0]['name']} for track in data['items']]
                return jsonify(tracks)
            else:
                return {"error": "Failed to fetch top songs"}, top_songs_response.status_code
        else:
            return {"error": "Authentication required"}, 401

class ReceiveToken(Resource):
     def put(self):
        token_info = request.get_json()
        session['token_info'] = token_info['token']   
        return jsonify(token_info) 

class Logout(Resource):
    def get(self):
        session.clear()
        os.remove(os.path.join(cache_path, 'spotify_cache'))
        return make_response(jsonify({"message": "Successfully logged out"}), 200)

SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Spotify Flask API"
    },
)

@app.route(API_URL)
def swagger_json():
    swagger_data = json.load(open('static/swagger.json'))
    return jsonify(swagger_data)

@app.route('/callback')
def callback():
    return redirect(url_for('home'))

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

api.add_resource(Login, '/api/Login')
api.add_resource(Logout, '/api/Logout')
api.add_resource(UserProfile, '/api/MyProfile')
api.add_resource(Pictures, '/api/MyPicture')
api.add_resource(TopArtists, '/api/FavArtists')
api.add_resource(TopSongs, '/api/FavSongs')

# Run the Flask application
if __name__ == '__main__':
    app.run(port=8888, debug=True, host='127.0.0.1')
