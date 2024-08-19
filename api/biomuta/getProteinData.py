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
		seen = {"mutationid":{}} 
               	count_hash = {"ann":{}, "doname":{}}
	
		fieldValue = '%' + inJson["fieldvalue"].lower().strip() + '%'
		sql = "SELECT canonicalAc, geneName,description FROM biomuta_protein WHERE lower(canonicalAc) LIKE '%s' " % (fieldValue)

                cur.execute(sql)
		row = cur.fetchone()
		canonicalAc = row[0]
		geneName = row[1]
		geneDesc = row[2].split("OS=")[0]


		annHash = {}
		sql = configJson["queries"]["query_5"]
                sql = sql.replace("QVALUE", canonicalAc)

		cur.execute(sql)
                for row in cur.fetchall():
			annType = row[4]
			if annType not in annHash:
				annHash[annType] = {}
			tmpList = []
			for pos in xrange(row[0],row[1]+1):
				key = str(pos) + ":" + row[2] + ":" + row[3]
				if key not in annHash[annType]:
					annHash[annType][key] = []
				annValue = row[6].replace(";", "")
				annHash[annType][key].append(row[5] + ":" + annValue)
		
		for annType in annHash:
			for key in annHash[annType]:
				annHash[annType][key] = "; ".join(sorted(set(annHash[annType][key])))
 
		doid2uberonid1 = {}
		doid2uberonid2 = {}
		sql = configJson["queries"]["query_10"]
                cur.execute(sql)
                for row in cur.fetchall():
			if row[0] not in doid2uberonid1:
				url = serverJson["rootinfo"]["uberonurl"] + row[1]
				link = "<a href=%s>UBERON:%s</a>" % (url, row[1])
				doid2uberonid1[row[0]] = [link]
				doid2uberonid2[row[0]] = ["UBERON" + row[1]]
			else:
				url = serverJson["rootinfo"]["uberonurl"] + row[1]
                                link = "<a href=%s>UBERON:%s</a>" % (url, row[1])
				doid2uberonid1[row[0]].append(link)
				doid2uberonid2[row[0]].append("UBERON" + row[1])
		for doId in doid2uberonid1:
			doid2uberonid1[doId] = "; ".join(doid2uberonid1[doId])
			doid2uberonid2[doId] = "; ".join(doid2uberonid2[doId])

		cancerid2doname = {}
		countHash1 = {}
                countHash2 = {}
                sql = configJson["queries"]["query_4"]
                sql = sql.replace("QVALUE", canonicalAc)
                cur.execute(sql)
		for row in cur.fetchall():
			cancerid2doname[row[0]] = row[1]
                        doName = row[1]
                        countHash1[doName] = int(row[2])


		sql = configJson["queries"]["query_6"]
                sql = sql.replace("QVALUE", canonicalAc)

                cur.execute(sql)
                for row in cur.fetchall():
                        pos = row[0]
                        countHash2[pos] = int(row[1])
		plotData1 = []
                plotData2 = []
                for t in sorted(countHash1.items(), key=lambda x: x[1], reverse=True):
                        plotData1.append({"x": t[0], "y1":t[1]})
                for pos in sorted(countHash2):
                        plotData2.append({"x": pos, "y1":countHash2[pos]})


		mutationid2pmid = {}
		sql = configJson["queries"]["query_7"]
                sql = sql.replace("QVALUE", canonicalAc)
                cur.execute(sql)
                for row in cur.fetchall():
                        mutationId = row[0]
                        mutationid2pmid[mutationId] = row[1]
			

		sql = configJson["queries"]["query_3"]
		sql = sql.replace("QVALUE", canonicalAc)
		


		cur.execute(sql)
		labelList = configJson["tableheaders"]["proteinview"]["labellist"]
		typeList = configJson["tableheaders"]["proteinview"]["typelist"]
		csvBuffer = ",".join(["UniProtKB AC"] + labelList) + '\n'
		objList = [labelList, typeList]
		
		for row in cur.fetchall():
			if row[-1] == "COSMIC":
				continue
			seen["mutationid"][row[0]] = True
			csvCollection = [canonicalAc]
			obj = []
			row = list(row)
			key = str(row[5]) + "::"
			annValue = ""
			tmp_ann_list = []
			if "uniprot" in annHash:
				if key in annHash["uniprot"]:
					tmp_ann_list.append(annHash["uniprot"][key])
			row.append("; ".join(tmp_ann_list))

			key = str(row[5]) + ":" + row[6] + ":" + row[7]
			annValue = ""
			tmp_ann_list = []
			if "netnglyc" in annHash:
				if key in annHash["netnglyc"]:
					tmp_ann_list.append(annHash["netnglyc"][key].strip())
                        if "polyphen" in annHash:
                                if key in annHash["polyphen"]:
					tmp_ann_list.append(annHash["polyphen"][key].strip())
			row.append(";".join(sorted(set(tmp_ann_list))))

	
			for j in range(1,len(row)):
				obj.append(row[j]);
				val = str(row[j])
				val = val.replace(',', '')
				csvCollection.append(val);

			csvCollection[-6] = cancerid2doname[row[-6]]
			obj[-6] = cancerid2doname[row[-6]]

			if obj[-6] not in count_hash["doname"]:
                                count_hash["doname"][obj[-6]] = 1
                        else:
                                count_hash["doname"][obj[-6]] += 1


			doId = cancerid2doname[row[-6]].split("/")[0].split(":")[1].strip()
			csvCollection[-5] = doid2uberonid2[doId]
                        obj[-5] = doid2uberonid1[doId]


			url = serverJson["rootinfo"]["dourl"] + obj[7].split("/")[0]
			obj[7] = "<a href=%s>%s<a>" % (url, obj[7]) 


			pmId = mutationid2pmid[row[0]] if row[0] in mutationid2pmid else ""
			url = serverJson["rootinfo"]["pubmedurl"] + pmId
			link = "<a href=%s>%s<a>" % (url, pmId) if pmId != "" else ""
			obj.append(link)
			csvCollection.append(pmId)
			objList.append(obj)
			csvBuffer += ', '.join(csvCollection) + '\n'
                       	
		mutCount = str(len(seen["mutationid"].keys()))

		for i in xrange(2, len(objList)):
			if objList[i][11].strip() == "":
				continue
			for ann in objList[i][11].strip().split(";"):
				ann = ann.strip().split(":")[0]
				if ann in count_hash["ann"]:
                                        count_hash["ann"][ann] += 1
                                else:
                                        count_hash["ann"][ann] = 1
			
			if objList[i][12].strip() == "":
				continue
			for ann in objList[i][12].strip().split(";"):
				ann = ann.split(":")[1]
				first = ann.split(" ")[0]
				if first in ["probably", "possibly"]:
					ann = first + " " + ann.split(" ")[1]
				else:
					ann = first
				if ann in count_hash["ann"]:
                                        count_hash["ann"][ann] += 1
                                else:
                                        count_hash["ann"][ann] = 1
				
		outJson = {"taskStatus":1, "inJson":inJson, 
			"mutationtable":objList,
			"plotdata1":plotData1, 
			"plotdata2":plotData2
		}
                
		rowCount = str(len(objList) - 2)
		query = inJson["fieldvalue"]
		outJson["pageconf"] = configJson["pageconf"]["proteinview"]
                for key in outJson["pageconf"]:
			if type(outJson["pageconf"][key]) is not dict:
				outJson["pageconf"][key] = outJson["pageconf"][key].replace("QVALUE", query)
				outJson["pageconf"][key] = outJson["pageconf"][key].replace("GENENAME", geneName)
				outJson["pageconf"][key] = outJson["pageconf"][key].replace("GENEDESC", geneDesc)
				outJson["pageconf"][key] = outJson["pageconf"][key].replace("BIOXPRESSURL", serverJson["rootinfo"]["bioxpressurl"] + query)
				outJson["pageconf"][key] = outJson["pageconf"][key].replace("MUTCOUNT",mutCount)
                            	outJson["pageconf"][key] = outJson["pageconf"][key].replace("ROWCOUNT",rowCount) 

		for t in sorted(countHash1.items(), key=lambda x: x[1], reverse=True):
			v = t[0]
			nn = str(count_hash["doname"][v]) if v in count_hash["doname"] else "0"
			k = t[0].split("/")[-1] + " (" + nn + ")"
			outJson["pageconf"]["sitefilters"]["cancertype"]["filterhash"][k] = v

		tmp_obj = {}
		for k in outJson["pageconf"]["sitefilters"]["uniprot"]["filterhash"]:
			v = outJson["pageconf"]["sitefilters"]["uniprot"]["filterhash"][k]
			if v in count_hash["ann"]:
				kk = k + " (" + str(count_hash["ann"][v]) + ")"
				tmp_obj[kk] = v
		outJson["pageconf"]["sitefilters"]["uniprot"]["filterhash"] = tmp_obj
		tmp_obj = {}
                for k in outJson["pageconf"]["sitefilters"]["predictions"]["filterhash"]:
                        v = outJson["pageconf"]["sitefilters"]["predictions"]["filterhash"][k]
                        if v in count_hash["ann"]:
                                kk = k + " (" + str(count_hash["ann"][v]) + ")"
                                tmp_obj[kk] = v
		outJson["pageconf"]["sitefilters"]["predictions"]["filterhash"] = tmp_obj


		timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
		outputFile =  serverJson["pathinfo"]["tmppath"] + "/biomuta-proteinview-" + timeStamp + ".csv" 
		outJson["downloadfilename"] = "biomuta-proteinview-" + timeStamp + ".csv"
		FW = open(outputFile, "w")
		FW.write("%s" % (csvBuffer))
        	FW.close()
		cmd = "chmod 777 " + outputFile
       		x = commands.getoutput(cmd)
		DBH.close()
	except Exception, e:
		outJson = {"inJson":inJson,"taskStatus":0}
                outJson["errorMsg"] = errorMsg if errorMsg != "" else str(e)
	

	print json.dumps(outJson, indent=4, separators=(',',':'))


if __name__ == '__main__':
        main()



'''
'''

When the /getProteinData endpoint is hit with appropriate JSON data, the response will include:

Mutation Table: Data related to the requested protein.
Plot Data: Two datasets for visual representation.
CSV File: A downloadable link to the CSV file containing the mutation table
'''
from flask import request, jsonify
from flask_restx import Resource, Namespace
from pymongo import MongoClient

def getProteinData_route(api, db):
    
    
    protein_collection = db['C_biomuta_protein']
    ann_collection = db['C_biomuta_protein_ann']
    do2uberon_collection = db['C_biomuta_do2uberon']
    mutation_eff_collection = db['C_biomuta_mutation_eff']
    mutation_freq_collection = db['C_biomuta_mutation_freq']
    mutation_pmid_collection = db['C_biomuta_mutation_pmid']

    class GetProteinData(Resource):
        def post(self):
            inJson = request.json
            field_value = inJson.get("fieldvalue", "").strip()

            try:
                # Fetch protein data
                protein = protein_collection.find_one({"canonicalAc": field_value})
                if not protein:
                    return jsonify({"taskStatus": 0, "errorMsg": "Protein not found"}), 404

                canonicalAc = protein['canonicalAc']
                geneName = protein.get('geneName', 'Unknown Gene')
                geneDesc = protein.get('description', 'Unknown Description').split("OS=")[0]

                # Fetch annotations
                annHash = {}
                annotations = ann_collection.find({"canonicalAc": canonicalAc})
                for ann in annotations:
                    annType = ann['annType']
                    if annType not in annHash:
                        annHash[annType] = {}
                    for pos in range(ann['startPos'], ann['endPos'] + 1):
                        key = f"{pos}:{ann['ref']}:{ann['alt']}"
                        if key not in annHash[annType]:
                            annHash[annType][key] = []
                        annHash[annType][key].append(f"{ann['annName']}:{ann['annValue']}".replace(";", ""))
                for annType in annHash:
                    for key in annHash[annType]:
                        annHash[annType][key] = "; ".join(sorted(set(annHash[annType][key])))

                # Fetch doid to uberon mappings
                doid2uberonid1 = {}
                doid2uberonid2 = {}
                doid2uberon_mappings = do2uberon_collection.find({})
                for mapping in doid2uberon_mappings:
                    url = f"http://fantom.gsc.riken.jp/5/sstar/UBERON:{mapping['uberonId']}"
                    link = f"<a href={url}>UBERON:{mapping['uberonId']}</a>"
                    doid2uberonid1.setdefault(mapping['doId'], []).append(link)
                    doid2uberonid2.setdefault(mapping['doId'], []).append(f"UBERON{mapping['uberonId']}")
                for doId in doid2uberonid1:
                    doid2uberonid1[doId] = "; ".join(doid2uberonid1[doId])
                    doid2uberonid2[doId] = "; ".join(doid2uberonid2[doId])

                # Fetch cancer id to doName mappings
                cancerid2doname = {}
                countHash1 = {}
                mutations = mutation_freq_collection.aggregate([
                    {"$match": {"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}}},
                    {"$lookup": {"from": "C_biomuta_cancer", "localField": "cancerId", "foreignField": "id", "as": "cancer"}},
                    {"$unwind": "$cancer"},
                    {"$group": {"_id": "$cancer.doName", "frequency": {"$sum": "$frequency"}}}
                ])
                for mutation in mutations:
                    cancerid2doname[mutation['_id']] = mutation['frequency']
                    countHash1[mutation['_id']] = mutation['frequency']

                # Fetch positional frequency data
                countHash2 = {}
                freq_data = mutation_freq_collection.aggregate([
                    {"$match": {"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}}},
                    {"$group": {"_id": "$posInPep", "frequency": {"$sum": "$frequency"}}}
                ])
                for item in freq_data:
                    countHash2[item['_id']] = item['frequency']

                plotData1 = [{"x": k, "y1": v} for k, v in sorted(countHash1.items(), key=lambda x: x[1], reverse=True)]
                plotData2 = [{"x": k, "y1": v} for k, v in sorted(countHash2.items())]

                # Fetch mutation ids to PMIDs
                mutationid2pmid = {}
                pmid_data = mutation_pmid_collection.find({"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}})
                for pmid in pmid_data:
                    mutationid2pmid[pmid['mutationId']] = pmid['pmId']

                # Construct the mutation table
                mutation_table = []
                mutation_effects = mutation_eff_collection.find({"canonicalAc": canonicalAc})
                for effect in mutation_effects:
                    row = [
                        effect.get('chr', ''),
                        effect.get('posInPep', ''),
                        effect.get('refCodon', ''),
                        effect.get('altCodon', ''),
                        effect.get('posInPep', ''),
                        effect.get('refResidue', ''),
                        effect.get('altResidue', ''),
                        cancerid2doname.get(effect.get('cancerId', ''), ''),
                        doid2uberonid1.get(effect.get('cancerId', ''), ''),
                        countHash2.get(effect.get('mutationId', ''), 0),
                        effect.get('dataSrc', ''),
                        annHash.get('uniprot', {}).get(f"{effect['posInPep']}:{effect['refResidue']}:{effect['altResidue']}", ""),
                        annHash.get('netnglyc', {}).get(f"{effect['posInPep']}:{effect['refResidue']}:{effect['altResidue']}", ""),
                        mutationid2pmid.get(effect['mutationId'], "")
                    ]
                    mutation_table.append(row)

                # Prepare the final output
                outJson = {
                    "taskStatus": 1,
                    "inJson": inJson,
                    "mutationtable": mutation_table,
                    "plotdata1": plotData1,
                    "plotdata2": plotData2
                }

                return outJson, 200

            except Exception as e:
                return {"taskStatus": 0, "errorMsg": str(e)}, 500

    # Register the resource with the API and the route
    api.add_resource(GetProteinData, '/getProteinData')
    
