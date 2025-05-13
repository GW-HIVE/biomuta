#!/bin/bash

inputfile="/data/shared/repos/biomuta-old/generated_datasets/compiled/biomuta_v6.1.csv"
outfile="/data/shared/repos/biomuta/downloads/biomuta_thin.csv"

cut --complement -f 1,4,13 -d, $inputfile > $outfile