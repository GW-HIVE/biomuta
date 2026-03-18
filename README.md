# URLs
- frontend tst: https://hivelab.tst.biochemistry.gwu.edu/biomuta
- frontend prd: https://hivelab.biochemistry.gwu.edu/biomuta

# Data Release Pipeline
## JSON documents to be loaded into MongoDB
```
/data/shared/repos/biomuta/json_exports/
```
## Load data
Note to self: implement positional argument that takes the server instead of having to edit the script
```
cd /data/shared/repos/biomuta
senv # alias for source env/bin/activate
# Replace 'tst' or 'prd' with the correct environment if needed in mongo_port = config['dbinfo']['port']['tst']
python json_to_MongodbCollections.py
```
