import sys
from argparse import ArgumentParser
from pymongo import MongoClient

COLLECTION_LIST = [
    'C_biomuta.stats',
    'C_biomuta_do2uberon',
    'C_biomuta_cancer',
    'C_biomuta_protein',
    'C_biomuta_mutation_freq',
    'C_biomuta_mutation',
    'C_biomuta_mutation_pmid',
    'C_biomuta_protein_ann',
    'C_biomuta_mutation_eff'
]

def main():

    parser = ArgumentParser()
    for collection in COLLECTION_LIST:
        help_str = (
            f"Store true argument for the {collection.replace('_', ' ')} collection."
            if "collection" not in collection
            else f"Store true argument for the {collection.replace('_', ' ')}."
        )
        parser.add_argument(
            f"--{collection}",
            action="store_true",
            help=help_str,
        )
    parser.add_argument("-n", "--num", type=int, default=5)
    options = parser.parse_args()

    option_dict = options.__dict__
    option_list = [val for val in option_dict.values() if isinstance(val, bool)]
    if not any(option_list):
        print("Need to specify one collection.")
        parser.print_help()
        sys.exit(0)

    true_list = [x for x in option_list if x]
    if len(true_list) > 1:
        print("Too many collections passed, can only use one at a time.")
        parser.print_help()
        sys.exit(0)

    try:
        client = MongoClient(
            host=f"mongodb://127.0.0.1:8084",
            username='biomutaadmin',
            password='biomutapass',
            authSource='biomuta_db',
            authMechanism='SCRAM-SHA-1',
            serverSelectionTimeoutMS=1000,
        )
        dbh = client['biomuta_db']
    except Exception as e:
        msg = f"Failed to grab database handle: {str(e)}"
        print(msg)
        sys.exit(1)

    try:
        target_collection_idx = option_list.index(True)
        target_collection = COLLECTION_LIST[target_collection_idx]
        collection = dbh[target_collection]

        last_entries = collection.find().sort("_id", -1).limit(options.num)
        last_entries_list = list(last_entries)
        last_entries_list.reverse()

        for idx, entry in enumerate(last_entries_list):
            print(f"Entry: {idx + 1}:\n{entry}\n")
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()