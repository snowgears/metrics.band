import sys
import os
import spotipy
import spotipy.util as util


class SpotifyConnector(object):
    def __init__(self, scope, username, debug=False):
        self.scope = scope
        self.username = username
        self.debug = debug

    def generate_spotify_token(self):
        try:
            # create token
            token = util.prompt_for_user_token(self.username, self.scope)
        except:
            # clear cache
            os.remove(f".cache-{self.username}")
            # create token
            token = util.prompt_for_user_token(self.username, self.scope)
        spotify_token = spotipy.Spotify(auth=token)
        return spotify_token

    def get_playing_song_and_artists(self):
        # generate spotify token
        spotify_token = self.generate_spotify_token()
        # get currently playing song
        current_song = spotify_token.current_user_playing_track()
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
        # generate spotify token
        spotify_token = self.generate_spotify_token()
        # get song features
        song_features = spotify_token.audio_features(song_id)
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
    scope = 'user-library-read user-read-recently-played user-read-currently-playing'

    spotify_connector = SpotifyConnector(scope=scope, username=username)
    current_song, current_artists = spotify_connector.get_playing_song_and_artists()
    print(current_song)
    print(current_artists)


if __name__ == "__main__":
    debug()
