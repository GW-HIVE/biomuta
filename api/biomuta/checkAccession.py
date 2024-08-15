#!/usr/bin/python
'''import os,sys
import string
import cgi
import commands
from optparse import OptionParser
import json
import util

libpath = '/hive/net3/software/MySQL-python-1.2.5/build/lib.linux-x86_64-2.7/';
sys.path.append(libpath)
import MySQLdb


__version__="1.0"
__status__ = "Dev"



#~~~~~~~~~~~~~~~~~~~~~
def main():
	   	
	usage = "\n%prog  [options]"
        parser = OptionParser(usage,version="%prog " + __version__)
        msg = "Input JSON text"
        parser.add_option("-j","--inJson",action="store",dest="inJson",help=msg)

	global PHASH
	global AUTH
	PHASH = {}

	(options,args) = parser.parse_args()
	for file in ([options.inJson]):
		if not (file):
			parser.print_help()
			sys.exit(0)

	configJson = json.loads(open("conf/config.json", "r").read())
	serverJson  =  configJson[configJson["server"]]
 
	inJson  = json.loads(options.inJson)
	outJson = {"isvalid":False, "taskstatus":1}
        
	errorMsg = ''
	try:
        	DBH = MySQLdb.connect(
			host = serverJson["dbinfo"]["dbhost"], 
			user = serverJson["dbinfo"]["dbuserid"], 
			passwd = serverJson["dbinfo"]["dbpassword"], 
			db = serverJson["dbinfo"]["dbname"]
		)
		cur = DBH.cursor()
                ac = inJson["ac"].lower()	
                aclist = "'%s','%s-1','%s-2','%s-3'" % (ac, ac, ac, ac)
                sql = "SELECT count(*) n FROM biomuta_protein WHERE lower(canonicalAc) IN (%s) " % (aclist)
		cur.execute(sql)
		row = cur.fetchone()
		if row[0] > 0:
                    outJson["isvalid"] = True
                DBH.close()
	except IOError as e:
    		outJson["taskstatus"] = 0
		outJson["errormsg"] = "I/O error({0}): {1}".format(e.errno, e.strerror)
	except ValueError:
    		outJson["taskstatus"] = 0
		outJson["errormsg"] = "Could not convert data to an integer."
	except:
    		outJson["taskstatus"] = 0
		outJson["errormsg"] = "Unexpected error:", sys.exc_info()[0]
		raise


	print json.dumps(outJson, indent=4)


if __name__ == '__main__':
        main()



'''
'''
##################################################################

Functionality: This script is used to check if a specific accession number exists in the database. It verifies the presence of data based on the accession number provided by the user.

In the frontend, this endpoint is used to validate whether the input accession number is recognized in the database. If it is valid, the frontend may proceed to show detailed information or offer further options. If its invalid, the frontend likely displays a message to the user.
'''

from flask import request, jsonify
from pymongo import MongoClient, errors
def check_accession_route(app, db):
    collection = db['C_biomuta_protein']  # MongoDB collection name
    
    @app.route('/checkAccession', methods=['POST'])
    def check_accession():
        outJson = {"isvalid": False, "taskstatus": 1}
        
        try:
            inJson = request.json
            ac = inJson.get("ac")
            if not ac:
                raise ValueError("No accession number provided")

            aclist = [ac, f"{ac}-1", f"{ac}-2", f"{ac}-3"]
 # MongoDB query to check if the accession exists. The query looks for the canonicalAc field in MongoDB that matches any of the values in the aclist.
            query = {"canonicalAc": {"$in": aclist}}
            count = collection.count_documents(query)

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
