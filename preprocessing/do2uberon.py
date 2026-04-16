# python do2uberon.py --biomuta_csv /data/shared/repos/biomuta-old/generated_datasets/compiled/biomuta_v6.1.csv --expression_csv /data/shared/repos/biomuta/downloads/human_protein_expression_normal.csv --do2uberon_json /data/shared/repos/biomuta/json_exports/biomuta_do2uberon.json --output_json /data/shared/repos/biomuta/generated/6.1/biomuta_do2uberon.json

import argparse
import csv
import json
import logging
import re

logging.basicConfig(
    filename="/data/shared/repos/biomuta/logs/do2uberon_mapping.log",
    filemode='a',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--biomuta_csv", required=True)
    parser.add_argument("--expression_csv", required=True)
    parser.add_argument("--do2uberon_json", required=True)
    parser.add_argument("--output_json", required=True)
    args = parser.parse_args()

    with open(args.do2uberon_json) as f:
        existing = json.load(f)

    existing_do_ids = {entry["doId"] for entry in existing}
    next_id = max(entry["id"] for entry in existing) + 1
    logging.info(f"Loaded {len(existing)} existing entries, next id={next_id}")

    # do_id -> set of uniprotkb_canonical_ac
    do_to_proteins = {}
    with open(args.biomuta_csv, newline='') as f:
        for row in csv.DictReader(f):
            match = re.match(r'DOID:(\d+)', row['do_name'])
            if not match:
                continue
            do_id = int(match.group(1))
            if do_id in existing_do_ids:
                continue
            do_to_proteins.setdefault(do_id, set()).add(row['uniprotkb_canonical_ac'])

    logging.info(f"Found {len(do_to_proteins)} new DOIDs to process")

    # uniprotkb_canonical_ac -> set of uberon ids (numeric)
    protein_to_uberon = {}
    with open(args.expression_csv, newline='') as f:
        for row in csv.DictReader(f):
            ac = row['uniprotkb_canonical_ac']
            match = re.match(r'UBERON:(\d+)', row['uberon_anatomical_id'])
            if not match:
                continue
            uberon_id = int(match.group(1))
            protein_to_uberon.setdefault(ac, set()).add(uberon_id)

    new_entries = []

    for do_id, proteins in do_to_proteins.items():
        uberon_ids = set()
        for protein in proteins:
            protein_uberons = protein_to_uberon.get(protein, set())
            if len(proteins) > 1 and len(protein_uberons) > 1:
                logging.warning(f"DOID:{do_id} maps to multiple proteins {proteins}, and protein {protein} maps to multiple UBERON IDs {protein_uberons}")
            uberon_ids.update(protein_uberons)
        if not uberon_ids:
            logging.warning(f"No UBERON mapping found for DOID:{do_id} (proteins: {proteins})")
            continue
        for uberon_id in uberon_ids:
            new_entries.append({"doId": do_id, "uberonId": uberon_id, "id": next_id})
            next_id += 1

    logging.info(f"Adding {len(new_entries)} new entries")
    output = existing + new_entries

    with open(args.output_json, 'w') as f:
        json.dump(output, f, indent=4)

    logging.info(f"Written to {args.output_json}")

if __name__ == "__main__":
    main()