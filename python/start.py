import pickle
from SpotifyConnector import *
from PSQLConnector import *
from os import walk

import sched
import time

if __name__ == "__main__":

    with open('config.json') as f:
        config = json.load(f)

    psql = PSQLConnector(host=config['psql_host'], port=config['psql_port'], dbname=config['psql_dbname'],
                         dbuser=config['psql_dbuser'],
                         dbpassword=config['psql_dbpassword'])

    s = sched.scheduler(time.time, time.sleep)

    cache_files = []
    for (dirpath, dirnames, filenames) in walk('cache/'):
        cache_files.extend(filenames)
        break

    print(cache_files)

    spotify_connectors = []

    for cache_file in cache_files:
        spotify_connector = SpotifyConnector(cache_file)
        spotify_connector.get_token_from_cache()
        print(spotify_connector.get_current_user())
        spotify_connectors.append(spotify_connector)


    # spotify_connector1 = SpotifyConnector('kevin')
    # spotify_connector1.get_token_from_cache()
    # if spotify_connector1.access_token is None:
    #     print(spotify_connector1.get_spotipy_oath_uri())
    #     print('Enter url:')
    #     x = input()
    #     print(x)
    #     spotify_connector1.generate_access_tokens(x)
    #
    # spotify_user1 = spotify_connector1.get_current_user()
    # print(spotify_user1)
    #
    # spotify_connector2 = SpotifyConnector('tanner')
    # spotify_connector2.get_token_from_cache()
    # if spotify_connector2.access_token is None:
    #     print(spotify_connector2.get_spotipy_oath_uri())
    #     print('Enter url:')
    #     x = input()
    #     spotify_connector2.generate_access_tokens(x)
    #
    # spotify_user2 = spotify_connector2.get_current_user()
    # print(spotify_user2)
    #
    # spotify_connector3 = SpotifyConnector('scott')
    # spotify_connector3.get_token_from_cache()
    # if spotify_connector3.access_token is None:
    #     print(spotify_connector3.get_spotipy_oath_uri())
    #     print('Enter url:')
    #     x = input()
    #     spotify_connector3.generate_access_tokens(x)
    #
    # spotify_user3 = spotify_connector3.get_current_user()
    # print(spotify_user3)
    #
    # spotify_connector4 = SpotifyConnector('cheeto')
    # spotify_connector4.get_token_from_cache()
    # if spotify_connector4.access_token is None:
    #     print(spotify_connector4.get_spotipy_oath_uri())
    #     print('Enter url:')
    #     x = input()
    #     spotify_connector4.generate_access_tokens(x)
    #
    # spotify_user4 = spotify_connector4.get_current_user()
    # print(spotify_user4)
    #
    # print('\n')

    def query_spotify(sc):

        try:
            with open('payload_backups_1.pkl', 'rb') as f:
                payloads = pickle.load(f)
        except:
            payloads = []

        for spotify_connector in spotify_connectors:
            payload = [spotify_connector.get_spotify_snapshot_payload()]
            print(payload)
            payloads.extend(payload)

        payloads = list(filter(None, payloads))

        print('\n')
        print(len(payloads))
        print('\n')

        psql.connect()
        response = psql.insert_record_list(payloads)

        if -1 not in response:
            print('Succesfully sent ' + str(len(response)) + ' records.')
            print('Clearing Queue.')
            payloads.clear()
        else:
            print(str(response.count(-1)) + ' failed records.')

        print('Queue: ' + str(len(payloads)))

        with open('payload_backups_1.pkl', 'wb') as f:
            pickle.dump(payloads, f)

        s.enter(120, 1, query_spotify, (sc,))


    s.enter(1, 1, query_spotify, (s,))
    s.run()
