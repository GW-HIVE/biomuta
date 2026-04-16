import argparse
import csv
import json
import logging
import os, sys
import string
from Bio import SeqIO
from Bio.Seq import Seq

__version__ = "1.0"
__status__ = "Dev"

logging.basicConfig(filename="/data/shared/repos/biomuta/logs/codon_mapping.log",
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_codon_table(codon_file):
    """Load codon table from file"""
    codon_dic = {}
    with open(codon_file, "r") as tsvfile:
        for row in tsvfile:
            row = row.strip().split('\t')
            codon_dic[row[0]] = row[1]
    
    # Also create reverse lookup (amino acid to possible codons)
    aa_to_codons = {}
    for codon, aa in codon_dic.items():
        if aa not in aa_to_codons:
            aa_to_codons[aa] = []
        aa_to_codons[aa].append(codon)
    
    return codon_dic, aa_to_codons

def load_cds_sequences(cds_file):
    """Load CDS sequences from FASTA file"""
    cds_seq_hash = {}
    for record in SeqIO.parse(cds_file, "fasta"):
        cds_seq_hash[record.id.split(".")[0]] = str(record.seq.upper())
    return cds_seq_hash

def load_chromosome_sequences(chrom_file_pattern):
    """Load chromosome sequences from FASTA files"""
    chrom_seqs = {}
    for i in range(1, 23):
        chrom_file = chrom_file_pattern.format(i)
        if os.path.exists(chrom_file):
            for record in SeqIO.parse(chrom_file, "fasta"):
                chrom_seqs[str(i)] = str(record.seq.upper())
    
    # Also load X and Y chromosomes if they exist
    for chrom in ["X", "Y"]:
        chrom_file = chrom_file_pattern.format(chrom)
        if os.path.exists(chrom_file):
            for record in SeqIO.parse(chrom_file, "fasta"):
                chrom_seqs[chrom] = str(record.seq.upper())
    
    return chrom_seqs

def load_transcript_mapping(gtf_file):
    """
    Load transcript mapping from GTF file
    Returns dictionary with transcript IDs as keys and dictionaries of exon ranges as values
    """
    transcript_exons = {}
    with open(gtf_file, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            
            fields = line.strip().split("\t")
            if len(fields) < 9 or fields[2] != "exon":
                continue
            
            chrom = fields[0]
            start = int(fields[3])
            end = int(fields[4])
            strand = fields[6]
            
            attributes = fields[8].split(";")
            transcript_id = None
            for attr in attributes:
                if "transcript_id" in attr:
                    transcript_id = attr.split('"')[1]
                    break
            
            if transcript_id:
                if transcript_id not in transcript_exons:
                    transcript_exons[transcript_id] = {
                        "chrom": chrom,
                        "strand": strand,
                        "exons": []
                    }
                transcript_exons[transcript_id]["exons"].append((start, end))
    
    # Sort exons for each transcript
    for transcript_id in transcript_exons:
        transcript_exons[transcript_id]["exons"].sort()
    
    return transcript_exons

def get_cds_position(transcript_info, genomic_pos):
    """
    Maps genomic position to CDS position
    Returns CDS position (0-based)
    """
    cds_pos = 0
    strand = transcript_info["strand"]
    exons = transcript_info["exons"]
    
    if strand == "+":
        for start, end in exons:
            if genomic_pos < start:
                return None  # Position is before this exon
            elif start <= genomic_pos <= end:
                return cds_pos + (genomic_pos - start)
            else:
                cds_pos += (end - start + 1)
    else:  # strand == "-"
        for start, end in reversed(exons):
            if genomic_pos > end:
                return None  # Position is after this exon
            elif start <= genomic_pos <= end:
                return cds_pos + (end - genomic_pos)
            else:
                cds_pos += (end - start + 1)
    
    return None  # Position not found in any exon

def map_mutation_to_codon(mut_row, transcript_mapping, cds_sequences, codon_table):
    """
    Maps a mutation to codon and CDS position
    mut_row format: uniprot_id, chrom, pos, ref_nt, mut_nt, ref_aa, mut_aa, aa_pos
    """
    uniprot_id = mut_row[10].split("-")[0]
    chrom = mut_row[1]
    pos = int(mut_row[2])
    ref_nt = mut_row[4]
    mut_nt = mut_row[5]
    ref_aa = mut_row[7]
    mut_aa = mut_row[8]
    aa_pos = int(mut_row[6])
    
    # Find matching transcript
    # In real implementation, you would need a mapping from UniProt ID to Ensembl transcript ID
    # For this example, we'll just loop through all transcripts and find one that matches
    
    matching_transcripts = []
    for transcript_id, transcript_info in transcript_mapping.items():
        if transcript_id not in cds_sequences:
            continue
            
        cds_sequence = cds_sequences[transcript_id]
        cds_pos = get_cds_position(transcript_info, pos)
        
        if cds_pos is None:
            continue
        
        # Calculate codon position and codon index
        codon_index = cds_pos // 3
        pos_in_codon = cds_pos % 3
        
        # Get reference codon
        ref_codon = cds_sequence[codon_index*3:codon_index*3+3]
        
        # Calculate mutated codon
        mut_codon_list = list(ref_codon)
        mut_codon_list[pos_in_codon] = mut_nt
        mut_codon = "".join(mut_codon_list)
        
        # Verify amino acid matches
        if codon_table.get(ref_codon) == ref_aa and codon_table.get(mut_codon) == mut_aa:
            matching_transcripts.append({
                "transcript_id": transcript_id,
                "cds_pos": cds_pos,
                "codon_index": codon_index,
                "pos_in_codon": pos_in_codon,
                "ref_codon": ref_codon,
                "mut_codon": mut_codon
            })
    
    return matching_transcripts

def infer_codon_from_aa(aa_pos, ref_aa, mut_aa, cds_seq, aa_to_codons):
    """
    Infer possible codons from amino acid information
    Returns list of possible combinations (ref_codon, mut_codon, cds_pos)
    """
    results = []
    
    # Check if amino acid position is valid
    cds_pos = (aa_pos - 1) * 3
    if cds_pos + 2 >= len(cds_seq):
        return results
    
    # Get actual codon at this position
    actual_codon = cds_seq[cds_pos:cds_pos+3]
    
    # If the actual codon translates to the expected reference amino acid
    if ref_aa in aa_to_codons and actual_codon in aa_to_codons[ref_aa]:
        # For each possible mutated codon
        if mut_aa in aa_to_codons:
            for mut_codon in aa_to_codons[mut_aa]:
                # Count differences between reference and mutated codon
                diff_count = sum(1 for i in range(3) if actual_codon[i] != mut_codon[i])
                
                # If only one nucleotide differs, this is a valid mutation
                if diff_count == 1:
                    # Find position of mutation within codon
                    for i in range(3):
                        if actual_codon[i] != mut_codon[i]:
                            results.append({
                                "ref_codon": actual_codon,
                                "mut_codon": mut_codon,
                                "cds_pos": cds_pos,
                                "pos_in_codon": i,
                                "genomic_pos_offset": i
                            })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Infer reference and mutated codons from mutation data")
    parser.add_argument("-c", "--config", required=True, help="Configuration file")
    parser.add_argument("-m", "--mutations", required=True, help="Mutations file")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    args = parser.parse_args()
    
    config_json = json.loads(open(args.config, "r").read())
    logger.info("Starting codon mapping")
    
    # Load resources
    codon_dic, aa_to_codons = load_codon_table(config_json["codonfile"])
    logger.info(f"Loaded codon table from {config_json['codonfile']}")
    cds_sequences = load_cds_sequences(config_json["cdsfile"])
    logger.info(f"Loaded {len(cds_sequences)} CDS sequences")
    
    # Optionally load transcript mapping if available
    transcript_mapping = {}
    if "gtffile" in config_json:
        transcript_mapping = load_transcript_mapping(config_json["gtffile"])
        logger.info(f"Loaded {len(transcript_mapping)} transcripts from GTF")
    
    # Process mutations
    header = [
        "uniprot_id"
        ,"chrom"
        ,"pos"
        ,"ref_nt"
        ,"mut_nt"
        ,"ref_aa"
        ,"mut_aa"
        ,"aa_pos"
        ,"ref_codon"
        ,"mut_codon"
        ,"cds_pos"
        ,"pos_in_codon"
        ,"transcript_id"
    ]

    with open(args.mutations, "r") as f_in, open(args.output, "w") as f_out:
        # Write header
        writer = csv.writer(f_out, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        
        # Read the mutations CSV file
        reader = csv.reader(f_in, delimiter=',')
        next(reader)  # Skips the header row
        
        # Process each mutation
        for row in reader:
            uniprot_id = row[10].split("-")[0]
            chrom = row[1]
            pos = row[2]
            ref_nt = row[4]
            mut_nt = row[5]
            ref_aa = row[7]
            mut_aa = row[8]
            aa_pos = row[6]

            logger.info(f"Processing mutation: {uniprot_id} {ref_aa}{aa_pos}{mut_aa}")
            
            # Find matching transcripts for this UniProt ID
            # In a real implementation, you would need a mapping from UniProt ID to Ensembl transcript ID
            # For this example, we'll use a simple approach
            
            possible_results = []
            
            # If we have transcript mapping data
            if transcript_mapping:
                # Try to find transcripts that match the mutation
                for transcript_id, transcript_info in transcript_mapping.items():
                    if transcript_info["chrom"] == chrom and transcript_id in cds_sequences:
                        cds_seq = cds_sequences[transcript_id]
                        
                        # Try to infer codon from amino acid information
                        results = infer_codon_from_aa(int(aa_pos), ref_aa, mut_aa, cds_seq, aa_to_codons)
                        
                        for result in results:
                            possible_results.append({
                                "uniprot_id": uniprot_id,
                                "transcript_id": transcript_id,
                                "ref_codon": result["ref_codon"],
                                "mut_codon": result["mut_codon"],
                                "cds_pos": result["cds_pos"],
                                "pos_in_codon": result["pos_in_codon"]
                            })
            
            # If we couldn't find any results, try a more general approach
            if not possible_results:
                logger.warning(f"No codon mapping found for {uniprot_id} {ref_aa}{aa_pos}{mut_aa}")
                # Try all possible reference codons for this amino acid
                if ref_aa in aa_to_codons:
                    for ref_codon in aa_to_codons[ref_aa]:
                        # Try all possible mutated codons for the mutated amino acid
                        if mut_aa in aa_to_codons:
                            for mut_codon in aa_to_codons[mut_aa]:
                                # Check if they differ by only one nucleotide
                                diff_pos = []
                                for i in range(3):
                                    if ref_codon[i] != mut_codon[i]:
                                        diff_pos.append(i)
                                
                                # If only one position differs and it matches our ref/mut nucleotides
                                if len(diff_pos) == 1 and ref_codon[diff_pos[0]] == ref_nt and mut_codon[diff_pos[0]] == mut_nt:
                                    cds_pos = (int(aa_pos) - 1) * 3
                                    pos_in_codon = diff_pos[0]
                                    
                                    possible_results.append({
                                        "uniprot_id": uniprot_id,
                                        "transcript_id": "INFERRED",
                                        "ref_codon": ref_codon,
                                        "mut_codon": mut_codon,
                                        "cds_pos": cds_pos,
                                        "pos_in_codon": pos_in_codon
                                    })
            
            # Write results
            for result in possible_results:
                writer.writerow([uniprot_id, chrom, pos, ref_nt, mut_nt, ref_aa, mut_aa, aa_pos, result['ref_codon'], result['mut_codon'], result['cds_pos'], result['pos_in_codon'], result['transcript_id']])
            
            # If no results were found, still write the original data with empty fields
            if not possible_results:
                writer.writerow(["UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN"])

    logger.info("Codon mapping complete")

if __name__ == "__main__":
    main()