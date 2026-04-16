#!/usr/bin/env python3
# python biomuta-protein.py --biomuta-csv /data/shared/repos/biomuta-old/generated_datasets/compiled/biomuta_v6.1.csv --existing-protein-json /data/shared/repos/biomuta/json_exports/biomuta_protein.json --output-json /data/shared/repos/biomuta/generated/6.1/biomuta_protein.json

import argparse
import csv
import json
import logging
import requests
import time
from pathlib import Path


TRANSCRIPTLOCUS_CSV = "/data/shared/repos/biomuta/downloads/human_protein_transcriptlocus.csv"
MASTERLIST_CSV = "/data/shared/repos/biomuta/downloads/human_protein_masterlist.csv"
XREF_REFSEQ_CSV = "/data/shared/repos/biomuta/downloads/human_protein_xref_refseq.csv"


logging.basicConfig(
    filename="/data/shared/repos/biomuta/logs/biomuta_protein.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate biomuta_protein6.1.json from biomuta_v6.1.csv."
    )
    parser.add_argument(
        "--biomuta-csv",
        required=True,
        help="Path to biomuta.csv",
    )
    parser.add_argument(
        "--existing-protein-json",
        required=True,
        help="Path to biomuta_protein.json",
    )
    parser.add_argument(
        "--output-json",
        required=True,
        help="Path to biomuta_protein6.1.json",
    )
    parser.add_argument(
        "--missing-output",
        default="/data/shared/repos/biomuta/generated/current/biomuta_protein_unmapped_canonical_ac.txt",
        help="Path to write missing uniprotkb_canonical_ac values",
    )
    return parser.parse_args()


def normalize_peptide_id(value):
    if not value:
        return ""
    return value.split(".", 1)[0]


def first_non_empty(*values):
    for value in values:
        if value:
            return value
    return ""


def load_existing_proteins(path):
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    existing = {}
    for record in payload:
        canonical_ac = record.get("canonicalAc", "")
        if not canonical_ac or canonical_ac in existing:
            continue
        existing[canonical_ac] = {
            "peptideId": record.get("peptideId", "") or "",
            "geneName": record.get("geneName", "") or "",
            "description": record.get("description", "") or "",
            "refseqAc": record.get("refseqAc", "") or "",
        }

    logging.info("Loaded %d canonicalAc entries from existing protein JSON", len(existing))
    return existing


def load_transcriptlocus_maps(path):
    by_canonical = {}
    by_isoform = {}

    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            peptide_id = normalize_peptide_id(row["peptide_id"])
            if not peptide_id:
                continue

            canonical_ac = row["uniprotkb_canonical_ac"]
            isoform_ac = row["uniprotkb_isoform_ac"]

            if canonical_ac and canonical_ac not in by_canonical:
                by_canonical[canonical_ac] = peptide_id
            if isoform_ac and isoform_ac not in by_isoform:
                by_isoform[isoform_ac] = peptide_id

    logging.info(
        "Loaded transcript locus lookups: %d canonical, %d isoform",
        len(by_canonical),
        len(by_isoform),
    )
    return by_canonical, by_isoform


def load_masterlist_maps(path):
    by_canonical = {}
    by_reviewed = {}
    by_unreviewed = {}

    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            gene_name = row["gene_name"]
            if not gene_name:
                continue

            canonical_ac = row["uniprotkb_canonical_ac"]
            reviewed_isoform = row["reviewed_isoforms"]
            unreviewed_isoform = row["unreviewed_isoforms"]

            if canonical_ac and canonical_ac not in by_canonical:
                by_canonical[canonical_ac] = gene_name
            if reviewed_isoform and reviewed_isoform not in by_reviewed:
                by_reviewed[reviewed_isoform] = gene_name
            if unreviewed_isoform and unreviewed_isoform not in by_unreviewed:
                by_unreviewed[unreviewed_isoform] = gene_name

    logging.info(
        "Loaded masterlist lookups: %d canonical, %d reviewed isoform, %d unreviewed isoform",
        len(by_canonical),
        len(by_reviewed),
        len(by_unreviewed),
    )
    return by_canonical, by_reviewed, by_unreviewed


def load_refseq_map(path):
    by_canonical = {}

    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            canonical_ac = row["uniprotkb_canonical_ac"]
            refseq_id = row["xref_id"]
            if canonical_ac and refseq_id and canonical_ac not in by_canonical:
                by_canonical[canonical_ac] = refseq_id

    logging.info("Loaded refseq lookup: %d canonical", len(by_canonical))
    return by_canonical


def stream_unique_canonical_ac(path):
    seen = set()

    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        canonical_key = "uniprotkb_canonical_ac"
        for row in reader:
            canonical_ac = row[canonical_key]
            if not canonical_ac or canonical_ac in seen:
                continue
            seen.add(canonical_ac)
            yield canonical_ac


def write_missing_output(path, missing_ids):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        for canonical_ac in sorted(missing_ids):
            handle.write(f"{canonical_ac}\n")

UNIPROT_IDMAPPING_RUN = "https://rest.uniprot.org/idmapping/run"
UNIPROT_IDMAPPING_STATUS = "https://rest.uniprot.org/idmapping/status/{job_id}"
UNIPROT_IDMAPPING_RESULTS = "https://rest.uniprot.org/idmapping/results/{job_id}"


def submit_idmapping_job(ids, to_db):
    response = requests.post(
        UNIPROT_IDMAPPING_RUN,
        data={"from": "UniProtKB_AC-ID", "to": to_db, "ids": ",".join(ids)},
    )
    response.raise_for_status()
    return response.json()["jobId"]


def poll_idmapping_job(job_id, poll_interval=3, max_wait=120):
    url = UNIPROT_IDMAPPING_STATUS.format(job_id=job_id)
    elapsed = 0
    while elapsed < max_wait:
        response = requests.get(url, headers={"accept": "application/json"})
        response.raise_for_status()
        data = response.json()
        if "results" in data or "failedIds" in data:
            return data
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"UniProt ID mapping job {job_id} did not complete within {max_wait}s")


def fetch_idmapping_results(job_id):
    url = UNIPROT_IDMAPPING_RESULTS.format(job_id=job_id)
    response = requests.get(url, headers={"accept": "application/json"})
    response.raise_for_status()
    data = response.json()
    return {item["from"]: item["to"] for item in data.get("results", [])}


def batch_idmapping(ids, to_db, batch_size=500):
    results = {}
    ids = list(ids)
    for i in range(0, len(ids), batch_size):
        batch = ids[i: i + batch_size]
        try:
            job_id = submit_idmapping_job(batch, to_db)
            poll_idmapping_job(job_id)
            results.update(fetch_idmapping_results(job_id))
            logging.info("UniProt idmapping (%s): mapped %d/%d in batch", to_db, len(results), len(ids))
        except Exception as exc:
            logging.warning("UniProt idmapping (%s) batch failed: %s", to_db, exc)
    return results


def fallback_uniprot_mappings(missing_canonical, records):
    """Try to fill peptideId, geneName, refseqAc via UniProt ID mapping for still-missing entries."""
    missing_list = list(missing_canonical)
    if not missing_list:
        return

    logging.info("Falling back to UniProt ID mapping for %d canonical ACs", len(missing_list))

    record_by_ac = {r["canonicalAc"]: r for r in records}

    needs_peptide = [ac for ac in missing_list if not record_by_ac.get(ac, {}).get("peptideId")]
    needs_gene    = [ac for ac in missing_list if not record_by_ac.get(ac, {}).get("geneName")]
    needs_refseq  = [ac for ac in missing_list if not record_by_ac.get(ac, {}).get("refseqAc")]

    peptide_map = batch_idmapping(needs_peptide, "Ensembl_Protein") if needs_peptide else {}
    gene_map    = batch_idmapping(needs_gene,    "Gene_Name")        if needs_gene    else {}
    refseq_map  = batch_idmapping(needs_refseq,  "RefSeq_Protein")   if needs_refseq  else {}

    still_missing = set()
    for ac in missing_list:
        record = record_by_ac.get(ac)
        if not record:
            continue
        if not record["peptideId"] and ac in peptide_map:
            record["peptideId"] = normalize_peptide_id(peptide_map[ac])
        if not record["geneName"] and ac in gene_map:
            record["geneName"] = gene_map[ac]
        if not record["refseqAc"] and ac in refseq_map:
            record["refseqAc"] = refseq_map[ac]

        if not record["peptideId"] or not record["geneName"] or not record["refseqAc"]:
            still_missing.add(ac)

    missing_canonical.clear()
    missing_canonical.update(still_missing)
    logging.info("%d canonical ACs still missing after UniProt fallback", len(still_missing))

def main():
    args = parse_args()

    existing = load_existing_proteins(args.existing_protein_json)
    transcript_by_canonical, transcript_by_isoform = load_transcriptlocus_maps(TRANSCRIPTLOCUS_CSV)
    gene_by_canonical, gene_by_reviewed, gene_by_unreviewed = load_masterlist_maps(MASTERLIST_CSV)
    refseq_by_canonical = load_refseq_map(XREF_REFSEQ_CSV)

    existing_get = existing.get
    transcript_canonical_get = transcript_by_canonical.get
    transcript_isoform_get = transcript_by_isoform.get
    gene_canonical_get = gene_by_canonical.get
    gene_reviewed_get = gene_by_reviewed.get
    gene_unreviewed_get = gene_by_unreviewed.get
    refseq_canonical_get = refseq_by_canonical.get

    warned_peptide = set()
    warned_gene = set()
    warned_refseq = set()
    missing_canonical = set()
    records = []

    append_record = records.append
    add_missing = missing_canonical.add

    for record_id, canonical_ac in enumerate(stream_unique_canonical_ac(args.biomuta_csv), start=1):
        existing_record = existing_get(canonical_ac)
        if existing_record is None:
            existing_peptide = ""
            existing_gene = ""
            description = ""
            existing_refseq = ""
        else:
            existing_peptide = existing_record["peptideId"]
            existing_gene = existing_record["geneName"]
            description = existing_record["description"]
            existing_refseq = existing_record["refseqAc"]

        peptide_id = first_non_empty(
            transcript_canonical_get(canonical_ac),
            transcript_isoform_get(canonical_ac),
            existing_peptide,
        )
        if not peptide_id and canonical_ac not in warned_peptide:
            logging.warning("Missing peptideId for canonicalAc %s", canonical_ac)
            warned_peptide.add(canonical_ac)
            add_missing(canonical_ac)

        gene_name = first_non_empty(
            gene_canonical_get(canonical_ac),
            gene_reviewed_get(canonical_ac),
            gene_unreviewed_get(canonical_ac),
            existing_gene,
        )
        if not gene_name and canonical_ac not in warned_gene:
            logging.warning("Missing geneName for canonicalAc %s", canonical_ac)
            warned_gene.add(canonical_ac)
            add_missing(canonical_ac)

        refseq_ac = first_non_empty(
            refseq_canonical_get(canonical_ac),
            existing_refseq,
        )
        if not refseq_ac and canonical_ac not in warned_refseq:
            logging.warning("Missing refseqAc for canonicalAc %s", canonical_ac)
            warned_refseq.add(canonical_ac)
            add_missing(canonical_ac)

        append_record(
            {
                "peptideId": peptide_id,
                "geneName": gene_name,
                "canonicalAc": canonical_ac,
                "description": description,
                "refseqAc": refseq_ac,
                "id": record_id,
            }
        )

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)

    fallback_uniprot_mappings(missing_canonical, records)
    write_missing_output(args.missing_output, missing_canonical)

    logging.info("Wrote %d protein records to %s", len(records), args.output_json)
    logging.info(
        "Wrote %d missing canonicalAc values to %s",
        len(missing_canonical),
        args.missing_output,
    )
    logging.info("Output generation completed successfully")


if __name__ == "__main__":
    main()
