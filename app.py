import spotipy
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from spotipy.oauth2 import SpotifyOAuth
from pytube import Search, YouTube
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

client_id = "0da6fbf3834144c98492a2f28f237863"
client_secret = "bbb210d06ec14135b31d6c1ad50e62d1"
redirect_uri = "http://localhost:8888/callback"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def download_youtube_audio(playlist_link, destination_folder):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope="playlist-read-private"))

    playlist_id = playlist_link.split('/')[-1].split('?')[0]
    playlist = sp.playlist_tracks(playlist_id)

    youtube_urls = []

    for track in playlist['items']:
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        
        a = Search(track_name)
        s = a.results
        max = s[0].views
        maxi = s[0]
        for v in a.results:
            if v.views > max:
                max = v.views
                maxi = v
        url = maxi.watch_url
        youtube_urls.append(url)
        # print(f"Number of views: {maxi.views}")
        # print(f"{maxi.title}\n{maxi.watch_url}\n")
    
    for url in youtube_urls:
        video = YouTube(url)
        audio_stream = video.streams.filter(only_audio=True).first()
        download_path = os.path.join(destination_folder, secure_filename(video.title))
        
        print(f"Downloading {video.title} to {download_path}")
        audio_stream.download(download_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_link = request.form['playlist_link']
        destination_folder = request.form['destination_folder']

        os.makedirs(destination_folder, exist_ok=True)

        download_youtube_audio(playlist_link, destination_folder)
        print(f"Received Playlist Link: {playlist_link}")
        print(f"Download destination folder: {destination_folder}")

        return redirect(url_for('index'))  

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
