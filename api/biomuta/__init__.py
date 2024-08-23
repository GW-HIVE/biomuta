from flask import Flask, request, g, send_from_directory, make_response , jsonify
from flask_cors import CORS
from flask_restx import Api
from pymongo import MongoClient
import os
import json
import time

from .checkAccession import check_accession_route
from .getStats import get_stats_route
from .searchBioMuta import searchBioMuta_route
from .getProteinData import getProteinData_route
from .forwarder import forward_genename_route

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "biomuta_db"


def create_app():
    # Create Flask instance
    app = Flask(__name__)
    
    CORS(app, resources={r"/*": {"origins": "*"}})


    # Initialize MongoDB client
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[DB_NAME]
    app.mongo_db = mongo_db

    # Setup the API using the Flask-RESTX library
    api = Api(
        app,
        version="1.0",
        title="BioMuta APIs",
        description="BioMuta Cancer Mutation Database API",
    )

    # Register routes (namespaces)
    check_accession_route(api, app.mongo_db)
    get_stats_route(api, app.mongo_db)
    searchBioMuta_route(api, app.mongo_db)
    getProteinData_route(api, app.mongo_db)
    forward_genename_route(api, app.mongo_db)

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        duration = time.time() - g.start_time
        print(f"Request to {request.path} took {duration} seconds")
        return response
    
    @app.route('/download/<filename>', methods=['GET'])
    def download_file(filename):
        try:
            # Serve the file from the /tmp directory
            return send_from_directory(directory="/tmp", path=filename, as_attachment=True)
        except Exception as e:
            return make_response(jsonify({"taskStatus": 0, "errorMsg": str(e)}), 500)

    return app
