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
		userName = jsonObj["userName"] if "userName" in jsonObj else ""
		userPass = util.EncryptString(jsonObj["userPass"]) if "userPass" in jsonObj else ""
 		sessionId = jsonObj["sessionId"] if "sessionId" in jsonObj else ""
		typeId = jsonObj["typeId"] if "typeId" in jsonObj else ""

		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
		util.Authenticate(DBH, userName, userPass, sessionId, PHASH['MAXSESSIONAGE'],  AUTH)
		

		typeData = '{'
		if AUTH['status'] == 1:
			cur = DBH.cursor()
			fieldlist = PHASH['UPTYPE_FLIST'].split(",")
			sql = ("SELECT %s FROM UPType WHERE type_id = %s" % (PHASH['UPTYPE_FLIST'],typeId)) 
			cur.execute(sql)
			row = cur.fetchone()
			entrylist = []
			for j in range(0,len(fieldlist)):
				string = '"'+fieldlist[j]+'":"'+str(row[j])+'"'
				entrylist.append(string)
			typeData += ', '.join(entrylist)	
			
			
			fieldlist = PHASH['UPTYPEFIELD_FLIST'].split(",")
                        sql = ("SELECT %s FROM UPTypeField WHERE type_id = %s" % (PHASH['UPTYPEFIELD_FLIST'],typeId))
			cur.execute(sql)
			entrylist1 = []
			for row in  cur.fetchall():
				entrylist2 = []
				for j in range(0,len(fieldlist)):
					fieldlist[j] = fieldlist[j].strip("`")
					entrylist2.append('"'+fieldlist[j]+'":"'+str(row[j])+'"')
					#entrylist2.append('"emType":"text"')
					
				string = '{' + ', '.join(entrylist2) + '}'
				entrylist1.append(string)
			typeData +=  ', "fields":[' + ', '.join(entrylist1) + ']'	
			typeData +=  '}'


		sessionInfo = '{ "fullname":"'+AUTH['fullname']+'" , "loginStatus":"'+ str(AUTH['status']) + '", '
                sessionInfo += '"userName":"'+userName+'",'     
		sessionInfo += '"sessionId":"'+AUTH['id']+'", "msg":"'+AUTH['msg']+'"}';
                
		jsonTextOut = '{ '
                jsonTextOut += '"typedata" : '+typeData 
                jsonTextOut += ','
		jsonTextOut += '"sessioninfo" : '+sessionInfo
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



