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
        msg = "Input JSON text"
        parser.add_option("-j","--jsonTextIn",action="store",dest="jsonTextIn",help=msg)

	global PHASH
	global AUTH
	PHASH = {}
	AUTH = {}

	form = cgi.FieldStorage()
	jsonTextIn = form["json"].value if "json" in form else ""
	jsonTextOut = '{}'

	(options,args) = parser.parse_args()
        if jsonTextIn == '':
                for file in ([options.jsonTextIn]):
                        if not (file):
				print "Content-Type: text/plain"
				print
				print """"""
				print '{"errorMsg":"Flag-I bad command line input "}'
				sys.exit(0)
                jsonTextIn  = options.jsonTextIn
	

	sqllist = ''
	try:
		jsonObj = json.loads(jsonTextIn)
		jsonObj1 = jsonObj["typedata"]
		jsonObj2 = jsonObj["sessioninfo"]
		userName = jsonObj2["userName"] if "userName" in jsonObj2 else ""
		userPass = util.EncryptString(jsonObj2["userPass"]) if "userPass" in jsonObj2 else ""
 		sessionId = jsonObj2["sessionId"] if "sessionId" in jsonObj2 else ""

		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
		util.Authenticate(DBH, userName, userPass, sessionId, PHASH['MAXSESSIONAGE'],  AUTH)
	

		if AUTH['status'] == 1:
			fieldlist = ["title", "description"]
			entrylist = []
			for field in fieldlist:
				entrylist.append(("%s = '%s'" % (field, jsonObj1[field].strip())))
			sql = "UPDATE UPType SET " + ", ".join(entrylist)
			sql += (" WHERE type_id = %s" % (jsonObj1["typeId"])) 
			sqllist += sql

		sessioninfo = '{ "fullname":"'+AUTH['fullname']+'" , "loginStatus":"'+ str(AUTH['status']) + '", '
                sessioninfo += '"userName":"'+userName+'",'     
		sessioninfo += '"sessionId":"'+AUTH['id']+'", "msg":"'+AUTH['msg']+'"}';
                
		jsonTextOut = '{ '
                jsonTextOut += '"sessioninfo" : '+sessioninfo
		jsonTextOut += ','
		jsonTextOut += '"sqllist" : "'+sqllist+'"'
		jsonTextOut += '}'
		DBH.close()
	except:
		jsonTextOut = '{"errorMsg":"Flag-II no json text input "}'

	print "Content-Type: text/plain"	
	print
	print """"""
	print jsonTextOut


if __name__ == '__main__':
        main()



