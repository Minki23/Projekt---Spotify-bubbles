from flask import Flask, render_template, redirect, request, url_for, session
import spotipy
import spotipy.oauth2 as oauth2
import os

app = Flask(__name__)
app.secret_key = '43d103e7338d4f8ebe3a6b89e04ccda7'  # Replace with a secret key for session management

# Spotify API credentials
SPOTIPY_CLIENT_ID = "0689d1156c404b359ed3edd8c943df3e"
SPOTIPY_CLIENT_SECRET = "43d103e7338d4f8ebe3a6b89e04ccda7"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Scope for Spotify API
SCOPE = 'user-top-read'

# Spotify OAuth2 object
sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE, show_dialog=True)

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    # Check if token is expired and refresh if needed
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info['access_token']

@app.route('/')
def login():
    # Redirect to Spotify's authorization URL
    login_url = sp_oauth.get_authorize_url()
    return render_template('login.html', login_url=login_url)

@app.route('/callback')
def callback():
    # Get the authorization code from the callback URL
    code = request.args.get('code')
    if code:
        # Get the token info
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

@app.route('/home')
def home():
    token = get_token()
    if not token:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token)
    imgs = get_prof_pic(sp)
    return render_template('home.html', imgs=imgs)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)
