
'''
##################################################################

Functionality: This script is used to check if a specific accession number exists in the database. It verifies the presence of data based on the accession number provided by the user.

In the frontend, this endpoint is used to validate whether the input accession number is recognized in the database. If it is valid, the frontend may proceed to show detailed information or offer further options. If its invalid, the frontend likely displays a message to the user.
'''
from flask import request, jsonify
from flask_restx import Resource
from pymongo import errors

def check_accession_route(api, db):
    class CheckAccession(Resource):
        def post(self):
            outJson = {"isvalid": False, "taskstatus": 1}

            try:
                inJson = request.json
                ac = inJson.get("ac")
                if not ac:
                    raise ValueError("No accession number provided")

                aclist = [ac, f"{ac}-1", f"{ac}-2", f"{ac}-3"]
                
                # MongoDB query to check if the accession exists.
                query = {"canonicalAc": {"$in": aclist}}
                count = db['C_biomuta_protein'].count_documents(query)

                if count > 0:
                    outJson["isvalid"] = True

            except ValueError as ve:
                outJson["taskstatus"] = 0
                outJson["errormsg"] = str(ve)
            except IOError as e:
                outJson["taskstatus"] = 0
                outJson["errormsg"] = f"I/O error({e.errno}): {e.strerror}"
            except errors.PyMongoError as pe:
                outJson["taskstatus"] = 0
                outJson["errormsg"] = "Database error occurred."
            except Exception as e:
                outJson["taskstatus"] = 0
                outJson["errormsg"] = f"Unexpected error: {str(e)}"

            return jsonify(outJson)

    # Register the resource with the API and the route
    api.add_resource(CheckAccession, '/checkAccession')
