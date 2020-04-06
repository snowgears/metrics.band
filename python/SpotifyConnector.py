import sys
import spotipy
from spotipy import oauth2
import json
import time


# TODO add debug printing

class SpotifyConnector(object):
    """
    A Spotify connector with helper methods using spotipy

    ...

    Attributes
    ----------
    scope : str
        space separated string of spotify scope
    cache : str
        cache location
    debug: bool
        debug flag

    Methods
    -------
    generate_spotipy_obj():
        authenticates user with Spotify and returns an authenticated spotipy object. object used to query user data.
    get_playing_song_and_artists():
        gets currently playing song from Spotify and returns a song object and an artists object.
    get_song_features(song_id):
        returns Spotify song features given a Spotify song ID
    """

    def __init__(self, cache, debug=False):
        """
        Initializes SpotifyConnector class

        :param scope: str
        :param cache: str
        :param debug: bool, optional
        """
        self.scope = 'user-library-read user-read-recently-played user-read-currently-playing'
        self.cache = '.' + cache
        self.debug = debug

        # TODO put int try catch to let user know that they need config.json
        # load client id/secret and redirect URI from config.json
        with open('config.json') as f:
            config = json.load(f)

        self.sp_oauth = oauth2.SpotifyOAuth(config['SPOTIFY_CLIENT_ID'], config['SPOTIFY_CLIENT_SECRET'],
                                            config['SPOTIFY_REDIRECT_URI'], scope=self.scope, cache_path=self.cache)

        self.access_token = ""
        self.refresh_token = ""

        self.current_user = None

        self.previous_payload = {}
        self.previous_playing_song = {
            'song_id': None
        }
        self.previous_artist_list = {}
        self.previous_song_features = {}
        self.previous_artist_info = {}

    def get_spotipy_oath_uri(self):
        auth_url = self.sp_oauth.get_authorize_url()
        return auth_url

    def generate_access_tokens(self, url):
        code = self.sp_oauth.parse_response_code(url)
        token_info = self.sp_oauth.get_access_token(code)
        self.access_token = token_info['access_token']
        self.refresh_token = token_info['refresh_token']

    def refresh_access_tokens(self):
        token_info = self.sp_oauth.refresh_access_token(self.refresh_token)
        self.access_token = token_info['access_token']
        self.refresh_token = token_info['refresh_token']

    def get_token_from_cache(self):
        token_info = self.sp_oauth.get_cached_token()
        self.access_token = token_info['access_token']
        self.refresh_token = token_info['refresh_token']

    def generate_spotipy_obj(self):
        """
        Refreshes Spotify auth token and generates a Spotipy obj on successful authentication
        :return: Spotipy Object
        :rtype: object
        """
        self.refresh_access_tokens()
        spotipy_obj = spotipy.Spotify(auth=self.access_token)
        return spotipy_obj

    def get_current_user(self):
        """
        TODO document this shit
        :return:
        """
        # generate spotipy obj
        spotipy_obj = self.generate_spotipy_obj()

        self.current_user = spotipy_obj.current_user()
        return self.current_user

    def get_playing_song_and_artists(self):
        """
        Queries Spotify for current song, and parses data into a song object and a list of artists
        :return: song_obj/artist_list
        :rtype: object, list
        """
        # generate spotipy obj
        spotipy_obj = self.generate_spotipy_obj()
        # get currently playing song
        current_song = spotipy_obj.current_user_playing_track()

        if current_song is not None and current_song['is_playing'] and current_song[
            'currently_playing_type'] == 'track':

            # get current song artists
            artists = current_song['item']['artists']

            # parse artists
            artists_list = []
            for artist in artists:
                artist_obj = {
                    'artist_name': artist['name'],
                    'artist_spotify_id': artist['id'],
                    'song_id': current_song['item']['id']
                }
                artists_list.extend([artist_obj])

            # parse song info
            song_obj = {
                'username': self.current_user['id'],
                'song_id': current_song['item']['id'],
                'song_name': current_song['item']['name'],
                'song_popularity': current_song['item']['popularity'],
                'song_timestamp': int(time.time()) * 1000,
                'processed': False,
                'artists': [d['artist_spotify_id'] for d in artists_list],
                'type': current_song['currently_playing_type']
            }
            return song_obj, artists_list
        return None, None

    def get_song_features(self, song_id):
        """
        Queries Spotify for song features given a song_id
        :param song_id: int
        :return: song_features_obj
        :rtype: object
        """
        # generate spotipy obj
        spotipy_obj = self.generate_spotipy_obj()
        # get song features
        song_features = spotipy_obj.audio_features(song_id)
        # parse song features
        song_features_obj = {
            'song_id': song_id,
            'danceability': song_features[0]['danceability'],
            'energy': song_features[0]['energy'],
            'key': song_features[0]['key'],
            'loudness': song_features[0]['loudness'],
            'mode': song_features[0]['mode'],
            'speechiness': song_features[0]['speechiness'],
            'acousticness': song_features[0]['acousticness'],
            'instrumentalness': song_features[0]['instrumentalness'],
            'liveness': song_features[0]['liveness'],
            'valence': song_features[0]['valence'],
            'tempo': song_features[0]['tempo'],
            'duration': song_features[0]['duration_ms']
        }

        return song_features_obj

    def get_artists_info(self, artists_list):
        # generate spotipy obj
        spotipy_obj = self.generate_spotipy_obj()
        # get song features
        artists_info = spotipy_obj.artists(artists_list)

        artists_info_list = []

        for artist_info in artists_info['artists']:
            artist_info_obj = {
                'artist_id': artist_info['id'],
                'artist_name': artist_info['name'],
                'popularity': artist_info['popularity'],
                'generes': artist_info['genres']
            }

            artists_info_list.extend([artist_info_obj])

        return artists_info_list

    def get_spotify_snapshot_payload(self):
        # todo consolidate all datapoints into this single one
        current_song, current_artists = self.get_playing_song_and_artists()
        if current_song is not None:
            if current_song['song_id'] != self.previous_playing_song['song_id']:
                song_features = self.get_song_features(current_song['song_id'])
                artists_info = self.get_artists_info(current_song['artists'])

            else:
                song_features = self.previous_song_features
                artists_info = self.previous_artist_info

            payload = {
                'username': current_song['username'],
                'email': self.current_user['email'],
                'listen_timestamp': current_song['song_timestamp'],
                'song_info': {
                    'song_id': current_song['song_id'],
                    'song_name': current_song['song_name'],
                    'song_popularity': current_song['song_popularity'],
                    'danceability': song_features['danceability'],
                    'energy': song_features['energy'],
                    'key': song_features['key'],
                    'loudness': song_features['loudness'],
                    'mode': song_features['mode'],
                    'speechiness': song_features['speechiness'],
                    'acousticness': song_features['acousticness'],
                    'instrumentalness': song_features['instrumentalness'],
                    'liveness': song_features['liveness'],
                    'valence': song_features['valence'],
                    'tempo': song_features['tempo'],
                    'duration': song_features['duration'],
                    'artists': artists_info
                }
            }

            self.previous_payload = payload
            self.previous_playing_song = current_song
            self.previous_artist_list = current_artists
            self.previous_song_features = song_features
            self.previous_artist_info = artists_info


            return payload

        return None


def get_username_from_args():
    # get username from args
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()
    return username


def debug():
    username = get_username_from_args()

    spotify_connector = SpotifyConnector('testcache')
    current_song, current_artists = spotify_connector.get_playing_song_and_artists()
    print(current_song)
    print(current_artists)


if __name__ == "__main__":
    debug()
