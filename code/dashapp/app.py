import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import ast
import dash_table
from flask import Flask, request, redirect, render_template, url_for, session
from server import server

print('+++++++7')

def create_user_top_artists_across_periods(df_long_term, df_medium_term, df_short_term, entity="artist"):
    """
    From three csv files create on with the all the artists as the first column and another 3 columns
    corresponding to rank of this artist in the periods 'All Time', 'Last 6 Months', 'Last Month'.
    """
    entity_name = 'name' if entity.lower() == "artist" else "song_name"
    long_term_names = df_long_term[entity_name].tolist()
    medium_term_names = df_medium_term[entity_name].tolist()
    short_term_names = df_short_term[entity_name].tolist()

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
                df_long_term.loc[df_long_term[entity_name] == t].index.values[
                    0] + 1)
        except IndexError:
            long_term_position.append('-')
        try:
            medium_term_position.append(
                df_medium_term.loc[df_medium_term[entity_name] == t].index.values[
                    0] + 1)
        except IndexError:
            medium_term_position.append('-')
        try:
            short_term_position.append(
                df_short_term.loc[df_short_term[entity_name] == t].index.values[
                    0] + 1)
        except IndexError:
            short_term_position.append('-')

    user_top_artists_across_periods_df = pd.DataFrame()
    user_top_artists_across_periods_df[entity.capitalize()] = long_term_names
    user_top_artists_across_periods_df['All Time'] = long_term_position
    user_top_artists_across_periods_df['Last 6 Months'] = medium_term_position
    user_top_artists_across_periods_df['Last Month'] = short_term_position
    return user_top_artists_across_periods_df


def add_symbols(df):
    """
    Add the unicode symbols (arrows, fire) inside the corresponding cells of the df.
    """
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


def annotate_and_finalize_user_top_artists(user_id):
    """
    Read the 3 files of the top artists per period.
    Call the 'create_user_top_artists_across_periods' function to create the user_top_artists_across_periods df.
    Generate the colors for the table to be plotted.
    """
    user_top_artists_data_long_term = pd.read_csv(f'../data/{user_id}/user_top_artists_data_long_term.csv')
    user_top_artists_data_medium_term = pd.read_csv(f'../data/{user_id}/user_top_artists_data_medium_term.csv')
    user_top_artists_data_short_term = pd.read_csv(f'../data/{user_id}/user_top_artists_data_short_term.csv')

    user_top_artists_across_periods_df = create_user_top_artists_across_periods(user_top_artists_data_long_term,
                                                                                user_top_artists_data_medium_term,
                                                                                user_top_artists_data_short_term,
                                                                                entity='artist')
    user_top_artists_across_periods_df = user_top_artists_across_periods_df.apply(lambda df: add_symbols(df), axis=1)

    clrs_last_mo = (user_top_artists_across_periods_df['Last Month'].apply(
        lambda x: "#d8f0df" if '\u2B06' in x else ("#e6dada" if '\u2B07' in x else "white"))).tolist()
    clrs_6_mo = (user_top_artists_across_periods_df['Last 6 Months'].apply(
        lambda x: "#d8f0df" if '\u2B06' in x else ("#e6dada" if '\u2B07' in x else "white"))).to_list()
    return user_top_artists_across_periods_df, clrs_last_mo, clrs_6_mo


def annotate_and_finalize_user_top_tracks():
    """
    Read the 3 files of the top tracks per period.
    Call the 'create_user_top_artists_across_periods' function to create the user_top_artists_across_periods df.
    Generate the colors for the table to be plotted.
    """
    user_top_tracks_data_long_term = pd.read_csv(f'../data/{user_id}/user_top_tracks_data_long_term.csv')
    user_top_tracks_data_medium_term = pd.read_csv(f'../data/{user_id}/user_top_tracks_data_medium_term.csv')
    user_top_tracks_data_short_term = pd.read_csv(f'../data/{user_id}/user_top_tracks_data_short_term.csv')

    user_top_tracks_across_periods_df = create_user_top_artists_across_periods(user_top_tracks_data_long_term,
                                                                               user_top_tracks_data_medium_term,
                                                                               user_top_tracks_data_short_term,
                                                                               entity='track')
    user_top_tracks_data_all_term = pd.concat([user_top_tracks_data_long_term, user_top_tracks_data_medium_term,
                                               user_top_tracks_data_short_term])
    user_top_tracks_data_all_term = user_top_tracks_data_all_term.drop_duplicates()
    user_top_tracks_across_periods_df = user_top_tracks_across_periods_df.merge(
        user_top_tracks_data_all_term[['song_name', 'song_preview_url']], left_on=['Track'], right_on='song_name',
        how='left')
    user_top_tracks_across_periods_df = user_top_tracks_across_periods_df.drop(columns=['song_name'], axis=1)
    user_top_tracks_across_periods_df = user_top_tracks_across_periods_df.rename(
        columns={'song_preview_url': 'Listen!'})

    user_top_tracks_across_periods_df = user_top_tracks_across_periods_df.apply(lambda df: add_symbols(df), axis=1)

    clrs_last_mo = (user_top_tracks_across_periods_df['Last Month'].apply(
        lambda x: "#d8f0df" if '\u2B06' in x else ("#e6dada" if '\u2B07' in x else "white"))).tolist()
    clrs_6_mo = (user_top_tracks_across_periods_df['Last 6 Months'].apply(
        lambda x: "#d8f0df" if '\u2B06' in x else ("#e6dada" if '\u2B07' in x else "white"))).to_list()
    return user_top_tracks_across_periods_df, clrs_last_mo, clrs_6_mo


def plot_top_entity_across_periods(df, clrs_6_mo, clrs_last_mo, entity):
    if entity == 'artist':
        return dcc.Graph(
            id='top-per-period-artist',
            figure={
                'data': [
                    go.Table(
                        columnwidth=[35, 13, 20, 17],
                        header=dict(
                            values=list(
                                f"<b>{c}</b>" for c in
                                df.columns),
                            fill_color='#1da843',
                            align='center',
                            height=30,
                            font=dict(color='black', size=18)
                        ),
                        cells=dict(values=[df[c] for c in
                                           df.columns],
                                   fill_color=['white', 'white', clrs_6_mo, clrs_last_mo],
                                   line_color='#e1f0e5',
                                   align='center',
                                   font=dict(color='black', size=18),
                                   height=30
                                   )
                    )
                ],
                'layout': go.Layout(
                    margin=dict(t=0, l=0, r=0, b=0),
                    height=200
                )
            }
        )
    elif entity == 'track':
        return dcc.Graph(
            id='top-per-period-track',
            figure={
                'data': [
                    go.Table(
                        columnwidth=[35, 10, 17, 14, 35],
                        header=dict(
                            values=list(
                                f"<b>{c}</b>" for c in
                                df.columns),
                            fill_color='#1da843',
                            align='center',
                            height=30,
                            font=dict(color='black', size=18)
                        ),
                        cells=dict(values=[df[c] for c in
                                           df.columns],
                                   fill_color=['white', 'white', clrs_6_mo, clrs_last_mo],
                                   line_color='#e1f0e5',
                                   align='center',
                                   font=dict(color='black', size=18),
                                   height=30
                                   )
                    )
                ],
                'layout': go.Layout(
                    title='Top Artists per Listening Period'
                )
            }
        )


def generate_table_top_tracks(dataframe, clrs_last_mo, clrs_6_mo):
    body_outer, headers = [], []
    # Header
    for col in dataframe.columns:
        headers.append(html.Th(col, style={'backgroundColor': '#1da843'}))
    headers = [html.Tr(headers)]

    for i in range(len(dataframe)):
        body = []
        for col in dataframe.columns:
            if col == 'Last Month':
                body.append(html.Td(dataframe.iloc[i][col], style={'padding': '0px', 'margin': '0px',
                                                                   'backgroundColor': clrs_last_mo[i],
                                                                   'textAlign': 'center'
                                                                   }))
            elif col == 'Last 6 Months':
                body.append(html.Td(dataframe.iloc[i][col], style={'padding': '0px', 'margin': '0px',
                                                                   'backgroundColor': clrs_6_mo[i],
                                                                   'textAlign': 'center'}))
            elif col == 'Listen!':
                body.append(html.Audio(controls='controls', src=dataframe.iloc[i]['Listen!'],
                                       style={'width': '200px', 'height': '20px'}))
            elif col == 'All Time':
                body.append(html.Td(dataframe.iloc[i][col], style={'padding': '0px', 'margin': '0px',
                                                                   'textAlign': 'center'}))
            else:
                body.append(html.Td(dataframe.iloc[i][col], style={'padding': '0px', 'margin': '0px'}))
        body_outer.append(html.Tr(body, style={'height': '2px'}))

    return html.Table(headers + body_outer, style={'fontSize': 16, 'fontWeight': 'bold',
                                                   'fontFamily': 'helvetica', 'marginTop': '-2px'})


def get_genre_count(df):
    genres_top_count = {}
    for genre_list in df['genres']:
        for genre in ast.literal_eval(genre_list):
            if genre not in genres_top_count:
                genres_top_count[genre] = 1
            else:
                genres_top_count[genre] += 1
    genres_top_count = pd.Series(genres_top_count).sort_values(ascending=False)
    return genres_top_count.head()


def create_sunburst_data(df, top_genres):
    genres, artists, values = [], [], []
    for i, row in df.iterrows():
        for genre, value in zip(top_genres.index, top_genres.values):
            if genre in row['genres']:
                genres.append(genre)
                values.append(str(value))
                artists.append(row['name'])

    dataframe = pd.DataFrame()
    dataframe['artist'] = artists
    dataframe['genres'] = genres
    dataframe['values'] = values
    return dataframe


def plot_artist_sunburst(df, title):
    if not df.empty:
        fig = px.sunburst(df, path=['genres', 'artist'], values='values')
        fig.update_layout(margin=dict(t=10, l=0, r=0, b=0), title={'text': title,
                                                                   'x': 0.5, 'y': 0.92})
    else:
        fig = {
            'data': [],
            'layout': go.Layout(
                xaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False},
                yaxis={'showticklabels': False, 'ticks': '', 'showgrid': False, 'zeroline': False}
            )
        }
    return fig


def plot_bubble(df):
    fig = px.scatter(df, x="Release Date", y="Song Popularity",
                     size="Song Duration in Seconds", color="Artist",
                     hover_name="Song", size_max=60)
    fig.update_layout(yaxis=dict(gridcolor='#DFEAF4'),
                      title='My top songs over release date and their Spotify popularity', title_x=0.5,
                      xaxis=dict(gridcolor='#DFEAF4'), plot_bgcolor='white')
    return fig


def plot_user_saved_tracks_per_time_added(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['added_at'], y=df.index.T,
                             mode='markers', text=df['song_name'],
                             marker=dict(color=df['song_popularity'], size=12, showscale=True)
                             ))
    fig.update_layout(plot_bgcolor='white', title="Songs I added over time and their Spotify popularity",
                      title_x=0.5,
                      xaxis=dict(gridcolor='#DFEAF4', title='Date the song was added'),
                      yaxis=dict(gridcolor='#DFEAF4', title="Song popularity in Spotify"))
    return fig


def plot_uncommon_or_mainstream_tracks(df):
    fig = ff.create_table(df, height_constant=20)
    return fig


def plot_artists_or_albums_with_most_saved_tracks(df):
    fig = ff.create_table(df, height_constant=20, colorscale=[[0, '#1da843'], [.5, '#ffffff'], [1, '#ffffff']])
    return fig


def plot_related_artists(df):
    df = df[['name', 'followers', 'popularity', 'genres']]
    df = df.rename(columns={'name': 'Artist', 'followers': 'Followers', 'popularity': 'Popularity', 'genres': 'Genres'})
    fig = dash_table.DataTable(
        id='table',
        style_as_list_view=True,
        style_header={
            'backgroundColor': '#ebaf0c', 'color': 'white',
            'fontWeight': 'bold', 'fontSize': '20px'
        },
        style_cell={
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_cell_conditional=[
            {'if': {'column_id': 'Artist'},
             'width': '30%'},
            {'if': {'column_id': 'Followers'},
             'width': '15%'},
            {'if': {'column_id': 'Popularity'},
             'width': '15%'},
            {'if': {'column_id': 'Genres'},
             'width': '50px'},
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
        ],
        page_action='none',
        fixed_rows={'headers': True},
        style_table={'height': '300px', 'overflowY': 'auto', 'overflowX': 'auto', 'textAlign': 'left'},
        sort_action='native',
        filter_action='native',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
    )
    return fig


app = dash.Dash(name='app', server=server, url_base_pathname='/app/')


users = pd.read_csv('../data/users.csv')
user_id = users.iloc[-1]['id']
print('--------', user_id, '--------')

user_top_artists_across_periods, colors_last_mo_artists, colors_6_mo_artists = annotate_and_finalize_user_top_artists(user_id)
user_top_tracks_across_periods, colors_last_mo_tracks, colors_6_mo_tracks = annotate_and_finalize_user_top_tracks()

user_top_artists_data_long_term = pd.read_csv(f'../data/{user_id}/user_top_artists_data_long_term.csv')
user_top_artists_data_medium_term = pd.read_csv(f'../data/{user_id}/user_top_artists_data_medium_term.csv')
user_top_artists_data_short_term = pd.read_csv(f'../data/{user_id}/user_top_artists_data_short_term.csv')

top_genres_short_term = get_genre_count(user_top_artists_data_short_term)
top_genres_medium_term = get_genre_count(user_top_artists_data_medium_term)
top_genres_long_term = get_genre_count(user_top_artists_data_long_term)

top_genres_sunburst_data_short = create_sunburst_data(user_top_artists_data_short_term, top_genres_short_term)
top_genres_sunburst_data_medium = create_sunburst_data(user_top_artists_data_medium_term, top_genres_medium_term)
top_genres_sunburst_data_long = create_sunburst_data(user_top_artists_data_long_term, top_genres_long_term)

user_top_tracks_data_long_term = pd.read_csv(f'../data/{user_id}/user_top_tracks_data_long_term.csv')

user_top_tracks_data_long_term['song_duration_sec'] = user_top_tracks_data_long_term['song_duration']. \
    apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
user_top_tracks_data_long_term['album_release_date'] = \
    pd.to_datetime(user_top_tracks_data_long_term['album_release_date'])
user_top_tracks_data_long_term = user_top_tracks_data_long_term.rename(columns={
    'song_popularity': 'Song Popularity', 'album_release_date': 'Release Date',
    'artist_name': 'Artist', 'song_duration_sec': 'Song Duration in Seconds', 'song_name': 'Song'})

user_saved_tracks = pd.read_csv(f'../data/{user_id}/user_saved_tracks_data.csv')
user_saved_tracks = user_saved_tracks.sort_values(by='added_at')
user_saved_tracks = user_saved_tracks.reset_index()

user_saved_tracks['song_name_url'] = user_saved_tracks. \
    apply(lambda x: f'<a href="{x["song_external_url"]}">{x["song_name"]}</a>', axis=1)
uncommon_songs = user_saved_tracks.loc[user_saved_tracks['song_popularity'] > 0] \
    .sort_values(by='song_popularity', ascending=True).head(10)[['song_name_url', 'artist_name', 'song_popularity']]
uncommon_songs = uncommon_songs.rename(
    columns={'song_name_url': 'Song', 'artist_name': 'Artist', 'song_popularity': 'Popularity'})

mainstream_songs = user_saved_tracks.loc[user_saved_tracks['song_popularity'] > 0] \
    .sort_values(by='song_popularity', ascending=False).head(10)[['song_name_url', 'artist_name', 'song_popularity']]
mainstream_songs = mainstream_songs.rename(columns={'song_name_url': 'Song', 'artist_name': 'Artist',
                                                    'song_popularity': 'Popularity'})

user_saved_tracks['song_duration_sec'] = user_saved_tracks['song_duration']. \
    apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

user_saved_tracks['artist_name_url'] = user_saved_tracks. \
    apply(lambda x: f'<a href="{x["artist_external_url"]}">{x["artist_name"]}</a>', axis=1)
user_saved_tracks['album_name_url'] = user_saved_tracks. \
    apply(lambda x: f'<a href="{x["album_external_url"]}">{x["album_name"]}</a>', axis=1)
top_saved_artists = user_saved_tracks.groupby('artist_name_url').count(). \
    sort_values(by='song_name', ascending=False).head(10).reset_index()
top_saved_albums = user_saved_tracks.groupby('album_name_url').count(). \
    sort_values(by='song_name', ascending=False).head(10).reset_index()
top_saved_artists = top_saved_artists.rename(columns={'artist_name_url': 'Artist',
                                                      'index': 'Songs Saved'})[['Artist', 'Songs Saved']]
top_saved_albums = top_saved_albums.rename(columns={'album_name_url': 'Album',
                                                    'index': 'Songs Saved'})[['Album', 'Songs Saved']]

related_artists = pd.read_csv(f'../data/{user_id}/related_artists.csv')
related_artists_suggestions = related_artists.loc[~related_artists['external_url'].isin(
    user_saved_tracks['artist_external_url'].unique())]
related_artists_suggestions = related_artists_suggestions.loc[~related_artists_suggestions['external_url'].isin(
    user_top_artists_data_long_term['external_url'].unique()) ]
related_artists_suggestions = related_artists_suggestions.sort_values(by='followers', ascending=False)
related_artists_suggestions['genres'] = related_artists_suggestions['genres'].apply(
    lambda x: ', '.join(ast.literal_eval(x)))

########## DASH APP ##########



app.layout = html.Div([

    html.Div([
        html.Img(src=row['image_url'], style={'width': '8.33%', 'height': '100%'})
        for i, row in user_top_artists_data_long_term.head(12).iterrows()
    ],
        style={'height': '120px'}
    ),

    html.Div([
        '🎤 My Top Artists 🎤'
    ],
        style={'width': '58%', 'display': 'inline-block', 'float': 'left', 'textAlign': 'center',
               'fontFamily': 'helvetica', 'fontWeight': 'bold', 'fontSize': '22px', 'marginTop': '10px',
               'marginBottom': '10px'}
    ),

    html.Div([
        '🎶 My Top Tracks 🎶'
    ],
        style={'width': '40%', 'display': 'inline-block', 'float': 'right', 'textAlign': 'center',
               'fontFamily': 'helvetica', 'fontWeight': 'bold', 'fontSize': '22px', 'marginTop': '10px',
               'marginBottom': '10px'}
    ),

    html.Div([

        html.Div([
            plot_top_entity_across_periods(user_top_artists_across_periods,
                                           colors_6_mo_artists, colors_last_mo_artists,
                                           entity='artist'
                                           )
        ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left'}
        ),

        html.Div([
            dcc.Graph(figure=plot_artist_sunburst(top_genres_sunburst_data_long, title='All Time Top Genres'))
        ],
            style={'width': '33%', 'display': 'inline-block', 'float': 'left', 'position': 'static',
                   'margin': 0, 'padding': 0}
        ),

        html.Div([
            dcc.Graph(figure=plot_artist_sunburst(top_genres_sunburst_data_medium, title='Last 6 Months Top Genres'))
        ],
            style={'width': '33%', 'display': 'inline-block', 'float': 'left', 'position': 'static',
                   'margin': 0, 'padding': 0}
        ),

        html.Div([
            dcc.Graph(figure=plot_artist_sunburst(top_genres_sunburst_data_short, title='Last Month Top Genres'))
        ],
            style={'width': '33%', 'display': 'inline-block', 'float': 'left', 'position': 'static',
                   'margin': 0, 'padding': 0}
        ),

        html.Div([
            dcc.Graph(figure=plot_bubble(user_top_tracks_data_long_term))
        ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left'}
        ),

        html.Div([
            '🎧 My Library (Saved tracks) 🎧'
        ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left', 'textAlign': 'center',
                   'fontFamily': 'helvetica', 'fontWeight': 'bold', 'fontSize': '18px'}
        ),

        html.Div([
            f"I have ", html.B(user_saved_tracks.index.max() + 1), " saved tracks with a total duration of "
                                                                   f"{user_saved_tracks['song_duration_sec'].sum()} "
                                                                   f"seconds.",
            html.Br(),
            f"The tracks span across ", html.B(user_saved_tracks['album_name'].nunique()), " albums "
                                                                                           f"and ",
            html.B(user_saved_tracks['artist_name'].nunique()), " artists.",
            html.Br(),
            "The average Spotify Popularity of my tracks is {:.2f}.".format(
                user_saved_tracks['song_popularity'].mean()),
            html.Br(),
            f"The average duration of my tracks is {int(int(user_saved_tracks['song_duration_sec'].mean()) / 60)}:"
            f"{int(user_saved_tracks['song_duration_sec'].mean()) % 60} minutes."

        ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left',
                   'fontFamily': 'helvetica', 'textAlign': 'center'}
        ),

        html.Div([
            dcc.Graph(figure=plot_user_saved_tracks_per_time_added(user_saved_tracks))
        ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left'}
        ),

        html.Div([

            html.Div([
                html.Div([
                    'My Mainstream Songs (according to Spotify Popularity)'
                ],
                    style={'textAlign': 'center', 'fontFamily': 'helvetica'}
                ),
                dcc.Graph(figure=plot_uncommon_or_mainstream_tracks(mainstream_songs))
            ],
                style={'width': '49.5%', 'display': 'inline-block', 'float': 'left'}
            ),

            html.Div([
                html.Div([
                    'My Hidden Gems (according to Spotify Popularity)'
                ],
                    style={'textAlign': 'center', 'fontFamily': 'helvetica'}
                ),
                dcc.Graph(figure=plot_uncommon_or_mainstream_tracks(uncommon_songs))
            ],
                style={'width': '49.5%', 'display': 'inline-block', 'float': 'right'}
            ),
        ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left'}
        ),

        html.Div([

            html.Div([
                html.Div([
                    'My artists with the most saved tracks'
                ],
                    style={'textAlign': 'center', 'fontFamily': 'helvetica'}
                ),
                dcc.Graph(figure=plot_artists_or_albums_with_most_saved_tracks(top_saved_artists))
            ],
                style={'width': '49.5%', 'display': 'inline-block', 'float': 'left'}
            ),

            html.Div([
                html.Div([
                    'My albums with the most saved tracks'
                ],
                    style={'textAlign': 'center', 'fontFamily': 'helvetica'}
                ),
                dcc.Graph(figure=plot_artists_or_albums_with_most_saved_tracks(top_saved_albums))
            ],
                style={'width': '49.5%', 'display': 'inline-block', 'float': 'right'}
            ),
        ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left', 'marginTop': '20px'}
        ),

        html.Div([

            html.Div([
                'Related artists that are not in my top 50 artists nor in my library. Maybe I should check them.',
                html.Br(),
                '~ Feel free to filter and sort by column  ~'
            ],
                style={'textAlign': 'center', 'fontFamily': 'helvetica'}
            ),

            plot_related_artists(related_artists_suggestions),
            ],
            style={'width': '100%', 'display': 'inline-block', 'float': 'left', 'marginTop': '20px'}
        ),

    ],
        style={'width': '58%', 'display': 'inline-block', 'float': 'left'}
    ),

    html.Div([
        generate_table_top_tracks(user_top_tracks_across_periods, colors_last_mo_tracks, colors_6_mo_tracks),
    ],
        style={'width': '40%', 'display': 'inline-block', 'float': 'right'}
    ),

])

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
