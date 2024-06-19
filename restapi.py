import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="0689d1156c404b359ed3edd8c943df3e",
                                               client_secret="43d103e7338d4f8ebe3a6b89e04ccda7",
                                               redirect_uri="http://localhost:5500/",
                                               scope="user-library-read", show_dialog=True))
print("przed")
recommended_tracks = sp.recommendations(seed_genres=['rock', 'pop'], limit=10)
print("po")
for track in recommended_tracks['tracks']:
    print(f"{track['name']} by {', '.join([artist['name'] for artist in track['artists']])}")