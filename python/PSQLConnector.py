import psycopg2
import datetime

class PSQLConnector(object):
    def __init__(self, host, port, dbname, dbuser, dbpassword):
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.host = host
        self.port = port

        self.connection = None
        self.cursor = None

    def connect(self):
        # TODO try excepts my dude
        connection = psycopg2.connect(host=self.host, port=self.port, database=self.dbname, user=self.dbuser,
                                      password=self.dbpassword)
        self.connection = connection
        self.cursor = connection.cursor()
        return self.connection, self.cursor

    def close_connection(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()

    def sql_query(self, sql):
        # establish connection
        connection = self.connect()
        cursor = connection.cursor()

        # execute sql
        cursor.execute(sql)
        records = cursor.fetchall()

        for row in records:
            print(row)

        self.close_connection(connection=connection, cursor=cursor)

    # this is the only method needed to be externally called
    def insert_record_list(self, listen_snapshot_list):
        # inserts the user playback record list into the database

        listen_id_list = []
        try:
            for listen_snapshot in listen_snapshot_list:
                listen_id = self.insert_record(listen_snapshot, False)
                listen_id_list.append(listen_id)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            self.close_connection()

        return listen_id_list

    # this is the only method needed to be externally called
    def insert_record(self, listen_snapshot, close_connection):
        # inserts the user playback record into the database

        listen_id = -1
        try:
            user_email = listen_snapshot['email']
            listen_timestamp = listen_snapshot['listen_timestamp']
            song_info = listen_snapshot['song_info']
            artists = song_info['artists']

            # insert the enduser
            enduser_id = self.insert_enduser(user_email)
            # insert the album
            album_id = self.insert_album(song_info)
            # insert the song
            song_id = self.insert_song(song_info, album_id)

            for artist in artists:
                # insert the artist and return artist_id
                artist_id = self.insert_artist(artist)

                # insert a song_artist record for every artist
                song_artist_id = self.insert_song_artist(song_id, artist_id)

                # insert each genre and return that a list of all genre ids
                genre_id_list = self.insert_genres(artist['genres'])

                for genre_id in genre_id_list:
                    # insert an artist_genre record for every genre id
                    artist_genre_id = self.insert_artist_genre(artist_id, genre_id)

            # insert the listen record
            listen_id = self.insert_listen_history(enduser_id, listen_timestamp, song_id)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if close_connection:
                self.close_connection()

        return listen_id

    def insert_enduser(self, user_email):
        # inserts a record into the enduser table

        enduser_id = -1
        try:
            sql = "INSERT INTO metrics_band.enduser (email) VALUES (%s) ON CONFLICT (email) DO UPDATE SET email=%s RETURNING enduser_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (user_email, user_email))
            # get the generated id back
            enduser_id = self.cursor.fetchone()[0]
            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return enduser_id

    def insert_genres(self, genres):
        # inserts a record into the genre table for each genre in genres
        # genres = genres portion of main json object

        genre_id_list = []
        for genre_name in genres:
            try:
                sql = "INSERT INTO metrics_band.genre (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=%s RETURNING genre_id";
                # execute the INSERT statement
                self.cursor.execute(sql, (genre_name,genre_name))
                # get the generated id back
                genre_id = self.cursor.fetchone()[0]
                genre_id_list.append(genre_id)
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

        try:
            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return genre_id_list

    def insert_artist(self, artist):
        # inserts a record into the artist table

        try:
            spotify_artist_id = artist['artist_id']
            artist_name = artist['artist_name']

            sql = "INSERT INTO metrics_band.artist (name, spotify_id) VALUES (%s, %s) ON CONFLICT (spotify_id) DO UPDATE SET spotify_id=%s RETURNING artist_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (artist_name,spotify_artist_id, spotify_artist_id))
            # get the generated id back
            artist_id = self.cursor.fetchone()[0]

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return artist_id

    def insert_album(self, song_info):
        # inserts a record into the album table

        album_id = -1
        try:
            spotify_album_id = song_info['album_id']
            album_name = song_info['album_name']
            release_date = song_info['release_date']

            sql = "INSERT INTO metrics_band.album (spotify_id, album_name, release_date) VALUES (%s, %s, %s) ON CONFLICT (spotify_id) DO UPDATE SET spotify_id=%s RETURNING album_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (spotify_album_id, album_name, release_date, spotify_album_id))
            # get the generated id back
            album_id = self.cursor.fetchone()[0]

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return album_id

    def insert_song_artist(self, song_id, artist_id):
        # inserts a record into the song_artist table

        song_artist_id = -1
        try:
            sql = "INSERT INTO metrics_band.song_artist (song_id, artist_id) VALUES (%s, %s) ON CONFLICT ON CONSTRAINT CST_SONG_ARTIST DO UPDATE SET song_id=%s RETURNING song_artist_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (song_id, artist_id, song_id))
            # get the generated id back
            song_artist_id = self.cursor.fetchone()[0]
            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return song_artist_id

    def insert_song(self, song_info, album_id):
        # inserts a record into the song table

        try:
            spotify_song_id = song_info['song_id']
            song_name = song_info['song_name']
            danceability = song_info['danceability']
            energy = song_info['energy']
            key = song_info['key']
            loudness = song_info['loudness']
            mode = song_info['mode']
            speechiness = song_info['speechiness']
            acousticness = song_info['acousticness']
            instrumentalness = song_info['instrumentalness']
            liveness = song_info['liveness']
            valence = song_info['valence']
            tempo = song_info['tempo']
            duration = song_info['duration']

            sql = "INSERT INTO metrics_band.song (spotify_id, song_name, album_id, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (spotify_id) DO UPDATE SET spotify_id=%s RETURNING song_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (spotify_song_id, song_name, album_id, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, duration, spotify_song_id))
            # get the generated id back
            song_id = self.cursor.fetchone()[0]

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return song_id

    def insert_artist_genre(self, artist_id, genre_id):
        # inserts a record into the artist_genre table

        artist_genre_id = -1
        try:
            sql = "INSERT INTO metrics_band.artist_genre (artist_id, genre_id) VALUES (%s, %s) ON CONFLICT ON CONSTRAINT CST_ARTIST_GENRE DO UPDATE SET artist_id=%s RETURNING artist_genre_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (artist_id, genre_id, artist_id))
            # get the generated id back
            artist_genre_id = self.cursor.fetchone()[0]
            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return artist_genre_id


    def insert_listen_history(self, user_id, listen_timestamp, song_id):
        # inserts a record into the listen_history table

        listen_id = -1
        try:
            timestamp = datetime.datetime.fromtimestamp(listen_timestamp / 1e3)

            sql = "INSERT INTO metrics_band.listen_history (enduser_id, timestamp, song_id) VALUES (%s, %s, %s) RETURNING listen_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (user_id, timestamp, song_id))
            # get the generated id back
            listen_id = self.cursor.fetchone()[0]
            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return listen_id
