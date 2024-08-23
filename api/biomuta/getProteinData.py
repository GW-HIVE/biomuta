from flask import request, jsonify, make_response
from flask_restx import Resource
from pymongo import MongoClient

import time
def getProteinData_route(api, db):
    # MongoDB collections
    protein_collection = db['C_biomuta_protein']
    ann_collection = db['C_biomuta_protein_ann']
    cancer_collection = db['C_biomuta_cancer']
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

                # Build mutation_id to pmid mapping
                mutationid2pmid = {}
                pmid_data = mutation_pmid_collection.find({"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}})
                for pmid in pmid_data:
                    mutationid2pmid[pmid['mutationId']] = pmid['pmId']

                # Fetch mutation effects and construct the mutation table
                mutation_table = []
                mutation_effects = mutation_eff_collection.find({"canonicalAc": canonicalAc}).limit(6)  # Limit to 5 rows
                for effect in mutation_effects:
                    # Fetch the chr value from the biomuta_mutation collection
                    mutation = mutation_collection.find_one({"_id": effect["mutationId"]})
                    chr_value = mutation.get("chr", '') if mutation else ''

                    # Fetch frequency, data source, and cancerId from the mutation_freq_collection
                    freq_info = mutation_freq_collection.find_one({"mutationId": effect["mutationId"]})
                    frequency = freq_info.get('frequency', 0) if freq_info else 0
                    data_source = freq_info.get('dataSrc', '') if freq_info else ''
                    cancer_id = freq_info.get('cancerId', '') if freq_info else ''

                    # Fetch the doName from the cancer collection using the cancer_id
                    cancer_info = cancer_collection.find_one({"id": cancer_id})
                    do_name = cancer_info['doName'] if cancer_info else 'N/A'

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
                        cancer_id,  # Cancer ID
                        do_name,  # doName from cancer collection
                        frequency,  # Frequency (corrected)
                        data_source,  # Data Source (corrected)
                        uniprot_annotation_value,  # UniProt Annotation (corrected)
                        annHash.get('netnglyc', {}).get(f"{effect['posInPep']}:{effect['refResidue']}:{effect['altResidue']}", ""),  # NetNGlyc Annotation (corrected)
                        mutationid2pmid.get(effect['mutationId'], "NA")  # PMID (Corrected to use mutationid2pmid)
                    ]
                    mutation_table.append(row)

                # Prepare the final output
                outJson = {
                    "taskStatus": 1,
                    "inJson": inJson,
                    "mutationtable": mutation_table,
                }

                end_time = time.time()
                print(f"Total processing time: {end_time - start_time} seconds")

                return make_response(jsonify(outJson), 200)

            except Exception as e:
                return make_response(jsonify({"taskStatus": 0, "errorMsg": str(e)}), 500)

    # Register the resource with the API and the route directly without namespace
    api.add_resource(GetProteinData, '/getProteinData')
