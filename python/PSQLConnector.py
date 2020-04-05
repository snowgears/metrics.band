import psycopg2


class PSQLConnector(object):
    def __init__(self, host, dbname, dbuser, dbpassword):
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.host = host

        self.connection = None

    def connect(self):
        connection = psycopg2.connect(host=self.host, database=self.dbname, user=self.dbuser, password=self.dbpassword)
        self.connection = connection

    def insert_listen_history(self, song):
        sql = """INSERT INTO vendors(vendor_name)
             VALUES(%s) RETURNING vendor_id;"""
