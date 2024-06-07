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
		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
		
		cur = DBH.cursor()
	
		sql = ("SELECT createdBy FROM UPType WHERE type_id = %s" % (jsonObj["typeId"]))
                cur.execute(sql)
                row = cur.fetchone()
                createdBy = row[0]

                if createdBy != userName:
                        errorMsg = 'You do not have permission to perform this task for this type.'
                        jsonTextOut = '{"taskStatus" : "0", "errorMsg":"'+errorMsg+'"}'
                else:
			string = "DELETE FROM UPTypeField WHERE name = '%s'  AND type_id = %s"
			sql = (string % (jsonObj["fieldName"], jsonObj["typeId"]))
                	errorMsg +=  sql + ' | '
			cur.execute(sql)

			jsonTextOut = '{ '
			jsonTextOut += '"taskStatus" : "1"'
			jsonTextOut += '}'
			DBH.commit()
	except:
		DBH.rollback()
		jsonTextOut = '{"taskStatus" : "0", "errorMsg":"'+errorMsg+'"}'
		
	
	DBH.close()
	print jsonTextOut


if __name__ == '__main__':
        main()



