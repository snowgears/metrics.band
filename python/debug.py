import pickle

if __name__ == "__main__":
    with open('backups.pkl', 'rb') as f:
        songs, artists, features = pickle.load(f)

    print(songs)
    print(artists)
    print(features)
