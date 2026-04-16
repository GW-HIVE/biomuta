# BioMuta Data Release Pipeline

This pipeline is probably going to be applicable only to the BioMuta 6.0 release since the next release will take the portal into account from the start of the pipeline.

1. Remove unused columns from biomuta.csv
`bash /data/shared/repos/biomuta/download_scripts/cut_biomuta.sh`
This will generate `biomuta_thin.csv` in the Downloads directory.

2. Download GlyGen datasets that will be used in mapping
`bash /data/shared/repos/biomuta/download_scripts/dl_data.sh`
This will download some CSV files to the Downloads directory.

3. `preprocessing/codon_mapper.py`

4. `preprocessing/id_mapper.py`