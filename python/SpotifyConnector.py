import sys
import os
import spotipy
import spotipy.util as util


class SpotifyConnector(object):
    """
    A Spotify connector with helper methods using spotipy

    ...

    Attributes
    ----------
    scope : str
        space separated string of spotify scope
    username : int
        Spotify username
    debug: bool
        debug flag

    Methods
    -------
    generate_spotipy_obj():
        authenticates user with Spotify and returns an authenticated spotipy object
    get_playing_song_and_artists():
        gets currently playing song from Spotify and returns a song object and an artists object.
    get_song_features(song_id):
        returns Spotify song features given a Spotify song ID
    """

    def __init__(self, username, debug=False):
        """
        Initializes SpotifyConnector class

        :param scope: str
        :param username: int
        :param debug: bool, optional
        """
        self.scope = 'user-library-read user-read-recently-played user-read-currently-playing'
        self.username = username
        self.debug = debug

    def generate_spotipy_obj(self):
        """
        Creates a Spotify auth token and generates a Spotipy obj on successful authentication
        :return: Spotipy Object
        :rtype: object
        """
        try:
            # create token
            token = util.prompt_for_user_token(self.username, self.scope)
        except:
            # clear cache
            os.remove(f".cache-{self.username}")
            # create token
            token = util.prompt_for_user_token(self.username, self.scope)
        spotipy_obj = spotipy.Spotify(auth=token)
        return spotipy_obj

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
        if current_song is not None:
            # get current song artists
            artists = current_song['item']['artists']

            # parse artists
            artists_list = []
            for artist in artists:
                artist_obj = {
                    'artist_name': artist['name'],
                    'artist_spotify_id': artist['id']
                }
                artists_list.extend([artist_obj])

            # parse song info
            song_obj = {
                'username': self.username,
                'song_id': current_song['item']['id'],
                'song_name': current_song['item']['name'],
                'song_popularity': current_song['item']['popularity'],
                'song_timestamp': current_song['timestamp'],
                'processed': False
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

    spotify_connector = SpotifyConnector(username=username)
    current_song, current_artists = spotify_connector.get_playing_song_and_artists()
    print(current_song)
    print(current_artists)


if __name__ == "__main__":
    debug()
