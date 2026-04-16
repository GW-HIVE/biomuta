#!/bin/bash

# This script has not been tested

download_dir="/data/shared/repos/biomuta/downloads"

# GLYGEN DOWNLOADS

# Download Human Gene Expression (Normal) (for uberonId)
wget -P --no-check-certificate $download_dir https://data.glygen.org/ln2data/releases/data/v-2.7.1/reviewed/human_protein_expression_normal.csv

# Download Human Gene Symbols (for geneName)
wget -P --no-check-certificate $download_dir https://data.glygen.org/ln2data/releases/data/v-2.7.1/reviewed/human_protein_genenames_uniprotkb.csv
# Human Proteome Masterlist (UniProtKB) also has gene names
wget -P --no-check-certificate $download_dir https://data.glygen.org/ln2data/releases/data/v-2.7.1/reviewed/human_protein_masterlist.csv

# Download Human UniProtKB Xref RefSeq (for RefSeq ID "xref_id")
wget -P --no-check-certificate $download_dir https://data.glygen.org/ln2data/releases/data/v-2.8.1/reviewed/human_protein_xref_refseq.csv

# Download Human Transcript Locus (Ensembl Transcript coordinates) for peptideId
wget -P --no-check-certificate $download_dir https://data.glygen.org/ln2data/releases/data/v-2.8.1/reviewed/human_protein_transcriptlocus.csv



# ENSEMBL DOWNLOADS

# Download CDS sequences in the FASTA format from Ensembl
## Question: is the filename versioned? For future downloads.
wget -P $download_dir https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/cds/Homo_sapiens.GRCh38.cds.all.fa.gz
gunzip $download_dir/Homo_sapiens.GRCh38.cds.all.fa.gz
# Download GTF
wget -P $download_dir https://ftp.ensembl.org/pub/current_gtf/homo_sapiens/Homo_sapiens.GRCh38.115.gtf.gz
gunzip $download_dir/Homo_sapiens.GRCh38.115.gtf.gz