import psycopg2


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
    def insert_record(self, listen_snapshot):
        # inserts the user playback record into the database
        # this is the only method needed to be externally called

        # TODO DELETE THIS. IN THE FUTURE WILL COME OUT OF LISTEN_SNAPSHOT PAYLOAD
        user_email = 'tannerembry95@gmail.com' 

        # build out json object for current playing song of user and all info we need
        playing_json = self.build_json_for_song(user_email)

        listen_id = -1
        try:
            enduser_id = self.insert_enduser(user_email)
            #TODO for every artist in the artist json, get the genres section of that artist and populate the genres as well as a genre_set per artist
            genre_id_list = self.insert_genre(playing_json['genres']) # TODO parse out the genres section from the json object
            genre_set_id = self.insert_genre_set(genre_id_list)
            self.insert_artist(genre_set_id)
            self.insert_artist_set()
            self.insert_song()
            listen_id = self.insert_listen_history()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            self.close_connection()
    
        return listen_id

    def insert_enduser(self, user_email):
        # inserts a record into the enduser table

        enduser_id = -1
        try:
            sql = "INSERT INTO metrics_band.enduser (email) VALUES (%s) RETURNING enduser_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (user_email))
            # get the generated id back
            enduser_id = self.cursor.fetchone()[0]
            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
        return enduser_id

    def insert_genre(self, genres):
        # inserts a record into the genre table for each genre in genres
        # genres = genres portion of main json object

        genre_id_list = []
        for genre_name in genres['names']:
            try:
                sql = "INSERT INTO metrics_band.genre (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=%s RETURNING genre_id";
                # execute the INSERT statement
                self.cursor.execute(sql, (genre_name,genre_name))
                # get the generated id back
                genre_id = self.cursor.fetchone()[0]
                print(genre_id)
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

        # build out the insert queries for columns and values
        columns = []
        values = []
        i = 1
        for genre_id in genre_id_list:
            columns.append('genre'+str(i))
            values.append('%s')
            i = i + 1
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)

        # build out the select query for the WHERE conditional
        col_val_conditional = []
        for i in range(0, len(columns)):
            col_val_conditional.append(columns[i] + "="+ str(genre_id_list[i]))
        col_val_conditional_str = ' AND '.join(col_val_conditional)
        # print(col_val_conditional_str)

        try:
            # first check if the genre_set already exists in the table for those genre values
            genre_set_id = -1
            sql = "SELECT genre_set_id FROM metrics_band.genre_set WHERE "+col_val_conditional_str;
            print(sql)
            # execute the SELECT statement
            self.cursor.execute(sql)
            # get the generated id back
            genre_set_id = self.cursor.fetchone()[0]
            print("SET ID: "+str(genre_set_id))

            # if there isnt a genre_set that already exists, create a new entry for that genre set
            if(genre_set_id == -1):
                sql = "INSERT INTO metrics_band.genre_set ("+columns_str+") VALUES ("+values_str+") RETURNING genre_set_id";
                # execute the INSERT statement
                self.cursor.execute(sql, genre_id_list)
                # get the generated id back
                genre_set_id = self.cursor.fetchone()[0]
                print(genre_set_id)

            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
        return genre_set_id

    # TODO PICK UP FROM HERE
    # def insert_artist(self, artists):
    #     # inserts a record into the artist table for each artist in artists
    #     # artists = artists portion of main json object

    #     artist_id_list = []
    #     for genre_name in artists['names']:
    #         try:
    #             sql = "INSERT INTO metrics_band.artist (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=%s RETURNING genre_id";
    #             # execute the INSERT statement
    #             self.cursor.execute(sql, (genre_name,genre_name))
    #             # get the generated id back
    #             genre_id = self.cursor.fetchone()[0]
    #             print(genre_id)
    #             genre_id_list.append(genre_id)
    #         except (Exception, psycopg2.DatabaseError) as error:
    #             print(error)

    #     try:
    #         # commit the changes to the database
    #         self.connection.commit()
    #     except (Exception, psycopg2.DatabaseError) as error:
    #         print(error)
    
    #     return genre_id_list


    def insert_listen_history(self, user_id, song_id):
        # inserts a record into the listen_history table

        listen_id = 5
        try:
            sql = "INSERT INTO metrics_band.listen_history (enduser_id, song_id) VALUES (%s, %s) RETURNING listen_id";
            # execute the INSERT statement
            self.cursor.execute(sql, (user_id, song_id))
            # get the generated id back
            listen_id = self.cursor.fetchone()[0]
            print(listen_id)
            # commit the changes to the database
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            self.close_connection()
    
        return listen_id
