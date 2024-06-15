from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from flask_restful import Api, Resource
import spotipy
import spotipy.oauth2 as oauth2
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)
app.secret_key = '8c12a131e8964aa8874bc0f5fe4560e8'  # Replace with a secret key for session management

SPOTIPY_CLIENT_ID =  '0689d1156c404b359ed3edd8c943df3e'
SPOTIPY_CLIENT_SECRET = '43d103e7338d4f8ebe3a6b89e04ccda7'
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

def create_swagger_json():
    swagger_data = {
        "swagger": "2.0",
        "info": {
            "title": "Spotify Flask API",
            "description": "API documentation for Spotify integration with Flask",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": [
            "http"
        ],
        "paths": {
            "/api/top_artists": {
                "get": {
                    "summary": "Get user favorite artists from Spotify",
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "image": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized. Authentication required.",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/top_tracks": {
                "get": {
                    "summary": "Get user favorite songs from Spotify",
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "artist": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized. Authentication required.",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "securityDefinitions": {
            "oauth2": {
                "type": "oauth2",
                "flow": "implicit",
                "authorizationUrl": sp_oauth.get_authorize_url(),
                "scopes": {
                    "user-read-private": "Read user's private information",
                    "user-read-email": "Read user's email address",
                    "user-top-read": "Read user's top items"
                }
            }
        },
        "security": [
            {
                "oauth2": [
                    "user-read-private",
                    "user-read-email",
                    "user-top-read"
                ]
            }
        ]
    }
    return swagger_data
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Spotify Flask API"
    },
    oauth_config={
        'clientId': SPOTIPY_CLIENT_ID,
        'clientSecret': SPOTIPY_CLIENT_SECRET,
        'appName': "Spotify Flask API",
        'scopeSeparator': ' ',
        'scope': scope,
        'additionalQueryStringParams': {'show_dialog': 'true'}
    }
)
@app.route(API_URL)
def swagger_json():
    swagger_data = create_swagger_json()
    return jsonify(swagger_data)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)