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
        parser.add_option("-f","--fieldname",action="store",dest="fieldname",help="Field name")
	parser.add_option("-v","--fieldvalue",action="store",dest="fieldvalue",help="Field name")


        global PHASH
        global AUTH
        PHASH = {}

        outJson = '{}'

        (options,args) = parser.parse_args()

        for file in ([options.fieldname, options.fieldvalue]):
                if not (file):
                        parser.print_help()
                        sys.exit(0)
	fieldName = options.fieldname
	fieldValue = options.fieldvalue


		
	util.LoadParams("./conf/database.txt", PHASH)
	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
		passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
	
	cur = DBH.cursor()
	string = "SELECT %s FROM biomuta3 WHERE lower(%s) = '%s' AND Cancer_Type != '-' "
	sql = (string % (PHASH["PROTEINVIEW_FLIST"], fieldName, fieldValue)) 

	cur.execute(sql)
	fieldlist = PHASH["PROTEINVIEW_FLIST"].split(",")
	csvBuffer = PHASH["PROTEINVIEW_FLIST"] + '\n'
                
	objList = []
	for row in cur.fetchall():
		csvCollection = []
		obj = {}
		for j in range(0,len(fieldlist)):
			val = str(row[j])
			obj[fieldlist[j]] = val
			val = val.replace(',', '')
			csvCollection.append(val);
		objList.append(obj)
	outJson = objList	
	DBH.close()

	print json.dumps(outJson, separators=(',',':'), indent=4)

	

if __name__ == '__main__':
        main()



