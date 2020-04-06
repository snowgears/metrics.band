import pickle
from SpotifyConnector import *
import sched
import time


# with open('request_currently_results.pkl', 'rb') as f:  # Python 3: open(..., 'rb')
#     request_currently_results = pickle.load(f)
#
# features = []
# songs = []
#
# for i in request_currently_results:
#     features.extend(i['features'])
#     songs.extend(i['song'])
#
# print(songs)
# print(features)


def get_username_from_args():
    # get username from args
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()
    return username


if __name__ == "__main__":
    songs = []
    artists = []
    features = []

    s = sched.scheduler(time.time, time.sleep)
    spotify_connector1 = SpotifyConnector('kevin')

    print(spotify_connector1.get_spotipy_oath_uri())
    print('Enter url:')
    x = input()
    print(x)
    spotify_connector1.generate_access_tokens(x)

    spotify_user1 = spotify_connector1.get_current_user()

    print(spotify_user1)

    spotify_connector2 = SpotifyConnector('scott')

    print(spotify_connector2.get_spotipy_oath_uri())
    print('Enter url:')
    x = input()
    spotify_connector2.generate_access_tokens(x)

    spotify_user2 = spotify_connector2.get_current_user()

    print(spotify_user2)

    spotify_connector3 = SpotifyConnector('tanner')

    print(spotify_connector3.get_spotipy_oath_uri())
    print('Enter url:')
    x = input()
    spotify_connector3.generate_access_tokens(x)

    spotify_user3 = spotify_connector3.get_current_user()

    print(spotify_user3)


    def query_spotify(sc):
        current_song, current_artists = spotify_connector1.get_playing_song_and_artists()
        if current_song is not None:
            song_features = spotify_connector1.get_song_features(current_song['song_id'])

            print(current_song)
            print(current_artists)
            print(song_features)

            songs.extend([current_song])
            artists.extend(current_artists)
            features.extend([song_features])

            with open('backups_2.pkl', 'wb') as f:
                pickle.dump([songs, artists, features], f)

        current_song, current_artists = spotify_connector2.get_playing_song_and_artists()
        if current_song is not None:
            song_features = spotify_connector2.get_song_features(current_song['song_id'])

            print(current_song)
            print(current_artists)
            print(song_features)

            songs.extend([current_song])
            artists.extend(current_artists)
            features.extend([song_features])

            with open('backups_2.pkl', 'wb') as f:
                pickle.dump([songs, artists, features], f)

        current_song, current_artists = spotify_connector3.get_playing_song_and_artists()
        if current_song is not None:
            song_features = spotify_connector3.get_song_features(current_song['song_id'])

            print(current_song)
            print(current_artists)
            print(song_features)

            songs.extend([current_song])
            artists.extend(current_artists)
            features.extend([song_features])

            with open('backups_2.pkl', 'wb') as f:
                pickle.dump([songs, artists, features], f)

        s.enter(120, 1, query_spotify, (sc,))


    s.enter(1, 1, query_spotify, (s,))
    s.run()
