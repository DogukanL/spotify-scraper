from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from credentials import *
from os.path import isdir, exists
from os import mkdir
from playlist import Playlist
from track import Track
from csv import DictWriter
import pandas as pd
from itertools import islice
import argparse

"""
Scrapes spotify users songs and audio features and writes them to a csv file
"""


def to_chunks(iterable, chunk_size):
    it = iter(iterable)
    piece = list(islice(it, chunk_size))
    while piece:
        yield piece
        piece = list(islice(it, chunk_size))


def get_prefix(sp, user_id):
    user = sp.user(user_id)
    try:
        name = '_'.join(user['display_name'].split(' '))
        return name
    except AttributeError:
        return user_id


def get_playlists(sp, user):
    playlists = sp.user_playlists(user)
    while playlists:
        for playlist in playlists['items']:
            yield Playlist(playlist)
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None


def get_tracks_from_playlist(sp, playlist_id):
    tracks = sp.playlist_tracks(playlist_id, limit=100)
    while tracks:
        yield tuple(track for track in tracks['items'] if track['track'])
        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            tracks = None
            
def get_features(sp, user):
    prefix = get_prefix(sp, user)
    path = f'./data/{prefix}_features.csv'
        
    features_frame = pd.DataFrame(columns=['id', 'danceability', 'energy', 'key',
                                           'loudness', 'mode', 'speechiness',
                                           'acousticness', 'instrumentalness',
                                           'liveness', 'valence', 'tempo',
                                           'type', 'uri', 'track_href',
                                           'analysis_url', 'duration_ms', 'time_signature'])
    features_frame.set_index('id')
    print(f'Getting audio features for {prefix}...')
    
    for playlist in get_playlists(sp, user):
        for tracks in get_tracks_from_playlist(sp, playlist.id):
            # get ids of tracks
            ids = [track['track']['id'] for track in tracks]
            # remove None
            ids = list(
                filter(
                    lambda n: n is not None, ids
                )
            )
            # get track features
            data = sp.audio_features(ids)
            # filter data in case there are empty tracks
            data = list(
                filter(
                    lambda n: n is not None, data
                )
            )

            frame = pd.DataFrame(data)
            cols = frame.columns.to_list()
            cols.insert(0, cols.pop(cols.index('id')))
            frame = frame[cols]
            frame.set_index('id')

            features_frame = pd.concat([features_frame, frame], ignore_index=True)

    features_frame = features_frame.drop(columns=['type', 'uri', 'track_href',
                                                      'analysis_url', 'time_signature'])
    features_frame.to_csv(path, index=False)
    print(f'Done with features for {prefix}')
    
def get_tracks(sp, user):
    prefix = get_prefix(sp, user)
    path = f'./data/{prefix}_tracks.csv'
    fieldnames = (
            'id', 'name','album_id', 'album_name',
            'album_type', 'release_date', 'artists',
            'popularity', 'is_episode', 'is_explicit',
            'type', 'preview_url', 'playlist_id',
            'added_at', 'added_by')
    
    print(f'Getting tracks for {prefix}...')
    with open(path, 'w+') as file:
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for playlist in get_playlists(sp, user):
            for tracks in get_tracks_from_playlist(sp, playlist.id):
                tracks = [Track(track) for track in tracks]
                for track in tracks:
                    writer.writerow({
                        'id': track.id, 'name': track.name, 'album_id': track.album_id, 
                        'album_name': track.album_name, 'album_type': track.album_type,
                        'release_date': track.release_date, 'artists': track.artists_names,
                        'popularity': track.popularity, 'is_episode': track.is_episode,
                        'is_explicit': track.is_explicit, 'type': track.type,
                        'preview_url': track.preview_url, 'playlist_id': playlist.id,
                        'added_at': track.added_at, 'added_by': track.added_by})
    print(f'Done with tracks for {prefix}')

def main():
    oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )
    sp = Spotify(auth_manager=oauth)

    parser = argparse.ArgumentParser(description='Scrape spotify users\' '
                                    'tracks and audio features '
                                    'and saves them into a csv file.',
                                    allow_abbrev=False)

    parser.add_argument('-u', '--users',
                        nargs='+',
                        help='lits of user(s)',
                        required=True)

    parser.add_argument('-f', '--features',
                        action='store_true',
                        help='gets features',
                        required=False)

    parser.add_argument('-t', '--tracks',
                        action='store_true',
                        help='gets tracks',
                        required=False)
    
    args = parser.parse_args()
    
    if not exists('./data'):
        mkdir('./data')

    for user in args.users:
        if args.features:
            get_features(sp, user)
        if args.tracks:
            get_tracks(sp, user)

if __name__ == '__main__':
    main()
