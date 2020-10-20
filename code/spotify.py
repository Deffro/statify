import json
from flask import Flask, request, redirect, g, render_template
import requests
import datetime
from urllib.parse import quote
from flask_classful import FlaskView, route

app = Flask(__name__)

#  Client Keys
CLIENT_ID = '2490920ce5574a1a9b97a3e366c39dd3'
CLIENT_SECRET = 'bfb4c438f0e742e3ab325f98a4b3b9dc'

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


def get_auth_query_parameters():
    return {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        # "state": STATE,
        # "show_dialog": SHOW_DIALOG_str,
        "client_id": CLIENT_ID
    }


def get_token_data(auth_token):
    return {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }


@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in get_auth_query_parameters().items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def perform_auth():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    token_data = get_token_data(auth_token)
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    if post_request.status_code not in range(200, 299):
        raise Exception("Could not authenticate client.")
    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    now = datetime.datetime.now()
    return callback(access_token)


def callback(access_token):
    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return render_template("index.html", sorted_array=display_arr)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)