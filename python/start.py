import pickle
from SpotifyConnector import *
from PSQLConnector import *
from os import walk

import sched
import time

# run every 120 seconds
QUERY_INTERVAL = 120
PICKLE_FILENAME = 'payload_backups_2.pkl'

if __name__ == "__main__":

    # load spotify and psql credentials from config.json

    with open('config.json') as f:
        config = json.load(f)

    # initialize psqlconnector

    psql = PSQLConnector(host=config['psql_host'], port=config['psql_port'], dbname=config['psql_dbname'],
                         dbuser=config['psql_dbuser'],
                         dbpassword=config['psql_dbpassword'])

    # create scheduler
    s = sched.scheduler(time.time, time.sleep)


    def query_spotify(sc):

        # load spotify profiles from cache
        cache_files = []
        for (dirpath, dirnames, filenames) in walk('cache/'):
            cache_files.extend(filenames)
            break

        print(cache_files)

        # initialize spotifyconnectors for each cached profile
        spotify_connectors = []

        while True:
            try:
                for cache_file in cache_files:
                    spotify_connector = SpotifyConnector(cache_file)
                    spotify_connector.get_token_from_cache()
                    print(spotify_connector.get_current_user()['display_name'])
                    spotify_connectors.append(spotify_connector)
            except:
                time.sleep(30)
                continue
            else:
                break

        print('-' * 50)

        # load a backup pickle if one exists
        try:
            with open(PICKLE_FILENAME, 'rb') as f:
                payloads = pickle.load(f)
        except:
            payloads = []

        # generate spotify snapshot payload
        for spotify_connector in spotify_connectors:
            try:
                payload = [spotify_connector.get_spotify_snapshot_payload()]
                print('\n')
                print(payload)
                payloads.extend(payload)
            except:
                time.sleep(30)
                print('snapshot error')

        payloads = list(filter(None, payloads))

        print('\n')
        print(len(payloads))
        print('\n')

        # send that shit over to psql db
        psql.connect()
        response = psql.insert_record_list(payloads)

        # backup failed syncs
        if -1 not in response:
            print('Succesfully sent ' + str(len(response)) + ' records.')
            print('Clearing Queue.')
            payloads.clear()
        else:
            print(str(response.count(-1)) + ' failed records.')

        print('Queue: ' + str(len(payloads)))

        with open(PICKLE_FILENAME, 'wb') as f:
            pickle.dump(payloads, f)

        print('-' * 50)

        s.enter(QUERY_INTERVAL, 1, query_spotify, (sc,))


    s.enter(1, 1, query_spotify, (s,))
    s.run()
