import flask
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
import requests

app = flask.Flask(__name__)
API_URL = "http://127.0.0.1:8888"

@app.route("/")
def login():
    """
    Renders the login page with a login URL.
    
    Returns:
        str: Rendered HTML template for login with API login URL.
    """
    return render_template('login.html', login_url=API_URL + "/api/Login")

@app.route('/callback')
def callback():
    """
    Redirects to the home page after OAuth callback.
    
    Returns:
        flask.Response: Redirects to the home page URL.
    """
    return redirect(url_for('home'))

@app.route("/home")
def home():
    """
    Renders the home page with user data based on selected time range and data type.
    Retrieves profile picture, favorite artists or songs, and recommended tracks.
    
    Returns:
        str: Rendered HTML template for home page with retrieved data.
    """
    time_range = request.args.get('time_range', 'short_term')
    data_type = request.args.get('data_type', 'artists')
    profile_pic = requests.get(API_URL + "/api/MyPicture").json()
    
    if data_type == 'artists':
        imgs = requests.get(API_URL + "/api/FavArtists?time_range={}".format(time_range)).json()
    else:
        imgs = requests.get(API_URL + "/api/FavSongs?time_range={}".format(time_range)).json()
    
    recommended_tracks = requests.get(API_URL + "/api/Recommendations?time_range={}".format(time_range)).json()
    
    return render_template('home.html', items=imgs, recommendations=recommended_tracks["recommendations"], 
                           selected_range=time_range, selected_data_type=data_type, profile_pic=profile_pic)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="127.0.0.1")
