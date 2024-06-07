#!/usr/bin/python
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



