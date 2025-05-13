#!/bin/bash

download_dir="/data/shared/repos/biomuta/downloads"

# Download Human Gene Expression (Normal) (for uberonId)
wget -P $download_dir https://data.glygen.org/ln2data/releases/data/v-2.7.1/reviewed/human_protein_expression_normal.csv

# Download Human Gene Symbols (for geneName)
wget -P $download_dir https://data.glygen.org/ln2data/releases/data/v-2.7.1/reviewed/human_protein_genenames_uniprotkb.csv
# Human Proteome Masterlist (UniProtKB) also has gene names
wget -P $download_dir https://data.glygen.org/ln2data/releases/data/v-2.7.1/reviewed/human_protein_masterlist.csv

# Download Human UniProtKB Xref RefSeq (for RefSeq ID "xref_id")
wget -P $download_dir https://data.glygen.org/ln2data/releases/data/v-2.8.1/reviewed/human_protein_xref_refseq.csv

# Download Human Transcript Locus (Ensembl Transcript coordinates) for peptideId
wget -P $download_dir https://data.glygen.org/ln2data/releases/data/v-2.8.1/reviewed/human_protein_transcriptlocus.csv