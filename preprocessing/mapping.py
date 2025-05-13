import pandas as pd
import os
from typing import Dict, List, Union, Optional


def map_uniprot_to_identifiers(
    primary_file: str,
    uniprot_column: str,
    mapping_files: List[Dict[str, str]],
    output_file: Optional[str] = None
) -> pd.DataFrame:
    """
    Maps UniProt accession numbers to various identifiers across multiple files.
    
    Args:
        primary_file: Path to the CSV file containing UniProt accession numbers
        uniprot_column: Column name containing UniProt accession numbers in the primary file
        mapping_files: List of dictionaries with keys:
            - 'file': Path to mapping CSV file
            - 'uniprot_column': Column name for UniProt accession in this file
            - 'identifier_column': Column name for the identifier to map to
            - 'identifier_type': Type of identifier (for naming the output column)
        output_file: Optional path to save the resulting DataFrame as CSV
    
    Returns:
        DataFrame with UniProt accession numbers and all mapped identifiers
    """
    # Read primary file with UniProt accession numbers
    try:
        primary_df = pd.read_csv(primary_file, sep=None, engine='python')
    except Exception as e:
        raise ValueError(f"Error reading primary file {primary_file}: {str(e)}")
    
    # Validate primary file has the UniProt column
    if uniprot_column not in primary_df.columns:
        raise ValueError(f"UniProt column '{uniprot_column}' not found in primary file. Available columns: {', '.join(primary_df.columns)}")
    
    # Create result DataFrame with UniProt accessions
    result = primary_df[[uniprot_column]].copy()
    
    # Process each mapping file
    for mapping_info in mapping_files:
        try:
            # Extract mapping information
            map_file = mapping_info['file']
            map_uniprot_col = mapping_info['uniprot_column']
            map_id_col = mapping_info['identifier_column']
            id_type = mapping_info['identifier_type']
            
            # Read mapping file
            mapping_df = pd.read_csv(map_file, sep=None, engine='python')
            
            # Validate mapping file columns
            required_cols = [map_uniprot_col, map_id_col]
            missing_cols = [col for col in required_cols if col not in mapping_df.columns]
            if missing_cols:
                print(f"Warning: Columns {', '.join(missing_cols)} not found in {map_file}. Skipping this mapping file.")
                print(f"Available columns: {', '.join(mapping_df.columns)}")
                continue
                
            # Create a mapping dictionary for fast lookups
            id_map = dict(zip(mapping_df[map_uniprot_col].str.strip(), mapping_df[map_id_col].str.strip()))
            
            # Create output column name
            output_col_name = f"{id_type}"
            
            # Apply mapping to result DataFrame
            result[output_col_name] = result[uniprot_column].str.strip().map(id_map)
            
        except Exception as e:
            print(f"Warning: Error processing mapping file {mapping_info['file']}: {str(e)}")
            continue
    
    # Save to output file if specified
    if output_file:
        result.to_csv(output_file, index=False)
        print(f"Mapping results saved to {output_file}")
    
    return result


def example_usage():
    """Example of how to use the mapping function"""
    # Define primary file with UniProt accessions
    primary_file = "/data/shared/repos/biomuta-old/generated_datasets/compiled/biomuta_v6.1.csv"
    uniprot_column = "uniprotkb_canonical_ac"
    
    # Define mapping files
    mapping_files = [
        {
            'file': 'gene_names.csv',
            'uniprot_column': 'UniProt_Accession',
            'identifier_column': 'Gene_Name',
            'identifier_type': 'Gene_Name'
        },
        {
            'file': 'ensembl_ids.csv',
            'uniprot_column': 'Accession',
            'identifier_column': 'Ensembl_ID',
            'identifier_type': 'Ensembl_ID'
        },
        # Add more mapping files as needed
    ]
    
    # Perform mapping
    result = map_uniprot_to_identifiers(
        primary_file=primary_file,
        uniprot_column=uniprot_column,
        mapping_files=mapping_files,
        output_file="uniprot_mapped_identifiers.csv"
    )
    
    # Show first few rows of the result
    print(result.head())


if __name__ == "__main__":
    example_usage()