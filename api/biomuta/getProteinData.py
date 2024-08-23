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

    class GetProteinData(Resource):
        def post(self):
            inJson = request.json
            field_value = inJson.get("fieldvalue", "").strip().lower()

            try:
                total_start_time = time.time()

                # Fetch protein data in one query
                protein = protein_collection.find_one({"canonicalAc": {"$regex": field_value, "$options": "i"}})
                if not protein:
                    return make_response(jsonify({"taskStatus": 0, "errorMsg": "Protein not found"}), 404)

                canonicalAc = protein['canonicalAc']

                # Fetch all necessary annotations, mutation effects, frequencies, and cancer data in fewer queries
                annotations = list(ann_collection.find({"canonicalAc": canonicalAc}))
                mutation_effects = list(mutation_eff_collection.find({"canonicalAc": canonicalAc}))
                mutation_ids = [effect["mutationId"] for effect in mutation_effects]

                # Use $in operator to fetch multiple documents in one query
                pmid_data = {pmid['mutationId']: pmid['pmId'] for pmid in mutation_pmid_collection.find({"mutationId": {"$in": mutation_ids}})}
                mutation_data = {mutation["id"]: mutation for mutation in mutation_collection.find({"id": {"$in": mutation_ids}})}
                freq_data = {freq["mutationId"]: freq for freq in mutation_freq_collection.find({"mutationId": {"$in": mutation_ids}})}
                cancer_ids = list(set(freq.get('cancerId', '') for freq in freq_data.values()))
                cancer_data = {cancer["id"]: cancer for cancer in cancer_collection.find({"id": {"$in": cancer_ids}})}

                # Process annotations
                annHash = {}
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

                # Construct the mutation table
                mutation_table = []
                for effect in mutation_effects:
                    mutation_id = effect["mutationId"]
                    mutation = mutation_data.get(mutation_id, {})
                    freq_info = freq_data.get(mutation_id, {})
                    cancer_info = cancer_data.get(freq_info.get('cancerId', ''), {})

                    # Fetch UniProt annotations
                    uniprot_annotation = next(
                        (ann for ann in annotations if ann["annType"] == "uniprot" and
                         ann["startPos"] <= effect['posInPep'] <= ann["endPos"]), None
                    )
                    uniprot_annotation_value = f"{uniprot_annotation['annName']}({uniprot_annotation['annValue']})" if uniprot_annotation else 'NA'

                    row = [
                        mutation.get("chr", ''),
                        effect.get('posInPep', ''),
                        effect.get('refCodon', ''),
                        effect.get('altCodon', ''),
                        effect.get('refResidue', ''),
                        effect.get('altResidue', ''),
                        freq_info.get('cancerId', ''),
                        cancer_info.get('doName', 'N/A'),
                        freq_info.get('frequency', 0),
                        freq_info.get('dataSrc', ''),
                        uniprot_annotation_value,
                        annHash.get('netnglyc', {}).get(f"{effect['posInPep']}:{effect['refResidue']}:{effect['altResidue']}", ""),
                        pmid_data.get(mutation_id, "NA")
                    ]
                    mutation_table.append(row)

                # Define the directory as /tmp (inside the Docker container)
                output_directory = "/tmp"

                # Generate the filename with a timestamp
                timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
                output_filename = f"biomuta-protein-details-{canonicalAc}-{timeStamp}.csv"
                output_filepath = os.path.join(output_directory, output_filename)

                # Write the output to a CSV file in one operation
                header = ["Chr", "Pos in Pep", "Ref Codon", "Alt Codon", "Ref Residue", "Alt Residue", "Cancer ID", "DoID", "Frequency", "Data Source", "UniProt Annotation", "NetNGlyc Annotation", "PMID"]
                with open(output_filepath, "w") as FW:
                    FW.write(",".join(header) + "\n")
                    for row in mutation_table:
                        FW.write(",".join([str(cell) for cell in row]) + "\n")

                outJson = {
                    "taskStatus": 1,
                    "inJson": inJson,
                    "mutationtable": mutation_table,
                    "downloadfilename": output_filename 
                }

                print(f"Total processing time: {time.time() - total_start_time} seconds")

                return make_response(jsonify(outJson), 200)

            except Exception as e:
                return make_response(jsonify({"taskStatus": 0, "errorMsg": str(e)}), 500)

    api.add_resource(GetProteinData, '/getProteinData')

