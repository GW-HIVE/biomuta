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

	outJson = '{}'

	(options,args) = parser.parse_args()
                
	for file in ([options.inJson]):
		if not (file):
			parser.print_help()
			sys.exit(0)
	inJson  = options.inJson


	errorMsg = ''
	try:

		util.LoadParams("./conf/database.txt", PHASH)
        	DBH = MySQLdb.connect(host = PHASH['DBHOST'], user = PHASH['DBUSERID'], 
				passwd = PHASH['DBPASSWORD'], db = PHASH['DBNAME'])
	
		cur = DBH.cursor()	
		inJson = json.loads(inJson)
		sql = ""
		fieldValue = "placeholder"
		if inJson["qryList"][0]["fieldname"] == "genericfield":
                	fieldValue = "%"+inJson["qryList"][0]["fieldvalue"].lower().strip().split('.')[0]+"%"
			string = "SELECT %s FROM biomuta3 "
			string += "WHERE (lower(gene_name) LIKE '%s' OR "
			string += "lower(uniprot_ac) LIKE '%s' OR  lower(accession) LIKE '%s' ) "
			string += " AND Cancer_Type != '-' AND accession != '-' "
                	string += "GROUP BY Cancer_Type,uniprot_ac,accession,gene_name "
			string += "ORDER BY uniprot_ac, accession, gene_name, variation_count DESC"
			sql = string % (PHASH["SEARCH_FLIST"], fieldValue, fieldValue, fieldValue)
		else:
			obj = inJson["qryList"][0]
			sql = "SELECT %s FROM biomuta3 " % (PHASH["SEARCH_FLIST"])
			sql += "WHERE Cancer_Type != '-' AND "
			sql += " lower(%s) LIKE '%s' " % (obj["fieldname"], "%"+obj["fieldvalue"].lower().strip().split('.')[0]+"%")
			for i in xrange(1, len(inJson["qryList"])):
				obj = inJson["qryList"][i]
				sql += " %s " % (inJson["junList"][i-1])
				sql += " lower(%s) LIKE '%s' " % (obj["fieldname"], "%"+obj["fieldvalue"].lower().strip().split('.')[0]+"%")
			sql += " GROUP BY Cancer_Type,uniprot_ac,accession,gene_name "
			sql += " ORDER BY UniProt_AC, variation_count DESC"

		#print "Robel", sql               
		cur.execute(sql)
		fieldlist = PHASH["SEARCH_FLBLS"].split(",")
		csvBuffer = PHASH["SEARCH_FLBLS"] + '\n'
		objList = []
		for row in cur.fetchall():
			csvCollection = []
			obj = {}
			for j in range(0,len(fieldlist)):
				val = str(row[j])
                                #val = val.replace(':', '|')
                                #val = val.replace('\"', '\\\"')
				obj[fieldlist[j]] = val
				val = val.replace(',', '')
				csvCollection.append(val);
			csvBuffer += ', '.join(csvCollection) + '\n'
			objList.append(obj)

		outJson = {"taskStatus":1, "inJson":inJson, "searchResults":objList}	

		outputFile =  "/hive/net3/apache_temp/" + fieldValue + ".csv" 
		errorMsg = 'Could not write out CSV file ' + outputFile
               
		FW = open(outputFile, "w")
		FW.write("%s" % (csvBuffer))
        	FW.close()
		cmd = "chmod 777 " + outputFile
       		x = commands.getoutput(cmd)
		DBH.close()
	except Exception, e:
                outJson["taskStatus"] = 0
                outJson["errorMsg"] = errorMsg if errorMsg != "" else str(e)
	

	print json.dumps(outJson, separators=(',',':'))


if __name__ == '__main__':
        main()



