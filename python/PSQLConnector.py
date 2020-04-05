import psycopg2


class PSQLConnector(object):
    def __init__(self, host, port, dbname, dbuser, dbpassword):
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.host = host
        self.port = port

        self.connection = None

    def connect(self):
        # TODO try excepts my dude
        connection = psycopg2.connect(host=self.host, port=self.port, database=self.dbname, user=self.dbuser,
                                      password=self.dbpassword)
        return connection

    @staticmethod
    def close_connection(connection, cursor):
        if connection:
            cursor.close()
            connection.close()

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
