
'''

When the /getProteinData endpoint is hit with appropriate JSON data, the response will include:

Mutation Table: Data related to the requested protein.
Plot Data: Two datasets for visual representation.
CSV File: A downloadable link to the CSV file containing the mutation table
'''
from flask import request, jsonify, make_response
from flask_restx import Resource
from pymongo import MongoClient

import time


def getProteinData_route(api, db):
    # MongoDB collections
    protein_collection = db['C_biomuta_protein']
    ann_collection = db['C_biomuta_protein_ann']
    do2uberon_collection = db['C_biomuta_do2uberon']
    mutation_eff_collection = db['C_biomuta_mutation_eff']
    mutation_freq_collection = db['C_biomuta_mutation_freq']
    mutation_pmid_collection = db['C_biomuta_mutation_pmid']
    mutation_collection = db['C_biomuta_mutation']

    class GetProteinData(Resource):
        def post(self):
            inJson = request.json
            field_value = inJson.get("fieldvalue", "").strip().lower()

            try:
                # Start timer for the overall process
                start_time = time.time()

                # Fetch protein data
                start_protein_fetch = time.time()
                protein = protein_collection.find_one({"canonicalAc": {"$regex": field_value, "$options": "i"}})
                end_protein_fetch = time.time()
                print(f"Protein fetch time: {end_protein_fetch - start_protein_fetch} seconds")

                if not protein:
                    return make_response(jsonify({"taskStatus": 0, "errorMsg": "Protein not found"}), 404)

                canonicalAc = protein['canonicalAc']
                geneName = protein.get('geneName', 'Unknown Gene')
                geneDesc = protein.get('description', 'Unknown Description').split("OS=")[0]

                # Fetch annotations
                start_ann_fetch = time.time()
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
                end_ann_fetch = time.time()
                print(f"Annotation fetch time: {end_ann_fetch - start_ann_fetch} seconds")

                # Fetch doid to uberon mappings
                start_doid_fetch = time.time()
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
                end_doid_fetch = time.time()
                print(f"DOID to Uberon fetch time: {end_doid_fetch - start_doid_fetch} seconds")

                # Fetch cancer id to doName mappings
                start_cancerid_fetch = time.time()
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
                end_cancerid_fetch = time.time()
                print(f"Cancer ID to doName fetch time: {end_cancerid_fetch - start_cancerid_fetch} seconds")

                # Fetch positional frequency data
                start_freq_fetch = time.time()
                countHash2 = {}
                freq_data = mutation_freq_collection.aggregate([
                    {"$match": {"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}}},
                    {"$group": {"_id": "$posInPep", "frequency": {"$sum": "$frequency"}}}
                ])
                for item in freq_data:
                    countHash2[item['_id']] = item['frequency']
                end_freq_fetch = time.time()
                print(f"Positional frequency fetch time: {end_freq_fetch - start_freq_fetch} seconds")

                plotData1 = [{"x": k, "y1": v} for k, v in sorted(countHash1.items(), key=lambda x: x[1], reverse=True)]
                plotData2 = [{"x": k, "y1": v} for k, v in sorted(countHash2.items())]

                # Fetch mutation ids to PMIDs
                start_pmid_fetch = time.time()
                mutationid2pmid = {}
                pmid_data = mutation_pmid_collection.find({"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}})
                for pmid in pmid_data:
                    mutationid2pmid[pmid['mutationId']] = pmid['pmId']
                end_pmid_fetch = time.time()
                print(f"PMID fetch time: {end_pmid_fetch - start_pmid_fetch} seconds")

                # Construct the mutation table with correctly aligned columns
                start_table_construct = time.time()
                mutation_table = []
                mutation_effects = mutation_eff_collection.find({"canonicalAc": canonicalAc})
                for effect in mutation_effects:
                    # Fetch the chr value from the biomuta_mutation collection
                    mutation = mutation_collection.find_one({"_id": effect["mutationId"]})
                    chr_value = mutation.get("chr", '') if mutation else ''

                    # Fetch frequency and data source
                    freq_info = mutation_freq_collection.find_one({"mutationId": effect["mutationId"]})
                    frequency = freq_info.get('frequency', 0) if freq_info else 0
                    data_source = freq_info.get('dataSrc', '') if freq_info else ''

                    # Fetch UniProt annotations
                    uniprot_annotation = ann_collection.find_one({
                        "canonicalAc": canonicalAc,
                        "annType": "uniprot",
                        "startPos": {"$lte": effect['posInPep']},
                        "endPos": {"$gte": effect['posInPep']}
                    })
                    uniprot_annotation_value = f"{uniprot_annotation['annName']}({uniprot_annotation['annValue']})" if uniprot_annotation else 'NA'

                    # Corrected row data to match the table headers
                    row = [
                        chr_value,  # Chr
                        effect.get('posInPep', ''),  # Pos in Pep
                        effect.get('refCodon', ''),  # Ref Codon
                        effect.get('altCodon', ''),  # Alt Codon
                        effect.get('refResidue', ''),  # Ref Residue (corrected)
                        effect.get('altResidue', ''),  # Alt Residue (corrected)
                        cancerid2doname.get(effect.get('cancerId', ''), ''),  # Cancer
                        doid2uberonid1.get(effect.get('cancerId', ''), ''),  # DOID-Uberon
                        frequency,  # Frequency (corrected)
                        data_source,  # Data Source (corrected)
                        uniprot_annotation_value,  # UniProt Annotation (corrected)
                        annHash.get('netnglyc', {}).get(f"{effect['posInPep']}:{effect['refResidue']}:{effect['altResidue']}", ""),  # NetNGlyc Annotation (corrected)
                        mutationid2pmid.get(effect['mutationId'], "NA")  # PMID
                    ]
                    mutation_table.append(row)
                end_table_construct = time.time()
                print(f"Mutation table construction time: {end_table_construct - start_table_construct} seconds")

                # Prepare the final output
                outJson = {
                    "taskStatus": 1,
                    "inJson": inJson,
                    "mutationtable": mutation_table,
                    "plotdata1": plotData1,
                    "plotdata2": plotData2
                }

                end_time = time.time()
                print(f"Total processing time: {end_time - start_time} seconds")

                return make_response(jsonify(outJson), 200)

            except Exception as e:
                return make_response(jsonify({"taskStatus": 0, "errorMsg": str(e)}), 500)

    # Register the resource with the API and the route directly without namespace
    api.add_resource(GetProteinData, '/getProteinData')