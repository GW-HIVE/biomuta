import pymongo
import sys
import argparse
import json


def main():

    parser = argparse.ArgumentParser(
        prog="create_indexes.py",
    )
    parser.add_argument("-s", "--server", help="tst/prd")
    options = parser.parse_args()
    if not options.server:
        parser.print_help()
        sys.exit(0)
    server = options.server
    if server.lower() not in {"tst", "prd"}:
        print('Invalid server name. Excepcts "tst" or "prd"')
        sys.exit(0)

    ### get config info for docker container creation
    config_obj = json.load(open("./config.json", "r"))

    host = "mongodb://127.0.0.1:"
    port = config_obj["dbinfo"]["port"][server]
    host_w_port = f"{host}{port}"
    db_name = config_obj["dbinfo"]["dbname"]
    db_user = config_obj["dbinfo"][db_name]["user"]
    db_pass = config_obj["dbinfo"][db_name]["password"]

    protein_collection_name = config_obj["dbinfo"][db_name]["protein"]
    mutation_eff_collection_name = config_obj["dbinfo"][db_name]["mutation_eff"]
    cancer_collection_name = config_obj["dbinfo"][db_name]["cancer"]
    do2uberon_collection_name = config_obj["dbinfo"][db_name]["do2uberon"]
    mutation_freq_collection_name = config_obj["dbinfo"][db_name]["mutation_freq"]
    mutation_pmid_collection_name = config_obj["dbinfo"][db_name]["mutation_pmid"]
    protein_ann_collection_name = config_obj["dbinfo"][db_name]["protein_ann"]

    try:
        client = pymongo.MongoClient(
            host_w_port,
            username=db_user,
            password=db_pass,
            authSource=db_name,
            authMechanism="SCRAM-SHA-1",
            serverSelectionTimeoutMS=10000,
        )
        client.server_info()
        dbh = client[db_name]

        ### create protein indexes on 'canonicalAc', 'geneName'
        protein_collection = dbh[protein_collection_name]
        protein_collection.create_index("canonicalAc", name="idx_canonicalAc")
        protein_collection.create_index("geneName", name="idx_geneName")
        indexes = protein_collection.list_indexes()
        print("protein indexes ========")
        for idx, index in enumerate(indexes):
            print(f"\t index {idx}: {index}")

        ### create mutation efficiency indexes on 'canonicalAc', 'mutationId', 'posInPep'
        mutation_eff_collection = dbh[mutation_eff_collection_name]
        mutation_eff_collection.create_index("canonicalAc", name="idx_canonicalAc")
        mutation_eff_collection.create_index("mutationId", name="idx_mutationId")
        mutation_eff_collection.create_index("posInPep", name="idx_posInPep")
        indexes = mutation_eff_collection.list_indexes()
        print("mutation_eff indexes ========")
        for idx, index in enumerate(indexes):
            print(f"\tindex {idx}: {index}")

        ### create cancer index on 'id'
        cancer_collection = dbh[cancer_collection_name]
        cancer_collection.create_index("id", name="idx_id")
        indexes = cancer_collection.list_indexes()
        print("cancer indexes ========")
        for idx, index in enumerate(indexes):
            print(f"\tindex {idx}: {index}")

        ### create do2uberon indexes on 'doId', 'uberonId'
        do2uberon_collection = dbh[do2uberon_collection_name]
        do2uberon_collection.create_index("doId", name="idx_doId")
        do2uberon_collection.create_index("uberonId", name="idx_uberonId")
        indexes = do2uberon_collection.list_indexes()
        print("do2uberon indexes ========")
        for idx, index in enumerate(indexes):
            print(f"\tindex {idx}: {index}")

        ### create mutation freq index on 'mutationId', 'cancerId'
        mutation_freq_collection = dbh[mutation_freq_collection_name]
        mutation_freq_collection.create_index("mutationId", name="idx_mutationId")
        mutation_freq_collection.create_index("cancerId", name="idx_cancerId")
        indexes = mutation_freq_collection.list_indexes()
        print("mutation_freq indexes ========")
        for idx, index in enumerate(indexes):
            print(f"\tindex {idx}: {index}")

        ### create mutation pmid index on 'mutationId', 'pmId'
        mutation_pmid_collection = dbh[mutation_pmid_collection_name]
        mutation_pmid_collection.create_index("mutationId", name="idx_mutationId")
        mutation_pmid_collection.create_index("pmId", name="idx_pmId")
        indexes = cancer_collection.list_indexes()
        print("mutation_pmid indexes ========")
        for idx, index in enumerate(indexes):
            print(f"\tindex {idx}: {index}")

        ### create protein ann index on 'canonicalAc', 'startPos', 'endPos', 'annType'
        protein_ann_collection = dbh[protein_ann_collection_name]
        protein_ann_collection.create_index("canonicalAc", name="idx_canonicalAc")
        protein_ann_collection.create_index("startPos", name="idx_startPos")
        protein_ann_collection.create_index("endPos", name="idx_endPos")
        protein_ann_collection.create_index("annType", name="idx_annType")
        indexes = protein_ann_collection.list_indexes()
        print("protein_ann indexes ========")
        for idx, index in enumerate(indexes):
            print(f"\tindex {idx}: {index}")

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
