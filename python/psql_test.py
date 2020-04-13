from PSQLConnector import *
import json

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)
    psql = PSQLConnector(host=config['psql_host'], port=config['psql_port'], dbname=config['psql_dbname'],
                         dbuser=config['psql_dbuser'],
                         dbpassword=config['psql_dbpassword'])

    records = psql.select_all_view()

    print(records)
