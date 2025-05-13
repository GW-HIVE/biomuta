"""Check the collections in the database.

usage: parser.py [-h] server

positional arguments:
  server      prd/beta/tst/dev

options:
  -h, --help  show this help message and exit
"""

import sys
from pymongo import MongoClient

def main():
    
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
        collections = dbh.list_collection_names()
        print("Collections:")
        for collection in collections:
            print(f"- {collection}")
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()