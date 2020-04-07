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

        # execute sql
        self.cursor.execute(sql)
        records = self.cursor.fetchall()

        for row in records:
            print(row)

        self.close_connection()
        return records

    # this is the only method needed to be externally called
    def insert_record_list(self, listen_snapshot_list):
        # inserts the user playback record list into the database

        listen_id_list = []
        try:
            for listen_snapshot in listen_snapshot_list:
                listen_id = self.insert_record(listen_snapshot, False)
                listen_id_list.append(listen_id)
                print(listen_snapshot)

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

            enduser_id = self.insert_enduser(user_email)

            artist_id_list = []
            for artist in artists:
                # insert each genre and return that a list of all genre ids
                genre_id_list = self.insert_genres(artist['genres'])
                # insert those genre ids as a genre set and return the genre_set_id
                genre_set_id = self.insert_genre_set(genre_id_list)
                # insert the artist along with the artists genre set id and get the artist_id
                artist_id = self.insert_artist(artist, genre_set_id)
                # add artist id to artist id list
                artist_id_list.append(artist_id)

            # insert the artist id list as a artist_set and get the artist_set_id
            artist_set_id = self.insert_artist_set(artist_id_list)
            # insert the song along with its artist_set_id
            song_id = self.insert_song(song_info, artist_set_id)
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
                self.cursor.execute(sql, (genre_name, genre_name))
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

    def insert_genre_set(self, genre_id_list):
        # inserts a record into the genre table
        # genre_list = list of genre ids

        # limit to 10 genres
        genre_id_list = genre_id_list[:10]

        # build out the insert queries for columns and values
        columns = []
        values = []
        i = 1
        for genre_id in genre_id_list:
            columns.append('genre' + str(i))
            values.append('%s')
            i = i + 1
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)

        # build out the select query for the WHERE conditional
        i = 0
        col_val_conditional = []
        for i in range(0, len(columns)):
            col_val_conditional.append(columns[i] + "=" + str(genre_id_list[i]))
        col_val_conditional_str = ' AND '.join(col_val_conditional)
        # print(col_val_conditional_str)

        try:
            # first check if the genre_set already exists in the table for those genre values
            genre_set_id = None
            sql = "SELECT genre_set_id FROM metrics_band.genre_set WHERE " + col_val_conditional_str;
            # execute the SELECT statement
            self.cursor.execute(sql)

            fetchone = self.cursor.fetchone();
            if (fetchone is not None):
                # get the generated id back
                genre_set_id = fetchone[0]
            else:
                # if there isnt a genre_set that already exists, create a new entry for that genre set
                sql = "INSERT INTO metrics_band.genre_set (" + columns_str + ") VALUES (" + values_str + ") RETURNING genre_set_id";
                # execute the INSERT statement
                self.cursor.execute(sql, genre_id_list)
                # get the generated id back
                genre_set_id = self.cursor.fetchone()[0]

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return genre_set_id

    def insert_artist(self, artist, genre_set_id):
        # inserts a record into the artist table

        try:
            spotify_artist_id = artist['artist_id']
            artist_name = artist['artist_name']

            sql = "INSERT INTO metrics_band.artist (name, spotify_id, genre_set_id) VALUES (%s, %s, %s) ON CONFLICT (spotify_id) DO UPDATE SET spotify_id=%s RETURNING artist_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (artist_name, spotify_artist_id, genre_set_id, spotify_artist_id))
            # get the generated id back
            artist_id = self.cursor.fetchone()[0]

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return artist_id

    def insert_artist_set(self, artist_id_list):
        # inserts a record into the artist set table
        # artist_id_list = list of genre ids

        # limit to 10 artists
        artist_id_list = artist_id_list[:10]

        # build out the insert queries for columns and values
        columns = []
        values = []
        i = 1
        for artist_id in artist_id_list:
            columns.append('artist' + str(i))
            values.append('%s')
            i = i + 1
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)

        # build out the select query for the WHERE conditional
        col_val_conditional = []
        for i in range(0, len(columns)):
            col_val_conditional.append(columns[i] + "=" + str(artist_id_list[i]))
        col_val_conditional_str = ' AND '.join(col_val_conditional)

        try:
            # first check if the artist_set already exists in the table for those artist id values
            artist_set_id = None
            sql = "SELECT artist_set_id FROM metrics_band.artist_set WHERE " + col_val_conditional_str;
            # execute the SELECT statement
            self.cursor.execute(sql)

            fetchone = self.cursor.fetchone();
            if (fetchone is not None):
                # get the generated id back
                artist_set_id = fetchone[0]
            else:
                # if there isnt a artist_set that already exists, create a new entry for that artist_set
                sql = "INSERT INTO metrics_band.artist_set (" + columns_str + ") VALUES (" + values_str + ") RETURNING artist_set_id";
                # execute the INSERT statement
                self.cursor.execute(sql, artist_id_list)
                # get the generated id back
                artist_set_id = self.cursor.fetchone()[0]

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return artist_set_id

    def insert_song(self, song_info, artist_set_id):
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

            sql = "INSERT INTO metrics_band.song (spotify_id, song_name, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, duration, artist_set_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (spotify_id) DO UPDATE SET spotify_id=%s RETURNING song_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (
                spotify_song_id, song_name, danceability, energy, key, loudness, mode, speechiness, acousticness,
                instrumentalness, liveness, valence, tempo, duration, artist_set_id, spotify_song_id))
            # get the generated id back
            song_id = self.cursor.fetchone()[0]

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        return song_id

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
