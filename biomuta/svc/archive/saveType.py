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
		jsonObj11 = jsonObj["typedata"]["fields"]

		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
		
		cur = DBH.cursor()

		sql = ("SELECT createdBy FROM UPType WHERE type_id = %s" % (jsonObj1["typeId"])) 
		cur.execute(sql)
		row = cur.fetchone()
		createdBy = row[0]
	
		if createdBy != userName:
			errorMsg = 'You do not have permission to perform this task for this type.'
			jsonTextOut = '{"taskStatus" : "0", "errorMsg":"'+errorMsg+'"}'
		else:
			fieldlist = ["title", "description"]
			entrylist = []
			for field in fieldlist:
				entrylist.append(("%s = '%s'" % (field, jsonObj1[field].strip())))
			sql = "UPDATE UPType SET " + ", ".join(entrylist)
			sql += (" WHERE type_id = %s" % (jsonObj1["typeId"])) 
                	errorMsg +=  sql + ' | '
			cur.execute(sql)

			numericfieldlist = PHASH['UPTYPEFIELD_NUMERIC'].split(",")
			isNumeric = {}
			for field in numericfieldlist:
				isNumeric[field] = 1
			for i in range(0,len(jsonObj11)):	
				entrylist = []
				for field in jsonObj11[i]:
					if field != 'name':
						pair = ("`%s` = '%s'" % (field, jsonObj11[i][field].strip()))
						if field in isNumeric:
							pair = ("`%s` = %s" % (field, 
							jsonObj11[i][field].strip()))
						entrylist.append(pair)
				sql = "UPDATE UPTypeField SET " + ", ".join(entrylist)
				sql += (" WHERE type_id = %s AND name = '%s'" % (jsonObj1["typeId"], 
				jsonObj11[i]["name"]))
				errorMsg += sql + '|'
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



