from flask import *
from PSQLConnector import *
from SpotifyConnector import *

with open('config.json') as f:
    config = json.load(f)
psql = PSQLConnector(host=config['psql_host'], port=config['psql_port'], dbname=config['psql_dbname'],
                     dbuser=config['psql_dbuser'],
                     dbpassword=config['psql_dbpassword'])
app = Flask(__name__)


@app.route('/test', methods=['GET'])
def test():
    return "hello!"


@app.route('/view-all', methods=['GET'])
def view_all():
    records = psql.select_all_view()
    return jsonify(records.to_dict('records'))


if __name__ == '__main__':
    app.run(debug=True)
