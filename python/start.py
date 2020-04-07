import pickle
from SpotifyConnector import *
from PSQLConnector import *

import sched
import time

if __name__ == "__main__":
    songs = []
    artists = []
    features = []



    s = sched.scheduler(time.time, time.sleep)

    spotify_connector1 = SpotifyConnector('kevin')
    spotify_connector1.get_token_from_cache()
    if spotify_connector1.access_token is None:
        print(spotify_connector1.get_spotipy_oath_uri())
        print('Enter url:')
        x = input()
        print(x)
        spotify_connector1.generate_access_tokens(x)

    spotify_user1 = spotify_connector1.get_current_user()
    print(spotify_user1)

    spotify_connector2 = SpotifyConnector('tanner')
    spotify_connector2.get_token_from_cache()
    if spotify_connector2.access_token is None:
        print(spotify_connector2.get_spotipy_oath_uri())
        print('Enter url:')
        x = input()
        spotify_connector2.generate_access_tokens(x)

    spotify_user2 = spotify_connector2.get_current_user()
    print(spotify_user2)

    spotify_connector3 = SpotifyConnector('scott')
    spotify_connector3.get_token_from_cache()
    if spotify_connector3.access_token is None:
        print(spotify_connector3.get_spotipy_oath_uri())
        print('Enter url:')
        x = input()
        spotify_connector3.generate_access_tokens(x)

    spotify_user3 = spotify_connector3.get_current_user()
    print(spotify_user3)

    spotify_connector4 = SpotifyConnector('cheeto')
    spotify_connector4.get_token_from_cache()
    if spotify_connector4.access_token is None:
        print(spotify_connector4.get_spotipy_oath_uri())
        print('Enter url:')
        x = input()
        spotify_connector4.generate_access_tokens(x)

    spotify_user4 = spotify_connector4.get_current_user()
    print(spotify_user4)

    print('\n')


    def query_spotify(sc):
        payloads = []

        payload1 = [spotify_connector1.get_spotify_snapshot_payload()]
        payload2 = [spotify_connector2.get_spotify_snapshot_payload()]
        payload3 = [spotify_connector3.get_spotify_snapshot_payload()]
        payload4 = [spotify_connector4.get_spotify_snapshot_payload()]

        payloads.extend(payload1)
        payloads.extend(payload2)
        payloads.extend(payload3)
        payloads.extend(payload4)

        payloads_processed = list(filter(None, payloads))

        print('\n')
        print(payloads_processed)
        print('\n')

        psql.connect()
        psql.insert_record_list(payloads_processed)

        payloads.clear()

        # with open('payloads.pkl', 'wb') as f:
        #     pickle.dump(payloads_processed, f)
        s.enter(120, 1, query_spotify, (sc,))


    s.enter(1, 1, query_spotify, (s,))
    s.run()
