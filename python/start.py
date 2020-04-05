import pickle

with open('request_currently_results.pkl', 'rb') as f:  # Python 3: open(..., 'rb')
    request_currently_results = pickle.load(f)

print(request_currently_results[0]['features'])
print(request_currently_results[1]['features'])

for i in request_currently_results:
    print(i['features'])
