from SpotifyConnector import *

if __name__ == "__main__":
    print('Enter name:')
    name = input()

    spotify_connector = SpotifyConnector(name)
    print(spotify_connector.get_spotipy_oath_uri())
    print('Enter url:')
    code = input()
    print(code)

    spotify_connector.generate_access_tokens(code)

    print(spotify_connector.get_current_user())
