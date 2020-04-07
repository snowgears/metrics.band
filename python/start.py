import pickle
from SpotifyConnector import *
from PSQLConnector import *

import sched
import time

if __name__ == "__main__":

    with open('config.json') as f:
        config = json.load(f)

    psql = PSQLConnector(host=config['psql_host'], port=config['psql_port'], dbname=config['psql_dbname'],
                         dbuser=config['psql_dbuser'],
                         dbpassword=config['psql_dbpassword'])

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

        try:
            with open('payload_backups.pkl', 'rb') as f:
                payloads = pickle.load(f)
        except:
            payloads = []

        payload1 = [spotify_connector1.get_spotify_snapshot_payload()]
        payload2 = [spotify_connector2.get_spotify_snapshot_payload()]
        payload3 = [spotify_connector3.get_spotify_snapshot_payload()]
        payload4 = [spotify_connector4.get_spotify_snapshot_payload()]

        payloads.extend(payload1)
        payloads.extend(payload2)
        payloads.extend(payload3)
        payloads.extend(payload4)

        payloads = list(filter(None, payloads))

        print('\n')
        print(len(payloads))
        # print(payloads)
        print(payload1)
        print(payload2)
        print(payload3)
        print(payload4)
        print('\n')

        # psql.connect()
        # response = psql.insert_record_list(payloads)
        #
        # if list(dict.fromkeys(response))[0] != -1:
        #     print('No error. Clearing Queue.')
        #     payloads.clear()

        print('Queue: ' + str(len(payloads)))

        with open('payload_backups.pkl', 'wb') as f:
            pickle.dump(payloads, f)

        s.enter(120, 1, query_spotify, (sc,))


    s.enter(1, 1, query_spotify, (s,))
    s.run()
