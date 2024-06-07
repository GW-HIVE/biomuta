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
        parser.add_option("-a","--accession",action="store",dest="accession",help="UniProtKB accession")
	parser.add_option("-g","--genename",action="store",dest="genename",help="Gene name")
	parser.add_option("-p","--pubmed",action="store",dest="pubmed",help="PUBMED ID")





	global PHASH
	global AUTH
	PHASH = {}

	outJson = '{}'

	(options,args) = parser.parse_args()
                
	for file in ([options.accession, options.genename, options.pubmed]):
		if not (file):
			parser.print_help()
			sys.exit(0)
	
	condList = []
	if options.accession != "N/A":
		condList.append("uniprot_ac LIKE '%s'" % ('%'+options.accession+'%'))
	if options.genename != "N/A":
                condList.append("gene_name LIKE '%s'" % ('%'+options.genename+'%')) 
	if options.pubmed != "N/A":
                condList.append("pmid LIKE '%s'" % ('%'+options.pubmed+'%')) 
 
	if len(condList) == 0:
		print {"errorMessage":"no query submitted!"}
		sys.exit()


	errorMsg = ''
		
	util.LoadParams("./conf/database.txt", PHASH)
        DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
			passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
	
	cur = DBH.cursor()	
	sql = "SELECT %s FROM biomuta3 WHERE " % (PHASH["SEARCH_FLIST"])
	sql += " AND ".join(condList)
	sql += " AND Cancer_Type != '-' AND accession != '-' "
	sql += "GROUP BY Cancer_Type,uniprot_ac,accession,gene_name "
	sql += "ORDER BY uniprot_ac, accession, gene_name, variation_count DESC"
	#print sql
               

	cur.execute(sql)
	fieldlist = PHASH["SEARCH_FLBLS"].split(",")
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



