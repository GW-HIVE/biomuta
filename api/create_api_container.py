import sys
import argparse
import subprocess
import json

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    ### handle command line arguments
    parser = argparse.ArgumentParser(
        prog="create_api_container.py",
        usage="python create_api_container.py [options] server",
    )
    parser.add_argument("-s", "--server", help="tst/prd")
    options = parser.parse_args()
    if not options.server or options.server not in {"tst", "prd"}:
        parser.print_help()
        sys.exit(1)
    server = options.server

    ### get config info for docker container creation
    config_obj = load_json("config.json")
    if not isinstance(config_obj, dict):
        print("Invalid config object type, expected dict.")
        sys.exit(1)
    
    # Customize these lines with project-specific details
    api_image = f"{config_obj['project']}_api_{server}"
    api_container_name = f"running_{api_image}"
    mongo_container_name = f"running_{config_obj['project']}_mongo_{server}"
    api_port = config_obj["api_port"][server]
    db_name = config_obj["dbinfo"]["dbname"]
    data_path = config_obj["data_path"]
    mongo_network_name = f"{config_obj['dbinfo']['bridge_network']}_{server}"
     # Access the admin user and password
    db_user = config_obj["dbinfo"]["admin"]["user"]
    db_pass = config_obj["dbinfo"]["admin"]["password"]
    
    conn_str = f"mongodb://{db_user}:{db_pass}@{mongo_container_name}:27017/?authSource={db_name}"
    ### create and populate command list
    cmd_list = []

    # command to package the API
    # This assumes your project has a setup.py for building a wheel
    # If not needed, remove the following line
    cmd_list.append("python setup.py bdist_wheel")

    # Build Docker image
    cmd_list.append(f"docker build -t {api_image} .")

    # Check if the container exists and remove it
    container_id = (
        subprocess.getoutput(f"docker ps --all | grep {api_container_name}")
        .split(" ")[0]
        .strip()
    )
    if container_id.strip() != "":
        cmd_list.append(f"docker rm -f {container_id}")

    # Create the API Docker container
    cmd = f"docker create --name {api_container_name} --network {mongo_network_name} -p 127.0.0.1:{api_port}:80"
    cmd += f" -v {data_path}:{data_path} -v /software/pipes:/hostpipe -e MONGODB_CONNSTRING={conn_str} -e DB_NAME={db_name}"
    cmd += f" -e DATA_PATH={data_path} -e SERVER={server} {api_image}"
    cmd_list.append(cmd)

    def run_command(cmd):
        result = subprocess.run(
            cmd,
            shell=True,
            universal_newlines=True,  # instead of 'text=True' 
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            print(
                f"Command failed with error code {result.returncode}: {result.stderr}"
            )
        else:
            print(result.stdout)

    # Run the commands
    for cmd in cmd_list:
        run_command(cmd)

if __name__ == "__main__":
    main()
