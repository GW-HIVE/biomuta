#!/usr/bin/python
import os,sys
import string
import cgi
import commands
from optparse import OptionParser
import json
import util

#To get around Mac's MySQLdb problem
#libpath = '/Library/Python/2.7/site-packages/MySQL_python-1.2.5-py2.7-macosx-10.11-intel.egg'
#os.environ['PYTHON_EGG_CACHE'] = '/tmp'
#sys.path.append(libpath)

import MySQLdb


__version__="1.0"
__status__ = "Dev"



#~~~~~~~~~~~~~~~~~~~~~
def main():

   	usage = "\n%prog  [options]"
        parser = OptionParser(usage,version="%prog " + __version__)
        msg = "userName"
        parser.add_option("-u","--userName",action="store",dest="userName",help=msg)
	msg = "Input JSON text"
	parser.add_option("-j","--jsonTextIn",action="store",dest="jsonTextIn",help=msg)

	global PHASH
	global AUTH
	PHASH = {}

	jsonTextOut = '{}'

	(options,args) = parser.parse_args()
                
	for file in ([options.jsonTextIn, options.userName]):
		if not (file):
			print "Content-Type: text/plain"
			print
			print """"""
			print '{"errorMsg":"Flag-I bad command line input "}'
			sys.exit(0)
	jsonTextIn  = options.jsonTextIn
	userName =  options.userName
	

	errorMsg = ''
	try:
		jsonObj = json.loads(jsonTextIn)
		jsonObj1 = jsonObj["typedata"]
		jsonObj1["name"] = jsonObj1["name"].lower()

		

		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
		
		cur1 = DBH.cursor()
	
		sql = ("SELECT type_id FROM  UPType WHERE lower(name) = '%s' " % (jsonObj1["name"]))
		cur1.execute(sql)
                row = cur1.fetchone()
		if row == None:
			cur2 = DBH.cursor()
			sql = "INSERT INTO UPType (name, title, description, is_virtual_fg, prefetch_fg, createdBy) "
			sql += ("VALUES ('%s', '%s', '%s', %s, %s, '%s') " % (jsonObj1["name"], jsonObj1["title"], 
							jsonObj1["description"], 
							jsonObj1["is_virtual_fg"],jsonObj1["prefetch_fg"], userName)) 
			errorMsg +=  sql
			cur2.execute(sql)
			sql = ("SELECT type_id FROM  UPType WHERE lower(name) = '%s' " % (jsonObj1["name"]))
			cur2.execute(sql)
			row = cur2.fetchone()
			newTypeId = row[0]
			jsonTextOut = '{ '
			jsonTextOut += '"taskStatus" : "1"'
			jsonTextOut += ', "newTypeId" : "'+str(newTypeId)+'"'
			jsonTextOut += '}'
			DBH.commit()
		else:
			errorMsg = 'Type already exists with name=' + jsonObj1["name"]
			jsonTextOut = '{"taskStatus" : "0", "errorMsg":"'+errorMsg+'"}'	
	except:
		DBH.rollback()
		jsonTextOut = '{"taskStatus" : "0", "errorMsg":"'+errorMsg+'"}'
		
	
	DBH.close()
	print jsonTextOut


if __name__ == '__main__':
        main()



