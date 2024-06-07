from flask import Flask, render_template
import spotipy
import spotipy.util as util
import os

app = Flask(__name__)

def get_prof_pic():
  os.environ["SPOTIPY_CLIENT_ID"]="0689d1156c404b359ed3edd8c943df3e"  
  os.environ["SPOTIPY_CLIENT_SECRET"]="43d103e7338d4f8ebe3a6b89e04ccda7"   
  os.environ["SPOTIPY_REDIRECT_URI"]="http://127.0.0.1:8888/callback"
  scope = 'user-top-read'
  token = util.prompt_for_user_token(scope=scope, show_dialog=True)
  sp = spotipy.Spotify(auth=token)
  sp.trace = False

  range = 'short_term'
  results = sp.current_user_top_artists(time_range=range, limit=15)
  imgs = []
  for i, item in enumerate(results['items']):
    imgs.append((item['images'][0]['url'],item['name']))
  return imgs

@app.route('/', methods=["GET", "POST"])
def home():
  imgs = get_prof_pic()
  return render_template('index.html', imgs=imgs)

app.run(host='0.0.0.0', port=5000)