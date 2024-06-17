from flask import Flask, render_template, redirect, request, url_for, session
import spotipy
import spotipy.oauth2 as oauth2
import os

app = Flask(__name__)
app.secret_key = '8c12a131e8964aa8874bc0f5fe4560e8'  # Replace with a secret key for session management

SPOTIPY_CLIENT_ID = "8dd947abb4a341f3a58073753636b4bf"
SPOTIPY_CLIENT_SECRET = "8c12a131e8964aa8874bc0f5fe4560e8"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
scope = 'user-top-read'

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='user-top-read', show_dialog=True)

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None

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
    
def get_top_songs(sp, time_range):
    results = sp.current_user_top_tracks(time_range=time_range, limit=30)
    imgs = [(item['album']['images'][0]['url'], item['name']) for item in results['items']]
    return imgs

def get_recommended_tracks(sp, time_range):
    # Get the user's top artists
    top_artists = sp.current_user_top_artists(time_range=time_range, limit=5)
    artist_ids = [artist['id'] for artist in top_artists['items'][:5]]  # Limit to 5 artists
    
    # Get recommended tracks based on top artists
    recommendations = sp.recommendations(seed_artists=artist_ids, limit=20)
    recommended_tracks = [(track['name'], track['artists'][0]['name']) for track in recommendations['tracks']]
    return recommended_tracks
def get_prof_pic(sp, range):
    
    results = sp.current_user_top_artists(time_range=range, limit=20)
    imgs = [(item['images'][0]['url'], item['name']) for item in results['items']]
    return imgs
@app.route('/home')
def home():
    token = get_token()
    if not token:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token)
     # Get the selected time range from the query parameters
    time_range = request.args.get('time_range', 'short_term')
    data_type = request.args.get('data_type', 'artists')
    
    if data_type == 'artists':
        imgs = get_prof_pic(sp, time_range)
    else:
        imgs = get_top_songs(sp, time_range)
        
    recommended_tracks = get_recommended_tracks(sp, time_range)
    return render_template('home.html', items=imgs, recommendations=recommended_tracks, selected_range=time_range, selected_data_type=data_type)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)
  
