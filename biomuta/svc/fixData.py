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


	global PHASH
	global AUTH
	PHASH = {}



	try:

		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
	
		cur = DBH.cursor()	
		sql = "SELECT id, gene_name FROM biomuta3 WHERE gene_name like '%;%'"
		cur.execute(sql)
		for row in cur.fetchall():
			nameList = row[1].split(";")
			if nameList[0] == nameList[1]:
				sql = "UPDATE biomuta3 SET gene_name = '%s' WHERE id = %s" % (nameList[0], row[0])
				print sql
				cur.execute(sql)
		DBH.commit()		
		DBH.close()
	except Exception, e:
                print str(e)
	


if __name__ == '__main__':
        main()



