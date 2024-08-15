import sys
import argparse
import json
from typing import Optional, Union
from pymongo import MongoClient, errors
from pymongo.database import Database

# Add the get_mongo_handle function here or import it if it's in a separate module
def get_mongo_handle(
    host: str,
    authSource: str,
    username: str,
    password: str,
    db_name: Optional[str] = None,
    authMechanism: str = "SCRAM-SHA-1",
    serverSelectionTimeoutMS: int = 10000,
) -> Union[Database, None]:
    """Gets a MongoDB handle."""
    if db_name is None:
        db_name = authSource
    try:
        client: MongoClient = MongoClient(
            host,
            username=username,
            password=password,
            authSource=authSource,
            authMechanism=authMechanism,
            serverSelectionTimeoutMS=serverSelectionTimeoutMS,
        )
        # test the connection
        client.server_info()
    except errors.ServerSelectionTimeoutError as e:
        print(e)
        return None
    except Exception as e:
        print(e)
        return None

    return client[db_name]

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    # Handle command line arguments
    parser = argparse.ArgumentParser(
        prog="init_mongodb.py", usage="python init_mongodb.py [options] server"
    )
    parser.add_argument("-s", "--server", help="tst/prd")
    options = parser.parse_args()
    if not options.server or options.server not in {"tst", "prd"}:
        parser.print_help()
        sys.exit(1)
    server = options.server

    # Get config info for database connection
    config_obj = load_json("config.json")
    if not isinstance(config_obj, dict):
        print("Invalid config JSON type, expected dict.")
        sys.exit(1)
    mongo_port = config_obj["dbinfo"]["port"][server]
    host = f"mongodb://127.0.0.1:{mongo_port}"
    admin_user = config_obj["dbinfo"]["admin"]["user"]
    admin_pass = config_obj["dbinfo"]["admin"]["password"]
    admin_db = config_obj["dbinfo"]["admin"]["db"]
    db_name = config_obj["dbinfo"]["dbname"]
    db_user = config_obj["dbinfo"][db_name]["user"]
    db_pass = config_obj["dbinfo"][db_name]["password"]

    # Get database handle and create the db user
    dbh = get_mongo_handle(host, admin_db, admin_user, admin_pass, db_name)
    if dbh is None:
        print("Error creating database handle.")
        sys.exit(1)
    dbh.command(
        "createUser", db_user, pwd=db_pass, roles=[{"role": "readWrite", "db": db_name}]
    )

if __name__ == "__main__":
    main()
