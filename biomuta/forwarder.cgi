#!/usr/bin/python
import os,sys
import string
import cgi
import commands
from optparse import OptionParser
import json
import cgitb
cgitb.enable()

libpath = '/hive/net3/software/MySQL-python-1.2.5/build/lib.linux-x86_64-2.7/';
sys.path.append(libpath)
import MySQLdb


__version__="1.0"
__status__ = "Dev"



#~~~~~~~~~~~~~~~~~~~~~
def main():
	   	

	configJson = json.loads(open("conf/config.json", "r").read())
	serverJson  =  configJson[configJson["server"]]

	form = cgi.FieldStorage()
	gene_name = form["gene"].value if "gene" in form else ""
        #sanitizize input using cgi.escape function, then remove ' and " from the search
        #Dacian Reece-Stremtan 8/10/2019
        gene_name = cgi.escape(gene_name) 
        gene_name = gene_name.replace("'","").replace('"',"")
            
        print "Content-Type: text/html"
        print
        if len(gene_name.strip()) > 15 or gene_name.find("'") != -1:
            print "bad value for gene name!"
            sys.exit()
       
        out_json = {}
        DBH = MySQLdb.connect(
                host = serverJson["dbinfo"]["dbhost"],
                user = serverJson["dbinfo"]["dbuserid"],
                passwd = serverJson["dbinfo"]["dbpassword"],
                db = serverJson["dbinfo"]["dbname"]
        )
        cur = DBH.cursor()

        sql = "SELECT canonicalAc FROM biomuta_protein WHERE lower(geneName) = '%s' " % (gene_name.lower())
	cur.execute(sql)
	row = cur.fetchone()
	url = "/biomuta/norecord"
	if row != None:
		ac = row[0][0:-2]
		url = "/biomuta/branchview/" + ac
	DBH.close()


	print "<meta HTTP-EQUIV=\"REFRESH\" content=\"0; url=%s\">" % (url)



if __name__ == '__main__':
        main()



