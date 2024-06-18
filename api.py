from flask import Flask, render_template, request, jsonify, redirect, session
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import requests
from spotipy import oauth2

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:8888"]}})
api = Api(app)


#natalka

# Spotify API credentials and settings
CLIENT_ID = "8dd947abb4a341f3a58073753636b4bf"
CLIENT_SECRET = "8c12a131e8964aa8874bc0f5fe4560e8"

#minki
# CLIENT_ID = '0689d1156c404b359ed3edd8c943df3e'
# CLIENT_SECRET = '43d103e7338d4f8ebe3a6b89e04ccda7'
REDIRECT_URI = 'http://localhost:5500/index.html'
SCOPE = 'user-top-read user-library-modify playlist-modify-public playlist-modify-private user-read-private user-read-email'

# Spotify OAuth object
sp_oauth = oauth2.SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path='/',  # Specify cache path if needed
    show_dialog=True  # Show dialog for user consent
)

app.secret_key = 'your_secret_key'

def get_token():
    """
    Retrieve OAuth token from session or refresh if expired.
    
    Returns:
        str: Access token if valid and refreshed successfully, else None.
    """
    token_info = session.get('token_info', None)
    
    if not token_info:
        return None

    if sp_oauth.is_token_expired(token_info):
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
        except oauth2.SpotifyOauthError as e:
            app.logger.error(f"Failed to refresh token: {e}")
            return None

    return token_info['access_token']

class UserProfile(Resource):
    def get(self):
        """
        Get user profile from Spotify API.

        Returns:
            dict: User profile data if successful.
            tuple: Error message and status code if authentication fails.
        """
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            return profile_response.json()
        else:
            return jsonify({"error": "Authentication required"}), 401

class Pictures(Resource):
    def get(self):
        """
        Get user pictures from Spotify API.

        Returns:
            str: URL of the user's profile picture if successful.
            tuple: Error message and status code if authentication fails or picture fetching fails.
        """
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            if profile_response.status_code == 200:
                return profile_response.json()['images'][0]['url']
            else:
                return jsonify({"error": "Failed to fetch pictures"}), profile_response.status_code
        else:
            return jsonify({"error": "Authentication required"}), 401

class TopArtists(Resource):
    def get(self):
        """
        Get user's top artists from Spotify API.

        Returns:
            list: List of tuples (artist name, image URL) if successful.
            tuple: Error message and status code if authentication fails.
        """
        number_of_artists = request.args.get('limit', 20)
        scope = request.args.get('scope', 'short_term')
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            href = f'https://api.spotify.com/v1/me/top/artists?time_range={scope}&limit={number_of_artists}'
            top_artists_response = requests.get(href, headers=headers).json()
            artists = []
            for artist in top_artists_response['items']:
                artists.append((artist['name'], artist['images'][0]['url']))
            return artists
        else:
            return jsonify({"error": "Authentication required"}), 401

class TopSongs(Resource):
    def get(self):
        """
        Get user's top songs from Spotify API.

        Returns:
            list: List of tuples (song name, artist name) if successful.
            tuple: Error message and status code if authentication fails.
        """
        number_of_songs = request.args.get('limit', 50)
        scope = request.args.get('scope', 'short_term')
        access_token = get_token()
        if access_token:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            href = f'https://api.spotify.com/v1/me/top/tracks?time_range={scope}&limit={number_of_songs}'
            top_songs_response = requests.get(href, headers=headers).json()
            tracks = []
            for track in top_songs_response['items']:
                tracks.append((track['name'], track['artists'][0]['name']))
            return tracks
        else:
            return jsonify({"error": "Authentication required"}), 401

def create_swagger_json():
    """
    Create Swagger JSON specification for API documentation.

    Returns:
        dict: Swagger JSON data.
    """
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
            "/profile": {
                "get": {
                    "summary": "Get user profile from Spotify",
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "schema": {
                                "type": "object"
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
            "/pictures": {
                "get": {
                    "summary": "Get user pictures from Spotify",
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "schema": {
                                "type": "string"
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
            "/artists": {
                "get": {
                    "summary": "Get user favorite artists from Spotify",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Number of artists to return",
                            "required": "false",
                            "type": "integer",
                            "format": "int32"
                        },
                        {
                            "name": "scope",
                            "in": "query",
                            "description": "Scope of artists to return",
                            "required": "false",
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string"
                                        },
                                        "image_url": {
                                            "type": "string"
                                        }
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
                "authorizationUrl": 'https://accounts.spotify.com/authorize',
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

# Configure Swagger UI
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Spotify Flask API"
    },
    oauth_config={
        'clientId': CLIENT_ID,
        'clientSecret': CLIENT_SECRET,
        'appName': "Spotify Flask API",
        'scopeSeparator': ' ',
        'scope': SCOPE,
        'additionalQueryStringParams': {'show_dialog': 'true'}
    }
)

@app.route(API_URL)
def swagger_json():
    """
    Serve Swagger JSON specification.

    Returns:
        dict: Swagger JSON data.
    """
    swagger_data = create_swagger_json()
    return jsonify(swagger_data)

# Register Swagger UI blueprint and API endpoints
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Registering API endpoints using Flask-RESTful
api.add_resource(UserProfile, '/profile')
api.add_resource(Pictures, '/pictures')
api.add_resource(TopArtists, '/artists')
api.add_resource(TopSongs, '/songs')

@app.route('/')
def start():
    """
    Redirect to Swagger UI on the root endpoint.
    """
    return redirect('/swagger')

@app.route('/login')
def login():
    """
    Redirect to Spotify login page for OAuth authorization.
    """
    session.clear()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """
    Callback URL after Spotify OAuth authorization.
    Retrieves access token and stores it in session.
    """
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect('/swagger')

# Run the Flask application
if __name__ == '__main__':
    app.run(port=5000, debug=True, host='127.0.0.1')
