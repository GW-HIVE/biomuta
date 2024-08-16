#!/usr/bin/python
'''
import os,sys
import string
import cgi
import commands
from optparse import OptionParser
import json
import util
import datetime
import time


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


	(options,args) = parser.parse_args()
                
	for file in ([options.inJson]):
		if not (file):
			parser.print_help()
			sys.exit(0)
	

	configJson = json.loads(open("conf/config.json", "r").read())
	serverJson  =  configJson[configJson["server"]]
 

	
	inJson  = json.loads(options.inJson)
	outJson = {}

	errorMsg = ''
	try:
        	DBH = MySQLdb.connect(
			host = serverJson["dbinfo"]["dbhost"], 
			user = serverJson["dbinfo"]["dbuserid"], 
			passwd = serverJson["dbinfo"]["dbpassword"], 
			db = serverJson["dbinfo"]["dbname"]
		)
		cur = DBH.cursor()	
		seen = {"canon":{}} 
		
                fieldValue = "%"+inJson["qryList"][0]["fieldvalue"].lower().strip().split('.')[0]+"%"
		sql = configJson["queries"]["generic"]
		sql = sql.replace("QVALUE", fieldValue)

		cur.execute(sql)

		labelList = configJson["tableheaders"]["searchresults"]["labellist"]
		typeList = configJson["tableheaders"]["searchresults"]["typelist"]
		objList1 = [labelList, typeList]
		objList2 = [labelList]
		canonList = []
		for row in cur.fetchall():
			obj1, obj2 = [], []
			seen["canon"][row[0]] = True
			for j in range(0,len(labelList)-4): 
				obj1.append(row[j])
				obj2.append(str(row[j]))
			objList1.append(obj1)
			objList2.append(obj2)
		canonList = seen["canon"].keys()	
		
		if len(canonList) > 0:
			canons = json.dumps(canonList)[1:-1]
			sql = configJson["queries"]["query_1"]
			sql = sql.replace("CANONS", canons)
			cur.execute(sql)
			countHash = {"n1":{}, "n2":{}}
			for row in cur.fetchall():
				countHash["n1"][row[0]] = row[1]
	
			sql = configJson["queries"]["query_2"]
                	sql = sql.replace("CANONS", canons)
			cur.execute(sql)
                	for row in cur.fetchall():
                        	countHash["n2"][row[0]] = row[1]
			

			pmid_count = {}
			doid_count = {}
			for canon in canonList:
				sql = configJson["queries"]["query_8"]
                        	sql = sql.replace("CANON", canon)
                        	cur.execute(sql)
                        	row = cur.fetchone()
				pmid_count[canon] = int(row[0])

				sql = configJson["queries"]["query_9"]
                        	sql = sql.replace("CANON", canon)
                        	cur.execute(sql)
                        	row = cur.fetchone()
                        	doid_count[canon] = int(row[0])

			for i in xrange(2,len(objList1)):
				obj1 = objList1[i]	
				obj2 = objList2[i-1]
				canon = obj2[0]
				n1 = countHash["n1"][obj1[0]] if obj1[0] in countHash["n1"] else 0
				n2 = countHash["n2"][obj1[0]] if obj1[0] in countHash["n2"] else 0
				obj1 += [n1,n2,doid_count[canon], pmid_count[canon]]
				obj2 += [str(n1),str(n2), str(doid_count[canon]), str(pmid_count[canon])]
				ac = obj1[0].split("-")[0]
				obj1[0] = '<a href="' + serverJson["rootinfo"]["proteinviewurl"] + ac + '">'+obj1[0] + '</a>'


		outJson = {"taskStatus":1, "inJson":inJson, "searchresults":objList1}
		if len(objList1) == 2:
			outJson = {"taskStatus":0, "inJson":inJson, "errorMsg":"No results were found!"}


		outJson["pageconf"] = configJson["pageconf"]["searchresults"]
                
		timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
		outputFile =  serverJson["pathinfo"]["tmppath"] + "/biomuta-searchresults-" + timeStamp + ".csv" 
		outJson["downloadfilename"] = "biomuta-searchresults-" + timeStamp + ".csv"
		FW = open(outputFile, "w")
		for i in xrange(0,len(objList2)):
			FW.write("%s\n" % (",".join(objList2[i])))
        	FW.close()
		cmd = "chmod 777 " + outputFile
       		x = commands.getoutput(cmd)
		DBH.close()
	except Exception, e:
                outJson["taskStatus"] = 0
                outJson["errorMsg"] = errorMsg if errorMsg != "" else str(e)
	
	print json.dumps(outJson, indent=4, separators=(',',':'))


if __name__ == '__main__':
        main()



'''

'''
###############################################################
handles complex searches within the BioMuta database and return relevant data related to single-nucleotide variations (SNVs) in cancer.

curl -X POST http://127.0.0.1:5000/searchBioMuta -H "Content-Type: application/json" -d "{\"qryList\":[{\"fieldname\":\"geneName\",\"fieldvalue\":\"KRAS\"}]}"

'''
from flask import request, jsonify
from flask_restx import Resource
from pymongo import MongoClient
import json
import datetime
import time

def searchBioMuta_route(api, db):
    
    class SearchBioMuta(Resource):
        def post(self):
            outJson = {}

            try:
                inJson = request.json
                fieldValue = inJson["qryList"][0]["fieldvalue"].lower().strip().split('.')[0]

                # MongoDB query for the generic search
                query = {
                    "$or": [
                        {"geneName": {"$regex": fieldValue, "$options": "i"}},
                        {"canonicalAc": {"$regex": fieldValue, "$options": "i"}},
                        {"refseqAc": {"$regex": fieldValue, "$options": "i"}},
                        {"peptideId": {"$regex": fieldValue, "$options": "i"}}
                    ]
                }

                protein_collection = db['C_biomuta_protein']
                protein_results = protein_collection.find(query)

                labelList = ["UniProtKB AC", "Gene Symbol", "RefSeq AC", "Ensembl Peptide",
                            "Modified Residues", "Modified Functional Residues", "DOID Count", "PMID Count"]
                typeList = ["string", "string", "string", "string", "number", "number", "number", "number"]
                
                objList1 = [labelList, typeList]
                canonList = []

                for result in protein_results:
                    obj1 = [result.get("canonicalAc"), result.get("geneName"),
                            result.get("refseqAc"), result.get("peptideId")]
                    objList1.append(obj1)
                    canonList.append(result.get("canonicalAc"))

                if canonList:
                    countHash = {"n1": {}, "n2": {}}

                    # MongoDB query for query_1 and query_2 equivalents
                    mutation_eff_collection = db['C_biomuta_mutation_eff']
                    mutation_eff_query = {
                        "canonicalAc": {"$in": canonList},
                        "refResidue": {"$ne": "altResidue"},
                        "altResidue": {"$ne": "*"}
                    }

                    # query_1
                    pipeline1 = [
                        {"$match": mutation_eff_query},
                        {"$group": {"_id": "$canonicalAc", "count": {"$sum": 1}}}
                    ]
                    results1 = mutation_eff_collection.aggregate(pipeline1)
                    for res in results1:
                        countHash["n1"][res["_id"]] = res["count"]

                    # query_2
                    pipeline2 = [
                        {"$match": mutation_eff_query},
                        {"$group": {"_id": "$canonicalAc", "count": {"$sum": 1}}}
                    ]
                    results2 = mutation_eff_collection.aggregate(pipeline2)
                    for res in results2:
                        countHash["n2"][res["_id"]] = res["count"]

                    # MongoDB query for query_8 and query_9 equivalents
                    mutation_pmid_collection = db['C_biomuta_mutation_pmid']
                    mutation_freq_collection = db['C_biomuta_mutation_freq']
                    
                    pmid_count = {}
                    doid_count = {}

                    for canon in canonList:
                        # query_8 equivalent
                        pmid_query = {"canonicalAc": canon}
                        pmid_count[canon] = mutation_pmid_collection.count_documents(pmid_query)

                        # query_9 equivalent
                        doid_query = {"canonicalAc": canon}
                        doid_count[canon] = mutation_freq_collection.count_documents(doid_query)

                    for i in range(2, len(objList1)):
                        obj1 = objList1[i]
                        canon = obj1[0]
                        n1 = countHash["n1"].get(canon, 0)
                        n2 = countHash["n2"].get(canon, 0)
                        obj1 += [n1, n2, doid_count[canon], pmid_count[canon]]

                        ac = obj1[0].split("-")[0]
                        obj1[0] = f'<a href="/biomuta/proteinview/{ac}">{obj1[0]}</a>'

                outJson = {"taskStatus": 1, "inJson": inJson, "searchresults": objList1}
                if len(objList1) == 2:
                    outJson = {"taskStatus": 0, "inJson": inJson, "errorMsg": "No results were found!"}

                timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
                outputFile = f'/tmp/biomuta-searchresults-{timeStamp}.csv'
                outJson["downloadfilename"] = f'biomuta-searchresults-{timeStamp}.csv'

                with open(outputFile, 'w') as FW:
                    for i in range(len(objList1)):
                        FW.write(f"{','.join(map(str, objList1[i]))}\n")

            except Exception as e:
                outJson["taskStatus"] = 0
                outJson["errorMsg"] = str(e)

            return jsonify(outJson)

    # Register the resource with the API and the route
    api.add_resource(SearchBioMuta, '/searchBioMuta')
