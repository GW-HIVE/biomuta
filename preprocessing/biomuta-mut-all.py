# nohup python biomuta-mut-all.py /data/shared/repos/biomuta-old/generated_datasets/compiled/biomuta_v6.1.csv /data/shared/repos/biomuta/generated/current/biomuta_mutation.json /data/shared/repos/biomuta/generated/current/biomuta_mutation_freq.json /data/shared/repos/biomuta/generated/current/biomuta_mutation_eff.json &

import argparse
import csv
import json
import logging
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANCER_MAP_PATH = ROOT / "json_exports/biomuta_cancer.json"
GEN = ROOT / "generated/current"
CODON_MAP_PATH = GEN / "mapped_codons.csv"
IDENT_MAP_PATH = GEN / "uniprot_mapped_identifiers.csv"

logging.basicConfig(
    filename="/data/shared/repos/biomuta/logs/biomuta_mut_all.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

def load_cancer_map(path):
    with open(path) as f:
        records = json.load(f)
    return {r["doName"]: r["id"] for r in records}


def load_codon_map(path):
    codon_map = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (
                row["uniprot_id"],
                row["chrom"],
                row["pos"],
                row["ref_nt"],
                row["mut_nt"],
                row["ref_aa"],
                row["mut_aa"],
                row["aa_pos"],
            )
            codon_map.setdefault(key, []).append(row)
    return codon_map


def load_ident_map(path):
    ident_map = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["uniprotkb_canonical_ac"], row["transcriptId"].split(".")[0])
            ident_map.setdefault(key, []).append(row)
    return ident_map


def build_outputs(biomuta_path, cancer_map, codon_map, ident_map):
    mutation_index = {}
    mutations = []

    freq_index = {}

    eff_seen = set()
    effects = []

    with open(biomuta_path, newline="") as f:
        for row in csv.DictReader(f):
            chr_id = row["chr_id"]
            pos = row["start_pos"]
            ref_nt = row["ref_nt"]
            alt_nt = row["alt_nt"]
            do_name = row["do_name"]
            source = row["source"]
            canonical_ac = row["uniprotkb_canonical_ac"]
            aa_pos = row["aa_pos"]
            ref_aa = row["ref_aa"]
            alt_aa = row["alt_aa"]

            # --- biomuta_mutation.json ---
            mut_key = (chr_id, pos, ref_nt, alt_nt)
            if mut_key not in mutation_index:
                mut_id = len(mutations) + 1
                mutation_index[mut_key] = mut_id
                mutations.append({"id": mut_id, "ref": ref_nt, "alt": alt_nt, "pos": int(pos), "chr": chr_id})
            else:
                mut_id = mutation_index[mut_key]

            # --- biomuta_mutation_freq.json ---
            cancer_id = cancer_map.get(do_name)
            freq_key = (mut_key, do_name, source)
            if freq_key not in freq_index:
                freq_index[freq_key] = {
                    "mutationId": mut_id,
                    "cancerId": cancer_id,
                    "frequency": 1,
                    "dataSrc": source,
                }
            else:
                freq_index[freq_key]["frequency"] += 1

            # --- biomuta_mutation_eff.json ---
            uniprot_base = canonical_ac.split("-")[0]
            codon_key = (uniprot_base, chr_id, pos, ref_nt, alt_nt, ref_aa, alt_aa, aa_pos)
            codon_records = codon_map.get(codon_key, [])

            for codon in codon_records:
                transcript_id_bare = codon["transcript_id"].split(".")[0]
                ident_key = (canonical_ac, transcript_id_bare)
                ident_records = ident_map.get(ident_key, [])

                # Fall back to one effect record with nulls if no identifier match
                if not ident_records:
                    ident_records = [None]

                for ident in ident_records:
                    peptide_id = ident["peptideId"] if ident else None
                    refseq_ac = ident["refseqAc"] if ident else None

                    eff_key = (mut_id, codon["transcript_id"], peptide_id, codon["cds_pos"], codon["pos_in_codon"], codon["mut_codon"])
                    if eff_key in eff_seen:
                        continue
                    eff_seen.add(eff_key)

                    effects.append({
                        "mutationId": mut_id,
                        "transcriptId": codon["transcript_id"],
                        "peptideId": peptide_id,
                        "posInCds": int(codon["cds_pos"]),
                        "posInPep": int(aa_pos),
                        "posInCodon": int(codon["pos_in_codon"]),
                        "refCodon": codon["ref_codon"],
                        "altCodon": codon["mut_codon"],
                        "refResidue": ref_aa,
                        "altResidue": alt_aa,
                        "refseqAc": refseq_ac,
                        "canonicalAc": canonical_ac,
                        "posInCanonicalAc": int(aa_pos),
                        "posInRefAc": int(aa_pos),
                        "id": len(effects) + 1,
                    })

    freq_list = [{"id": i + 1, **v} for i, v in enumerate(freq_index.values())]

    return mutations, freq_list, effects


def write_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logging.info(f"Wrote {len(data)} records to {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate BioMuta JSON output files.")
    parser.add_argument("biomuta_csv", help="Path to biomuta_v6.1.csv")
    parser.add_argument("out_mutation", help="Output path for biomuta_mutation.json")
    parser.add_argument("out_freq", help="Output path for biomuta_mutation_freq.json")
    parser.add_argument("out_eff", help="Output path for biomuta_mutation_eff.json")
    args = parser.parse_args()

    logging.info("Loading cancer map...")
    cancer_map = load_cancer_map(CANCER_MAP_PATH)

    logging.info("Loading codon map...")
    codon_map = load_codon_map(CODON_MAP_PATH)

    logging.info("Loading identifier map...")
    ident_map = load_ident_map(IDENT_MAP_PATH)

    logging.info("Processing biomuta CSV...")
    mutations, freq_list, effects = build_outputs(args.biomuta_csv, cancer_map, codon_map, ident_map)

    write_json(mutations, args.out_mutation)
    write_json(freq_list, args.out_freq)
    write_json(effects, args.out_eff)


if __name__ == "__main__":
    main()