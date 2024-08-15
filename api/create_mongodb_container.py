import sys
import argparse
import subprocess
import json
def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
def main():
    ### Handle command line arguments
    parser = argparse.ArgumentParser(
        prog="create_mongodb_container.py", usage="python create_mongodb_container.py [options] server"
    )
    parser.add_argument("-s", "--server", help="tst/prd")
    options = parser.parse_args()
    if not options.server or options.server not in {"tst", "prd"}:
        parser.print_help()
        sys.exit(1)
    server = options.server

    ### Get config info for docker container creation
    config_obj = load_json("config.json")
    if not isinstance(config_obj, dict):
        print(
            f"Error reading config JSON, expected type dict and got {type(config_obj)}."
        )
        sys.exit(1)



####
# Project specific variables
    project_name = config_obj['project']
    api_container_name = f"running_{project_name}_api_{server}"
    mongo_container_name = f"running_{project_name}_mongo_{server}"
    mongo_network_name = f"{project_name}_network_{server}"
    mongo_port = config_obj["dbinfo"]["port"][server]
    data_path = config_obj["data_path"]
    username = config_obj["dbinfo"]["admin"]["user"]
    password = config_obj["dbinfo"]["admin"]["password"]
    e_params = ""
    if username and password:
        e_params = f"-e MONGO_INITDB_ROOT_USERNAME={username} -e MONGO_INITDB_ROOT_PASSWORD={password}"

    ### Create and populate command list
    cmd_list = []

    # Check if containers already exist (whether running or in a stopped state)
    for c in {api_container_name, mongo_container_name}:
        cmd = f"docker ps --all | grep {c}"
        container_id = subprocess.getoutput(cmd).split(" ")[0].strip()
        if container_id.strip() != "":
            print(f"Found container: {c}")
            cmd_list.append(f"docker rm -f {container_id}")

    # Check if docker network already exists
    network_cmd = f"docker network ls | grep {mongo_network_name}"
    network_cmd_output = subprocess.getoutput(network_cmd).split()
    if network_cmd_output != []:
        if network_cmd_output[1] == mongo_network_name:
            print(f"Found network: {network_cmd_output[1]}")
            cmd_list.append(f"docker network rm {mongo_network_name} | true")

    # Create docker network command
    cmd_list.append(f"docker network create -d bridge {mongo_network_name}")

    # Create MongoDB container command
    mongo_cmd = f"docker create --name {mongo_container_name} --network {mongo_network_name} -p 127.0.0.1:{mongo_port}:27017"
    mongo_cmd += f" -v {data_path}/api_db/{server}:/data/db {e_params} mongo"
    cmd_list.append(mongo_cmd)

    # Run the commands
    for cmd in cmd_list:
        x = subprocess.getoutput(cmd)
        print(x)

if __name__ == "__main__":
    main()
