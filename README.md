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
python misc_scripts/json_to_MongodbCollections.py
```

# Troubleshooting
## How to check what's inside a collection (can also use `peak_collection.py`)
Connect to MongoDB via the Docker container
```
# tst
docker exec -it running_biomuta_mongo_tst mongosh
# prd
docker exec -it running_biomuta_mongo_prd mongosh
```
Once inside the docker:
```
use admin
db.auth("your_admin_user", "your_admin_password")
use your_db_name
db.<collection_name>.findOne() # e.g. db.C_biomuta_mutation.findOne()
```
## How to check if the app container is running
```
docker ps -a
```
Look for the BioMuta app container (not the mongo one). Check its status and how long ago it was running.
## How to check app container logs
```
docker logs <biomuta_app_container> --tail 100
```
## How to check if the app is listening on its expected port
```
ss -tlnp | grep <expected_port>
# or
netstat -tlnp | grep <expected_port>
```
## How to check system resources
Sometimes containers go down due to OOM (out of memory).
```
free -h
df -h
```
## How to check the proxy config to confirm what port it's forwarding to
```
cat /etc/apache2/sites-enabled/*.conf
# or for nginx
cat /etc/nginx/sites-enabled/*
```

# FAQ
## Indexing
### Why is indexing needed?
If you see that every single query in the MongoDB log shows `"planSummary":"COLLSCAN"`, it means MongoDB is scanning the entire collection (millions of documents) for every lookup by id. With queries scanning up to 3.28 million documents each taking 1-2 seconds, a single page load that triggers many such queries easily exceeds Apache/Nginx's proxy timeout, which returns the 502. The collection has no index on the `id` field, so as the collection grew over time, queries got progressively slower until they started timing out.
### How to index
The fix is to add an index inside the Docker container:
```
docker exec -it running_biomuta_mongo_prd mongosh
# Once inside the docker
use biomuta_db
db.auth("your_db_user", "your_db_password")
db.C_biomuta_mutation.createIndex({ id: 1 })
```
This will take a few minutes to build on a large collection, but once done, those queries that take 500-1700ms will drop to under 1ms. You should also check if other collections have the same problem:
```
db.C_biomuta_protein.createIndex({ id: 1 })
db.C_biomuta_cancer.createIndex({ id: 1 })
// etc. for all collections queried by id
```
Indexing is taken care of by the `load_data.py` script which creates indexes after loading — see this after `insert_many`:
```
collection.create_index("id")
```
