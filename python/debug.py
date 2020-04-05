import pickle
import pandas as pd

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

if __name__ == "__main__":
    with open('backups.pkl', 'rb') as f:
        songs, artists, features = pickle.load(f)

    songs_df = pd.DataFrame(songs)
    artists_df = pd.DataFrame(artists)
    features_df = pd.DataFrame(features)

    print(songs_df)
    print(artists_df)
    print(features_df)
