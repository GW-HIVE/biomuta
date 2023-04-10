import os,sys
import string
from optparse import OptionParser
import glob
import json
import subprocess

__version__="1.0"
__status__ = "Dev"



###############################
def main():

    
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog version___")
    parser.add_option("-s","--server",action="store",dest="server",help="dev/tst/beta/prd")
    (options,args) = parser.parse_args()

    for key in ([options.server]):
        if not (key):
            parser.print_help()
            sys.exit(0)

    server = options.server


    config_obj = json.loads(open("./conf/config.json", "r").read())

    image = "biomuta_app_%s" % (server) 
    container = "running_" + image
    app_port = config_obj["app_port"][server]
    data_path = config_obj["data_path"]
   
    with open(".env.production", "w") as FW:
        app_root_url = "https://hivelab.biochemistry.gwu.edu/biomuta/"
        if server == "tst":
            app_root_url = "https://hivelab.tst.biochemistry.gwu.edu/biomuta/"
        FW.write("REACT_APP_SERVER=%s\n" % (server))
        FW.write("REACT_APP_ROOT_URL=%s\n" % (app_root_url))
        FW.write("REACT_APP_APP_VERSION=1.1\n")


    cmd_list = []
    if os.path.isdir(data_path) == False:
        cmd_list.append("mkdir -p %s" % (data_path))


    cmd = "npm run build"
    cmd_list.append(cmd)
    cmd = "docker build -t %s ." % (image)
    cmd_list.append(cmd)

    for c in [container]:
        cmd = "docker ps --all |grep %s" % (c)
        container_id = subprocess.getoutput(cmd).split(" ")[0].strip()
        if container_id.strip() != "":
            cmd_list.append("docker rm -f %s " % (container_id))

    cmd = "docker create --name %s -p 127.0.0.1:%s:80 -v %s:%s %s" % (container,app_port,data_path, data_path, image)
    cmd_list.append(cmd)

    for cmd in cmd_list:
        #print (cmd)
        x = subprocess.getoutput(cmd)
        print (x)
    




if __name__ == '__main__':
    main()
