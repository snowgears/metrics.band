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
    username = get_username_from_args()
    spotify_connector = SpotifyConnector(username=username)


    def query_spotify(sc):
        current_song, current_artists = spotify_connector.get_playing_song_and_artists()
        song_features = spotify_connector.get_song_features(current_song['song_id'])

        print(current_song)
        print(current_artists)
        print(song_features)

        songs.extend([current_song])
        artists.extend(current_artists)
        features.extend([song_features])

        with open('backups.pkl', 'wb') as f:
            pickle.dump([songs, artists, features], f)

        print(len(songs))
        s.enter(120, 1, query_spotify, (sc,))


    s.enter(1, 1, query_spotify, (s,))
    s.run()
