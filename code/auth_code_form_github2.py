import os
import json
from flask import Flask, request, redirect, render_template
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import requests
import datetime
from urllib.parse import quote
from flask_classful import FlaskView, route
import pandas as pd
import numpy as np

server = Flask(__name__)

app = Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/'
)

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
CLIENT_SIDE_URL = "http://127.0.0.1"  # "http://b268218d4cdf.ngrok.io"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-top-read user-follow-modify user-library-read playlist-read-private " \
        "playlist-read-collaborative user-follow-read user-library-modify"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


def create_user_top_artists_across_periods(user_top_artists_data_long_term, user_top_artists_data_medium_term,
                                           user_top_artists_data_short_term, entity="artist"):
    entity_name = 'name' if entity.lower() == "artist" else "song_name"
    long_term_names = user_top_artists_data_long_term[entity_name].tolist()
    medium_term_names = user_top_artists_data_medium_term[entity_name].tolist()
    short_term_names = user_top_artists_data_short_term[entity_name].tolist()

    for m in medium_term_names:
        if m not in long_term_names:
            long_term_names.append(m)
    for s in short_term_names:
        if s not in long_term_names:
            long_term_names.append(s)

    long_term_position, medium_term_position, short_term_position = [], [], []
    for t in long_term_names:
        try:
            long_term_position.append(
                user_top_artists_data_long_term.loc[user_top_artists_data_long_term[entity_name] == t].index.values[
                    0] + 1)
        except IndexError:
            long_term_position.append('-')
        try:
            medium_term_position.append(
                user_top_artists_data_medium_term.loc[user_top_artists_data_medium_term[entity_name] == t].index.values[
                    0] + 1)
        except IndexError:
            medium_term_position.append('-')
        try:
            short_term_position.append(
                user_top_artists_data_short_term.loc[user_top_artists_data_short_term[entity_name] == t].index.values[
                    0] + 1)
        except IndexError:
            short_term_position.append('-')

    user_top_artists_across_periods = pd.DataFrame()

    user_top_artists_across_periods[entity.capitalize()] = long_term_names
    user_top_artists_across_periods['All Time'] = long_term_position
    user_top_artists_across_periods['Last 6 Months'] = medium_term_position
    user_top_artists_across_periods['Last Month'] = short_term_position

    return user_top_artists_across_periods


def add_symbols(df):
    if type(df['Last Month']) == np.int64:
        if type(df['Last 6 Months']) == np.int64:
            if df['Last Month'] < df['Last 6 Months']:
                df['Last Month'] = str(df['Last Month']) + " " + u"\u2B06"
            elif df['Last Month'] > df['Last 6 Months']:
                df['Last Month'] = str(df['Last Month']) + " " + u"\u2B07"
            else:
                df['Last Month'] = str(df['Last Month'])
        else:
            df['Last Month'] = str(df['Last Month']) + " " + u"\u2B50"
        if df['Last Month'].split(' ')[0].isnumeric():
            if int(df['Last Month'].split(' ')[0]) == 1:
                df['Last Month'] = str(df['Last Month']) + " " + chr(128293)

    if type(df['Last 6 Months']) == np.int64:
        if type(df['All Time']) == np.int64:
            if df['Last 6 Months'] < df['All Time']:
                df['Last 6 Months'] = str(df['Last 6 Months']) + " " + u"\u2B06"
            elif df['Last 6 Months'] > df['All Time']:
                df['Last 6 Months'] = str(df['Last 6 Months']) + " " + u"\u2B07"
            else:
                df['Last 6 Months'] = str(df['Last 6 Months'])
        else:
            df['Last 6 Months'] = str(df['Last 6 Months']) + " " + u"\u2B50"
        if df['Last 6 Months'].split(' ')[0].isnumeric():
            if int(df['Last 6 Months'].split(' ')[0]) == 1:
                df['Last 6 Months'] = str(df['Last 6 Months']) + " " + chr(128293)

    return df


def ms_to_min_sec(duration):
    sec = int((duration/1000) % 60)
    if sec < 10:
        sec = '0'+str(sec)
    minutes = int((duration/(1000*60)) % 60)
    return f"{minutes}:{sec}"


def process_user_saved_tracks_data(data):
    """
    :param data: in json format
    :return: pandas DataFrame
    """
    added_at = []
    artist_name, artist_external_url = [], []
    album_name, album_release_date, album_image_url = [], [], []
    album_external_url, album_total_tracks = [], []
    song_duration, song_external_url, song_name = [], [], []
    song_popularity, song_preview_url, song_number_in_album = [], [], []

    for track in data['items']:
        added_at.append(track['added_at'])
        artist_external_url.append(track['track']['album']['artists'][0]['external_urls']['spotify'])
        artist_name.append(track['track']['album']['artists'][0]['name'])
        album_external_url.append(track['track']['album']['external_urls']['spotify'])
        try:
            album_image_url.append(track['track']['album']['images'][1]['url'])
        except IndexError:
            try:
                album_image_url.append(track['album']['images'][0]['url'])
            except IndexError:
                album_image_url.append(np.nan)
        album_name.append(track['track']['album']['name'])
        album_release_date.append(track['track']['album']['release_date'])
        album_total_tracks.append(track['track']['album']['total_tracks'])
        song_duration.append(ms_to_min_sec(track['track']['duration_ms']))
        song_external_url.append(track['track']['external_urls']['spotify'])
        song_name.append(track['track']['name'])
        song_popularity.append(track['track']['popularity'])
        song_preview_url.append(track['track']['preview_url'])
        song_number_in_album.append(track['track']['track_number'])

    user_saved_track_data = pd.DataFrame(columns=['song_name', 'added_at', 'song_duration',
                                                  'song_popularity', 'song_number_in_album',
                                                  'song_external_url', 'song_preview_url',
                                                  'album_name', 'album_release_date',
                                                  'album_total_tracks', 'album_image_url',
                                                  'album_external_url', 'artist_name',
                                                  'artist_external_url'])
    user_saved_track_data['song_name'] = song_name
    user_saved_track_data['added_at'] = added_at
    user_saved_track_data['song_duration'] = song_duration
    user_saved_track_data['song_popularity'] = song_popularity
    user_saved_track_data['song_number_in_album'] = song_number_in_album
    user_saved_track_data['song_external_url'] = song_external_url
    user_saved_track_data['song_preview_url'] = song_preview_url
    user_saved_track_data['album_name'] = album_name
    user_saved_track_data['album_release_date'] = album_release_date
    user_saved_track_data['album_total_tracks'] = album_total_tracks
    user_saved_track_data['album_image_url'] = album_image_url
    user_saved_track_data['album_external_url'] = album_external_url
    user_saved_track_data['artist_name'] = artist_name
    user_saved_track_data['artist_external_url'] = artist_external_url
    return user_saved_track_data


def process_user_followed_artists_data(data):
    """
    :param data: in json format
    :return: pandas DataFrame
    """
    name, popularity, image_url, external_url, followers, genres = [], [], [], [], [], []
    for artist in data['artists']['items']:
        name.append(artist['name'])
        popularity.append(artist['popularity'])
        try:
            image_url.append(artist['images'][1]['url'])
        except IndexError:
            try:
                image_url.append(artist['images'][0]['url'])
            except IndexError:
                image_url.append(np.nan)
        external_url.append(artist['href'])
        followers.append(artist['followers']['total'])
        genres.append(artist['genres'])

    user_saved_artist_data = pd.DataFrame(columns=['name', 'followers', 'popularity',
                                                   'genres', 'image_url', 'external_url'])
    user_saved_artist_data['name'] = name
    user_saved_artist_data['followers'] = followers
    user_saved_artist_data['popularity'] = popularity
    user_saved_artist_data['genres'] = genres
    user_saved_artist_data['image_url'] = image_url
    user_saved_artist_data['external_url'] = external_url
    return user_saved_artist_data


def process_user_top_artists(data):
    """
    :param data: in json format
    :return: pandas DataFrame
    """
    name, popularity, image_url, external_url, followers, genres = [], [], [], [], [], []
    for artist in data['items']:
        name.append(artist['name'])
        popularity.append(artist['popularity'])
        try:
            image_url.append(artist['images'][1]['url'])
        except IndexError:
            try:
                image_url.append(artist['images'][0]['url'])
            except IndexError:
                image_url.append(np.nan)

        external_url.append(artist['external_urls']['spotify'])
        followers.append(artist['followers']['total'])
        genres.append(artist['genres'])

    user_top_artist_data = pd.DataFrame(columns=['name', 'followers', 'popularity',
                                                 'genres', 'image_url', 'external_url'])
    user_top_artist_data['name'] = name
    user_top_artist_data['followers'] = followers
    user_top_artist_data['popularity'] = popularity
    user_top_artist_data['genres'] = genres
    user_top_artist_data['image_url'] = image_url
    user_top_artist_data['external_url'] = external_url

    return user_top_artist_data


def process_user_top_tracks(data):
    """
    :param data: in json format
    :return: pandas DataFrame
    """
    artist_name, artist_external_url = [], []
    album_name, album_release_date, album_image_url = [], [], []
    album_external_url, album_total_tracks = [], []
    song_duration, song_external_url, song_name, song_popularity = [], [], [], []
    song_preview_url, song_number_in_album = [], []

    for track in data['items']:
        artist_external_url.append(track['album']['artists'][0]['external_urls']['spotify'])
        artist_name.append(track['album']['artists'][0]['name'])
        album_external_url.append(track['album']['external_urls']['spotify'])
        try:
            album_image_url.append(track['album']['images'][1]['url'])
        except IndexError:
            try:
                album_image_url.append(track['album']['images'][0]['url'])
            except IndexError:
                album_name.append(np.nan)
        album_name.append(track['album']['name'])
        album_release_date.append(track['album']['release_date'])
        album_total_tracks.append(track['album']['total_tracks'])
        song_duration.append(ms_to_min_sec(track['duration_ms']))
        song_external_url.append(track['external_urls']['spotify'])
        song_name.append(track['name'])
        song_popularity.append(track['popularity'])
        song_preview_url.append(track['preview_url'])
        song_number_in_album.append(track['track_number'])

    user_top_track_data = pd.DataFrame(
        columns=['song_name', 'song_duration', 'song_popularity', 'song_number_in_album',
                 'song_external_url', 'song_preview_url', 'album_name', 'album_release_date',
                 'album_total_tracks', 'album_image_url', 'album_external_url', 'artist_name',
                 'artist_external_url'])
    user_top_track_data['song_name'] = song_name
    user_top_track_data['song_duration'] = song_duration
    user_top_track_data['song_popularity'] = song_popularity
    user_top_track_data['song_number_in_album'] = song_number_in_album
    user_top_track_data['song_external_url'] = song_external_url
    user_top_track_data['song_preview_url'] = song_preview_url
    user_top_track_data['album_name'] = album_name
    user_top_track_data['album_release_date'] = album_release_date
    user_top_track_data['album_total_tracks'] = album_total_tracks
    user_top_track_data['album_image_url'] = album_image_url
    user_top_track_data['album_external_url'] = album_external_url
    user_top_track_data['artist_name'] = artist_name
    user_top_track_data['artist_external_url'] = artist_external_url
    return user_top_track_data


class SpotifyAPI(FlaskView):
    access_token = None
    refresh_token = None
    token_type = None
    expires_in = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True

    def get_auth_query_parameters(self):
        return {
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPE,
            # "state": STATE,
            # "show_dialog": SHOW_DIALOG_str,
            "client_id": CLIENT_ID
        }

    def get_access_token_data(self, auth_token):
        return {
            "grant_type": "authorization_code",
            "code": str(auth_token),
            "redirect_uri": REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }

    @route("/")
    def index(self):
        """
        Create authorization url and redirect to it
        """
        url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in self.get_auth_query_parameters().items()])
        auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
        return redirect(auth_url)

    @route("/callback/q")
    def perform_auth(self):
        # Requests refresh and access tokens
        auth_token = request.args['code']  # access the data from the GET (url)
        access_token_data = self.get_access_token_data(auth_token)
        post_request = requests.post(SPOTIFY_TOKEN_URL, data=access_token_data)
        if post_request.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
        # Tokens are Returned to Application
        response_data = json.loads(post_request.text)
        self.access_token = response_data["access_token"]
        self.refresh_token = response_data["refresh_token"]
        self.token_type = response_data["token_type"]
        self.expires_in = response_data["expires_in"]
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=self.expires_in)
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return self.callback()

    def get_persistent_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        print(expires)
        if expires < now:
            self.perform_auth()
            return self.get_persistent_access_token()
        elif token is None:
            self.perform_auth()
            return self.get_persistent_access_token()
        return token

    def get_authorization_header(self):
        access_token = self.get_persistent_access_token()
        return {
            "Authorization": "Bearer {}".format(access_token)
        }

    def get_profile_data(self):
        authorization_header = self.get_authorization_header()
        endpoint = f"{SPOTIFY_API_URL}/me"
        r = requests.get(endpoint, headers=authorization_header)
        return json.loads(r.text)

    def get_user_playlist_data(self, limit=50, offset=0):
        authorization_header = self.get_authorization_header()
        endpoint = f"{SPOTIFY_API_URL}/me/playlists?limit={limit}&offset={offset}"
        r = requests.get(endpoint, headers=authorization_header)
        return json.loads(r.text)

    def get_user_top_artists_and_tracks(self, entity_type="artists", limit=50,
                                        time_range="medium_term", offset=0):
        """
        :param entity_type:  artists or tracks
        :param limit: The number of entities to return. Minimum: 1. Maximum: 50.
        :param time_range: Over what time frame the affinities are computed. Valid values: long_term
            (calculated from several years of data and including all new data as it becomes available),
            medium_term (approximately last 6 months), short_term (approximately last 4 weeks)
        :param offset: The index of the first entity to return. Default: 0 (i.e., the first track).
            Use with limit to get the next set of entities
        :return:
        """
        authorization_header = self.get_authorization_header()
        endpoint = f"{SPOTIFY_API_URL}/me/top/{entity_type}?time_range={time_range}&limit={limit}" \
                   f"&offset={offset}"
        r = requests.get(endpoint, headers=authorization_header)
        return json.loads(r.text)

    def get_user_followed_artists(self, entity_type="artist", limit=50):
        authorization_header = self.get_authorization_header()
        endpoint = f"{SPOTIFY_API_URL}/me/following/?type={entity_type}&limit={limit}"
        r = requests.get(endpoint, headers=authorization_header)
        return json.loads(r.text)

    def get_user_saved_albums(self, limit=50, offset=0):
        authorization_header = self.get_authorization_header()
        endpoint = f"{SPOTIFY_API_URL}/me/albums/?limit={limit}&offset={offset}"
        r = requests.get(endpoint, headers=authorization_header)
        return json.loads(r.text)

    def get_user_saved_tracks(self, limit=50, offset=0):
        authorization_header = self.get_authorization_header()
        endpoint = f"{SPOTIFY_API_URL}/me/tracks/?limit={limit}&offset={offset}"
        r = requests.get(endpoint, headers=authorization_header)
        return json.loads(r.text)

    # def get_user_playlists(self, user_id, limit=50, offset=0):
    #     authorization_header = self.get_authorization_header()
    #     endpoint = f"{SPOTIFY_API_URL}/me/users/"  # not complete
    #     r = requests.get(endpoint, headers=authorization_header)
    #     return json.loads(r.text)

    def get_all_user_top_artists_and_tracks(self, entity_type="artists", time_range="medium_term"):
        """
        Return a DataFrame containing all of user's top artists or tracks
        :return: pandas DataFrame
        """
        total_top_entity = self.get_user_top_artists_and_tracks(entity_type=entity_type, limit=1,
                                                                time_range=time_range, offset=0)['total']
        user_top_entity_data = pd.DataFrame()
        for i in range(int(total_top_entity/50)+1):
            temp_json = self.get_user_top_artists_and_tracks(entity_type=entity_type, limit=50,
                                                             time_range=time_range, offset=i*50)
            if entity_type == "artists":
                temp = process_user_top_artists(temp_json)
            else:
                temp = process_user_top_tracks(temp_json)
            user_top_entity_data = pd.concat([user_top_entity_data, temp])
        return user_top_entity_data

    def get_all_user_saved_tracks(self):
        """
        Return a DataFrame containing all of user's saved tracks
        :return: pandas DataFrame
        """
        total_songs_saved = self.get_user_saved_tracks(limit=1, offset=0)['total']
        user_saved_tracks_data = pd.DataFrame()
        for i in range(int(total_songs_saved/50)+1):
            temp_json = self.get_user_saved_tracks(limit=50, offset=i*50)
            temp = process_user_saved_tracks_data(temp_json)
            user_saved_tracks_data = pd.concat([user_saved_tracks_data, temp])
        return user_saved_tracks_data

    def callback(self):
        user_profile_data = self.get_profile_data()

        user_saved_tracks_data = self.get_all_user_saved_tracks()
        user_top_artists_data_medium_term = \
            self.get_all_user_top_artists_and_tracks(entity_type="artists", time_range="medium_term")
        user_top_artists_data_long_term = \
            self.get_all_user_top_artists_and_tracks(entity_type="artists", time_range="long_term")
        user_top_artists_data_short_term = \
            self.get_all_user_top_artists_and_tracks(entity_type="artists", time_range="short_term")

        user_top_artists_across_periods = create_user_top_artists_across_periods(user_top_artists_data_long_term,
                                                                                 user_top_artists_data_medium_term,
                                                                                 user_top_artists_data_short_term,
                                                                                 entity='artist')
        user_top_artists_across_periods = user_top_artists_across_periods.apply(lambda df: add_symbols(df), axis=1)

        # user_top_tracks_data_medium_term = \
        #     self.get_all_user_top_artists_and_tracks(entity_type="tracks", time_range="medium_term")
        # user_top_tracks_data_long_term = \
        #     self.get_all_user_top_artists_and_tracks(entity_type="tracks", time_range="long_term")
        # user_top_tracks_data_short_term = \
        #     self.get_all_user_top_artists_and_tracks(entity_type="tracks", time_range="short_term")
        #
        # temp_json = self.get_user_followed_artists()
        # user_followed_artists_data_data = process_user_followed_artists_data(temp_json)
        #
        # path = f"../data/{user_profile_data['display_name']}/"
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # user_saved_tracks_data.to_csv(f"{path}user_saved_tracks_data.csv", index=False)
        #
        # user_top_artists_data_medium_term.to_csv(f"{path}user_top_artists_data_medium_term.csv", index=False)
        # user_top_tracks_data_medium_term.to_csv(f"{path}user_top_tracks_data_medium_term.csv", index=False)
        #
        # user_top_artists_data_long_term.to_csv(f"{path}user_top_artists_data_long_term.csv", index=False)
        # user_top_tracks_data_long_term.to_csv(f"{path}user_top_tracks_data_long_term.csv", index=False)
        #
        # user_top_artists_data_short_term.to_csv(f"{path}user_top_artists_data_short_term.csv", index=False)
        # user_top_tracks_data_short_term.to_csv(f"{path}user_top_tracks_data_short_term.csv", index=False)
        #
        # user_followed_artists_data_data.to_csv(f"{path}user_followed_artists_data_data.csv", index=False)

        return render_template("/dash/", sorted_array=user_profile_data)


SpotifyAPI.register(server, route_base='/')

app.layout = html.Div("My Dash app")

if __name__ == '__main__':
    app.run_server(debug=True, port=PORT)
