import pickle

with open('request_currently_results.pkl', 'rb') as f:  # Python 3: open(..., 'rb')
    request_currently_results = pickle.load(f)

features = []
songs = []

for i in request_currently_results:
    features.extend(i['features'])
    songs.extend(i['song'])

print(songs)
print(features)

