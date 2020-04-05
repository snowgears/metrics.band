import sys
import os
import spotipy
import spotipy.util as util
from pytz import timezone
import pandas as pd
import dateutil.parser
import datetime
import sched
import time
import pickle

scope = 'user-library-read user-read-recently-played user-read-currently-playing'

# get username from args
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()



# request_recently_results = []
# s = sched.scheduler(time.time, time.sleep)
# def query_spotify_recently_played(sc):
#     print("Doing stuff...")
#     # do your stuff
#     if token:
#         # auth token
#         sp = spotipy.Spotify(auth=token)
#
#         # get currently played songs
#         results = sp.current_user_recently_played(limit=50)
#
#         # append to list
#         request_recently_results.extend(results['items'])
#         print(len(request_recently_results))
#         with open('request_recently_results.pkl', 'wb') as f:
#             pickle.dump(request_recently_results, f)
#
#         # loop through results
#         # for item in results['items']:
#         #     track = item['track']
#         # parse date time from request response
#         # date = dateutil.parser.parse(item['played_at'])
#         # convert date to PST (for debugging)
#         # date_pst = date.astimezone(timezone('US/Pacific'))
#         # print(str(date_pst) + ': ' + track['name'] + ' - ' + track['artists'][0]['name'])
#
#     else:
#         print("Can't get token for", username)
#     s.enter(3600, 1, query_spotify_recently_played, (sc,))
#
#
# s.enter(1, 1, query_spotify_recently_played, (s,))
# s.run()


request_currently_results = []
s = sched.scheduler(time.time, time.sleep)


def query_spotify_currently_played(sc):
    print("Doing stuff...")
    try:
        # create token
        token = util.prompt_for_user_token(username, scope)
    except:
        # clear cache
        os.remove(f".cache-{username}")
        # create token
        token = util.prompt_for_user_token(username, scope)

    # do your stuff
    if token:
        # auth token
        sp = spotipy.Spotify(auth=token)

        # get currently played song
        results_playing = sp.current_user_playing_track()

        song_id = results_playing['item']['id']

        # get song features
        results_features = sp.audio_features(song_id)

        result_dict = {
            'song': results_playing,
            'features': results_features
        }

        request_currently_results.extend([result_dict])
        print(len(request_currently_results))
        with open('request_currently_results.pkl', 'wb') as f:
            pickle.dump(request_currently_results, f)


    else:
        print("Can't get token for", username)
    s.enter(120, 1, query_spotify_currently_played, (sc,))


s.enter(1, 1, query_spotify_currently_played, (s,))
s.run()
