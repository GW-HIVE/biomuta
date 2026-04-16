# Prompt for do2uberon.py
I want to generate a new biomuta_do2uberon.json called biomuta_do2uberon_v6.1.json. I expect it to stay largely the same (preserves the incremental "id" json field), but updated with missing "doId" fields compared to what "do_name" in biomuta_v6.1.csv has.
What to do:
1. Take "do_name" from biomuta_v6.1.csv and extract the doId number, e.g., for "DOID:1612 / breast cancer" doId would be 1612. Skip doId that already exist in biomuta_do2uberon.json
2. Look up the "uniprotkb_canonical_ac" corresponding to that DOID in biomuta_v6.1.csv
3. Find the matching "uniprotkb_canonical_ac" in human_protein_expression_normal.csv and retrieve the corresponding "uberon_anatomical_id"
4. Write the tuple of doId, uberonId and id to biomuta_do2uberon_v6.1.json
For cases where a single DOID maps to multiple proteins, and a protein maps to multiple UBERON ID, log a warning

# Prompt for biomuta-protein.py
Input file 1: $ head biomuta_v6.1.csv "sample_name","chr_id","start_pos","end_pos","ref_nt","alt_nt","aa_pos","ref_aa","alt_aa","do_name","uniprotkb_canonical_ac","source","dbsnp_id" "","1","11117039","11117039","C","A","2327","M","I","DOID:1612 / breast cancer","P42345-1","civic",""
"","1","11124516","11124516","G","T","2215","S","Y","DOID:363 / uterine cancer","P42345-1","civic",""
"","1","11124523","11124523","G","A","2213","P","S","DOID:4159 / skin cancer","P42345-1","civic",""
"","1","11127037","11127037","G","T","2108","F","L","DOID:1781 / thyroid gland cancer","P42345-1","civic",""
"","1","11127037","11127037","G","T","2108","F","L","DOID:1612 / breast cancer","P42345-1","civic",""
"","1","11127739","11127739","G","A","2034","A","V","DOID:1612 / breast cancer","P42345-1","civic",""
"","1","11128462","11128462","G","A","1968","H","Y","DOID:4159 / skin cancer","P42345-1","civic",""
"","1","11130747","11130747","C","T","1799","E","K","DOID:263 / kidney cancer","P42345-1","civic",""
"","1","11796321","11796321","G","A","222","A","V","DOID:1793 / pancreatic cancer","P42898","civic",""

Input file 2: biomuta_protein.json
[ { "peptideId": "ENSP00000305529", "geneName": "SIRPG", "canonicalAc": "Q9P1W8-1", "description": "Signal-regulatory protein gamma", "refseqAc": "NP_061026.2", "id": 1 }, { "peptideId": "ENSP00000334675", "geneName": "ERCC6L", "canonicalAc": "Q2NKX8-1", "description": "DNA excision repair protein ERCC-6-like", "refseqAc": "NP_060139.2", "id": 2 }, { "peptideId": "ENSP00000455442", "geneName": "NUPR2", "canonicalAc": "A6NF83-1", "description": "Nuclear protein 2", "refseqAc": "NP_001139184.1", "id": 3 }, { "peptideId": "ENSP00000354583", "geneName": "MFAP3L", "canonicalAc": "O75121-1", "description": "Microfibrillar-associated protein 3-like", "refseqAc": "NP_067679.6", "id": 4 }, { "peptideId": "ENSP00000274368", "geneName": "CRHBP", "canonicalAc": "P24387-1", "description": "Corticotropin-releasing factor-binding protein", "refseqAc": "NP_001873.2", "id": 5 }, ...] 

Mapping file 1: $ /data/shared/repos/biomuta/downloads/head human_protein_transcriptlocus.csv
"uniprotkb_canonical_ac","uniprotkb_isoform_ac","transcript_id","peptide_id","chromosome_id","start_pos","end_pos","strand"
"O75818-1","X6RLL4-1","ENST00000464646.1","ENSP00000419431.1","6","5002188","4995081","1"
"Q8TDG4-1","E3W980-1","ENST00000510985.1","ENSP00000424539.1","4","83455693","83407456","1"
"P30613-1","P30613-1","ENST00000572740.1","ENSP00000459921.1","HSCHR1_2_CTG31","106418","95598","1"
"P30613-1","P30613-2","ENST00000571194.5","ENSP00000461487.1","HSCHR1_2_CTG31","105910","95598","1"
"P30613-1","A0A0G2JLC7-1","ENST00000573938.1","ENSP00000459447.1","HSCHR1_2_CTG31","105979","105171","1"
"P30613-1","F8W6W2-1","ENST00000434082.3","ENSP00000398037.3","1","155300188","155295135","1"
"P50213-1","H0YKD0-1","ENST00000559186.5","ENSP00000452754.1","15","78157608","78161768","0"
"Q9BQI5-1","A0A804HJJ5-1","ENST00000682054.1","ENSP00000508116.1","1","66534359","66743092","0"
"A0A1B0GX78-1","A0A0J9YY10-1","ENST00000632829.1","ENSP00000488633.1","HSCHR7_2_CTG6","584699","585143","0"

Mapping file 2: $ head /data/shared/repos/biomuta/downloads/human_protein_masterlist.csv
"uniprotkb_canonical_ac","status","gene_name","reviewed_isoforms","unreviewed_isoforms"
"Q658T7-1","reviewed","FAM90A2P","Q658T7-1",""
"Q658T7-1","reviewed","FAM90A2P","Q658T7-2",""
"P30613-1","reviewed","PKLR","P30613-1","A0A0G2JLC7-1"
"P30613-1","reviewed","PKLR","P30613-2","F8W6W2-1"
"Q5MIZ7-1","reviewed","PPP4R3B","Q5MIZ7-1",""
"Q5MIZ7-1","reviewed","PPP4R3B","Q5MIZ7-2",""
"Q5MIZ7-1","reviewed","PPP4R3B","Q5MIZ7-3",""
"Q5MIZ7-1","reviewed","PPP4R3B","Q5MIZ7-4",""
"Q5MIZ7-1","reviewed","PPP4R3B","Q5MIZ7-5",""

Mapping file 3: $ head /data/shared/repos/biomuta/downloads/human_protein_xref_refseq.csv
"uniprotkb_canonical_ac","xref_key","xref_id","xref_label"
"P30613-1","protein_xref_refseq","NP_000289",""
"Q96J66-1","protein_xref_refseq","NP_115972",""
"Q96J65-1","protein_xref_refseq","NP_150229",""
"P40424-1","protein_xref_refseq","NP_001191892",""
"P40425-1","protein_xref_refseq","NP_002577",""
"P40426-1","protein_xref_refseq","NP_001128250",""
"P40429-1","protein_xref_refseq","NP_001257420",""
"Q9H2I8-1","protein_xref_refseq","NP_114413",""
"H0YL14-1","protein_xref_refseq","NP_001243455",""

In this chat, print a Python script that generates a file called biomuta_protein6.1.json that has the same structure as biomuta_protein.json and starts the "id" field from 1. What to do:
1. From biomuta_v6.1.csv, take unique "uniprotkb_canonical_ac". This will be "canonicalAc" in biomuta_protein6.1.json. Keep in mind that biomuta_v6.1.csv is a large file.
2. In human_protein_transcriptlocus.csv, look up matching "uniprotkb_canonical_ac" from step 1 and retrieve "peptide_id". This will be "peptideId" in biomuta_protein6.1.json. If can't find in the "uniprotkb_canonical_ac" column, fall back to "uniprotkb_isoform_ac". If can't find there, fall back to "canonicalAc" from biomuta_protein.json. If can't find at all, log a warning.
3. In human_protein_masterlist.csv, look up matching "uniprotkb_canonical_ac" from step 1 and retrieve "gene_name". This will be "geneName" in biomuta_protein6.1.json. If can't find in the "uniprotkb_canonical_ac" column, fall back to "reviewed_isoforms", then to "unreviewed_isoforms". If can't find there, fall back to "canonicalAc" from biomuta_protein.json. If can't find at all, log a warning.
4. In human_protein_xref_refseq.csv, look up matching "uniprotkb_canonical_ac" from step 1 and retrieve "xref_id". This will be "refseqAc" in biomuta_protein6.1.json. If can't find in the "uniprotkb_canonical_ac" column, fall back to "canonicalAc" from biomuta_protein.json. Else log a warning.
5. Where "description" exists for a "canonicalAc" in biomuta_protein.json, copy it to biomuta_protein6.1.json. If new record, leave "description" empty.
6. Write missing "uniprotkb_canonical_ac" into a text file in /data/shared/repos/biomuta/generated/6.1/biomuta_protein_missing_canonical_ac.txt, one ID per row
What to include in the Python script:
1. Take cmd args specifying inputs and outputs. Mapping files can be hardcoded.
2. Use Python logging module with logging.basicConfig(filename="c_biomuta_protein_mapping.log", filemode='a', format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
3. Build full lookup tables once. Normalize peptide IDs once during loading, not during lookup.
4. Stream biomuta_v6.1.csv instead of loading full set
5. Avoid repeated dictionary .get() chains per record
6. Avoid repeated attribute indexing inside hot loops
7. only log unique missing keys once
8. Log success messages