from flask import Flask
from pymongo import MongoClient
from checkAccession import check_accession_route
from getStats import get_stats_route
from searchBioMuta import searchBioMuta_route
from getProteinData import getProteinData_route
from forwarder import forward_genename_route
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['biomuta_db']  # MongoDB database name

# Register routes with the app
check_accession_route(app, db)
get_stats_route(app, db)
searchBioMuta_route(app, db)
getProteinData_route(app, db)
forward_genename_route(app, db)

if __name__ == '__main__':
    app.run(debug=True)
