from flask import request, jsonify, make_response
from flask_restx import Resource
from pymongo import MongoClient
import time
import datetime
import os

def getProteinData_route(api, db):
    # MongoDB collections
    protein_collection = db['C_biomuta_protein']
    ann_collection = db['C_biomuta_protein_ann']
    cancer_collection = db['C_biomuta_cancer']
    mutation_eff_collection = db['C_biomuta_mutation_eff']
    mutation_freq_collection = db['C_biomuta_mutation_freq']
    mutation_pmid_collection = db['C_biomuta_mutation_pmid']
    mutation_collection = db['C_biomuta_mutation']
    do2uberon_collection = db['C_biomuta_do2uberon']

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
                        # Ensure annValue is treated as a string
                        annValue = str(ann['annValue']).replace(";", "")
                        annHash[annType][key].append(f"{ann['annName']}:{annValue}")

                # Consolidate annotations in annHash
                for annType in annHash:
                    for key in annHash[annType]:
                        annHash[annType][key] = "; ".join(sorted(set(annHash[annType][key])))


                    

                # Build mutation_id to pmid mapping
                mutationid2pmid = {}
                pmid_data = mutation_pmid_collection.find({"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}})
                for pmid in pmid_data:
                    mutationid2pmid[pmid['mutationId']] = pmid['pmId']

                # Fetch data for plot 1 (Cancer Type vs Frequency)
                countHash1 = {}
                cancer_data = mutation_freq_collection.aggregate([
                    {"$match": {"mutationId": {"$in": list(mutation_eff_collection.find({"canonicalAc": canonicalAc}).distinct("mutationId"))}}},
                    {"$lookup": {"from": "C_biomuta_cancer", "localField": "cancerId", "foreignField": "id", "as": "cancer"}},
                    {"$unwind": "$cancer"},
                    {"$group": {"_id": "$cancer.doName", "totalFrequency": {"$sum": "$frequency"}}}
                ])
                for item in cancer_data:
                    doName = item['_id']
                    countHash1[doName] = int(item['totalFrequency'])

                plotData1 = [{"x": k, "y1": v} for k, v in sorted(countHash1.items(), key=lambda x: x[1], reverse=True)]

                # 2. Fetch data for plot 2 (position in peptide vs frequency)
                pos_data = mutation_eff_collection.aggregate([
                {"$match": {
                    "canonicalAc": canonicalAc,
                    "refResidue": {"$ne": "altResidue"},
                    "altResidue": {"$ne": "*"}
                }},
                {"$lookup": {
                    "from": "C_biomuta_mutation_freq",
                    "localField": "id",  # Correcting the field used for lookup
                    "foreignField": "mutationId",  # Ensure 'mutationId' in freq collection corresponds to 'id' in eff collection
                    "as": "freqData"
                }},
                {"$unwind": "$freqData"},
                {"$group": {
                    "_id": "$posInPep",  # Group by position in peptide
                    "totalFrequency": {"$sum": "$freqData.frequency"}  # Sum the frequencies
                }},
                {"$sort": {"_id": 1}}  # Sort by position in peptide
            ])

                countHash2 = {}
                for item in pos_data:
                    pos = item['_id']  # This is now correctly referencing the peptide position
                    countHash2[pos] = int(item['totalFrequency'])

                # Generate plotData2 for the chart
                plotData2 = [{"x": pos, "y1": countHash2[pos]} for pos in sorted(countHash2)]

                # Fetch mutation effects and construct the mutation table
                mutation_table = []
                mutation_effects = mutation_eff_collection.find({"canonicalAc": canonicalAc}).limit(28)
                for effect in mutation_effects:
                    # Fetch the chr value from the biomuta_mutation collection
                    mutation = mutation_collection.find_one({"id": effect["mutationId"]})
                    chr_value = mutation.get("chr", '') if mutation else ''
                    pos_value = mutation.get("pos", '') if mutation else ''

                    # Fetch frequency, data source, and cancerId from the mutation_freq_collection
                    freq_info = mutation_freq_collection.find_one({"mutationId": effect["mutationId"]})
                    frequency = freq_info.get('frequency', 0) if freq_info else 0
                    data_source = freq_info.get('dataSrc', '') if freq_info else ''
                    cancer_id = freq_info.get('cancerId', '') if freq_info else ''

                    # Fetch the doName from the cancer collection using the cancer_id
                    cancer_info = cancer_collection.find_one({"id": cancer_id})
                    cancerType = cancer_info['doName'] if cancer_info else 'N/A'

                    # Fetch Uberon ID using the cancer ID from the do2uberon collection
                    uberon_info = do2uberon_collection.find_one({"doId": cancer_id})
                    UberonId = uberon_info['uberonId'] if uberon_info else 'N/A'

                    # Fetch UniProt annotations
                    uniprot_annotation = ann_collection.find_one({
                        "canonicalAc": canonicalAc,
                        "annType": "uniprot",
                        "startPos": {"$lte": effect['posInPep']},
                        "endPos": {"$gte": effect['posInPep']}
                    })
                    uniprot_annotation_value = f"{uniprot_annotation['annName']}({uniprot_annotation['annValue']})" if uniprot_annotation else 'NA'

                    # Construct functional predictions using NetNGlyc and PolyPhen annotations
                    key = f"{effect.get('posInPep', '')}:{effect.get('refResidue', '')}:{effect.get('altResidue', '')}"
                    functional_predictions = []
                    if "netnglyc" in annHash and key in annHash["netnglyc"]:
                        functional_predictions.append(annHash["netnglyc"][key].strip())
                    if "polyphen" in annHash and key in annHash["polyphen"]:
                        functional_predictions.append(annHash["polyphen"][key].strip())
                    functional_predictions_str = ";".join(sorted(set(functional_predictions))) if functional_predictions else 'NA'

                    # Corrected row data to match the table headers
                    row = [
                        mutation.get('chr', ''),
                        #chr_value,  # Chr
                        pos_value,  # genomic position
                        effect.get('posInPep', ''),  # Pos in Pep
                        effect.get('refCodon', ''),  # Ref Codon
                        effect.get('altCodon', ''),  # Alt Codon
                        effect.get('refResidue', ''),  # Ref Residue (corrected)
                        effect.get('altResidue', ''),  # Alt Residue (corrected)
                        cancerType,  #	DOID and term corresponding to reported cancer type
                        UberonId, #Uberon ID for corresponding anatomical entity
                        frequency,  # Frequency (corrected)
                        data_source,  # Data Source (corrected)
                        uniprot_annotation_value,  # UniProt Annotation (corrected)
                        functional_predictions_str,  # Functional Predictions
                        mutationid2pmid.get(effect['mutationId'], "NA")  # PMID (Corrected to use mutationid2pmid)
                    ]
                    mutation_table.append(row)
			# Define the directory as /tmp (inside the Docker container)
                output_directory = "/tmp"

                # Generate the filename with a timestamp
                timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
                output_filename = f"biomuta-protein-details-{canonicalAc}-{timeStamp}.csv"
                output_filepath = os.path.join(output_directory, output_filename)

                # Write the output to a CSV file in one operation
                header = ["Chr", "Chr Position","Protein Position", "Ref Codon", "Alt Codon", "Ref Residue", "Alt Residue", "Cancer Type", "UberonID", "Frequency", "Data Source", "UniProt Annotation", "Functional Predictions", "PMID"]
                with open(output_filepath, "w") as FW:
                    FW.write(",".join(header) + "\n")
                    for row in mutation_table:
                        FW.write(",".join([str(cell) for cell in row]) + "\n")
                
					
                # Prepare the final output
                outJson = {
                    "taskStatus": 1,
                    "inJson": inJson,
                    "mutationtable": mutation_table,
                    "downloadfilename": output_filename ,
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
