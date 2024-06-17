import flask
import requests
app = flask.Flask(__name__)
API_URL = "http://127.0.0.1:8888"

@app.route("/")
def home():
    requests.get(API_URL + "/api/token").json()
    artists = requests.get(API_URL + "/api/artists").json()
    tracks = requests.get(API_URL + "/api/songs").json()
    print(tracks)
    return flask.render_template("home.html", imgs=artists, list=tracks)
if __name__ == "__main__":
    app.run(debug=True, port=5000, host="127.0.0.1")