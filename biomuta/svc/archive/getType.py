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
        msg = "Type ID"
        parser.add_option("-t","--typeId",action="store",dest="typeId",help=msg)
	msg = "userName"
        parser.add_option("-u","--userName",action="store",dest="userName",help=msg)
        

	global PHASH
	global AUTH
	PHASH = {}

        
	(options,args) = parser.parse_args()
	for file in ([options.typeId]):
		if not (file):
			print '{"errorMsg":"Bad command line input "}'
			sys.exit(0)
                
	typeId = options.typeId
	userName = options.userName

	sqllist = ''
	try:
		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])

		typeData = '{'
		cur = DBH.cursor()
		
		sql = ("SELECT createdBy FROM UPType WHERE type_id = %s" % (typeId))
                cur.execute(sql)
                row = cur.fetchone()
                createdBy = row[0]
		readOnly = 0 if createdBy == userName else 1


		
		fieldlist = PHASH['UPTYPE_FLIST'].split(",")
		sql = ("SELECT %s FROM UPType WHERE type_id = %s" % (PHASH['UPTYPE_FLIST'],typeId)) 
		cur.execute(sql)
		row = cur.fetchone()
		entrylist = []
		for j in range(0,len(fieldlist)):
			val = str(row[j])
			val = val.replace('\"', '\\\"')
			string = '"'+fieldlist[j]+'":"' + val + '"'
			entrylist.append(string)
		typeData += ', '.join(entrylist)	
		
		
		fieldlist = PHASH['UPTYPEFIELD_FLIST'].split(",")
		sql = ("SELECT %s FROM UPTypeField WHERE type_id = %s" % (PHASH['UPTYPEFIELD_FLIST'],typeId))
		cur.execute(sql)
		entrylist1 = []
		for row in  cur.fetchall():
			entrylist2 = []
			for j in range(0,len(fieldlist)):
				val = str(row[j])
                        	val = val.replace('\"', '\\\"')
				fieldlist[j] = fieldlist[j].strip("`")
				entrylist2.append('"'+fieldlist[j]+'":"'+val+'"')
				#entrylist2.append('"emType":"text"')
			string = '{' + ', '.join(entrylist2) + '}'
			entrylist1.append(string)
		typeData +=  ', "fields":[' + ', '.join(entrylist1) + ']'	
		typeData +=  '}'

		jsonTextOut = '{ '
                jsonTextOut += '"typedata" : '+typeData 
		jsonTextOut += ','
		jsonTextOut += '"readOnly":"'+str(readOnly)+'", '
		jsonTextOut += '"sqllist" : "'+sqllist+'"'
		jsonTextOut += '}'
		DBH.close()
	except:
		jsonTextOut = '{"errorMsg":"Flag-II no json text input "}'


	#print "Content-Type: text/plain"
        #print
        #print """"""
	print jsonTextOut


if __name__ == '__main__':
        main()



