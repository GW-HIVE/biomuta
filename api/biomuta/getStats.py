#!/usr/bin/python
'''
import os,sys
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
	outJson = {"titles":{}, "taskstatus":1}
        
	errorMsg = ''
	try:
        	DBH = MySQLdb.connect(
			host = serverJson["dbinfo"]["dbhost"], 
			user = serverJson["dbinfo"]["dbuserid"], 
			passwd = serverJson["dbinfo"]["dbpassword"], 
			db = serverJson["dbinfo"]["dbname"]
		)
		cur = DBH.cursor()
		sql = "SELECT id, title FROM biomuta_stat "
		cur.execute(sql)
		for row in cur.fetchall():
			outJson["titles"][row[0]] = row[1]
		
		sql = "SELECT jsonstring FROM biomuta_stat WHERE id = %s " % (inJson["statid"])
                cur.execute(sql)
               	row = cur.fetchone() 
		obj = json.loads(row[0])
		outJson["dataframe"] = [obj["fieldnames"], obj["fieldtypes"]]
		outJson["pageconf"]  = configJson["pageconf"]["about"]
		for row in obj["dataframe"]:
			outJson["dataframe"].append(row)
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
##############################################################
Interact with a MongoDB collection to retrieve statistical data based on a given statid
curl -X POST http://127.0.0.1:5000/getStats -H "Content-Type: application/json" -d "{\"statid\": \"66b606e202dafde1d7c99874\"}"
'''
from flask import request, jsonify
from pymongo import MongoClient, errors
from bson import ObjectId

def get_stats_route(app, db):
    collection = db['C_biomuta.stats']  # MongoDB collection name
    
    @app.route('/getStats', methods=['POST'])
    def get_stats():
        inJson = request.json
        outJson = {"titles": {}, "taskstatus": 1}

        try:
            # Fetch titles from MongoDB
            titles = collection.find({}, {"_id": 1, "countName": 1})
            for title in titles:
                outJson["titles"][str(title["_id"])] = title["countName"]

            # Fetch the specific document based on the ObjectId
            stat_id = inJson.get("statid")
            try:
                object_id = ObjectId(stat_id)
                stat_record = collection.find_one({"_id": object_id})
                #print("Fetched stat_record:", stat_record)  # Debugging print
            except Exception as e:
                outJson["taskstatus"] = 0
                outJson["errormsg"] = "Invalid ObjectId format: " + str(e)
                return jsonify(outJson)

            if stat_record:
                # Check if all necessary fields exist
                if "countName" in stat_record and "versionName" in stat_record and "countValue" in stat_record:
                    outJson["dataframe"] = [
                        ["countName", "versionName", "countValue"],
                        [stat_record["countName"], stat_record["versionName"], stat_record["countValue"]]
                    ]
                else:
                    outJson["taskstatus"] = 0
                    outJson["errormsg"] = "Fields missing in stat_record: " + str(stat_record)
            else:
                outJson["taskstatus"] = 0
                outJson["errormsg"] = "Record not found."

        except Exception as e:
            outJson["taskstatus"] = 0
            outJson["errormsg"] = "Unexpected error: " + str(e)

        return jsonify(outJson)
