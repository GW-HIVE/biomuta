## Containerized app modules for HIVE Lab
All application modules that should be integrated to the 
main HIVE Lab website needs to be set up following this example
application module for BioMuta.


## Cloning this example module repositiory
First clone this repo to any direcotry in your server 
```
$ git clone https://github.com/GW-HIVE/biomuta
```

## Getting code for global header and footer
The global header and footer for your module needs to be the 
same as that of the main HIVE Lab website. To do this, you need to also 
clone the repo for the main HIVE Lab website and copy relevant code
to your module code directory following these cmmands.
```
$ git clone https://github.com/GW-HIVE/hivelab
$ cp -r ./hivelab/app/src/components/global/ ./biomuta/app/src/components/
```

## Editing menu for your module 
Ths config JSON file contains menu information for the module. Please
use vi or any editor to edit it.
```
{
  "module":"biomuta",
  "title":"BioMuta - single-nucleotide variations (SNVs) in cancer",
  "menu":[
    {
      "pageid":"home",
      "label":"BioMuta Home",
      "url":"/biomuta/home",
      "children":[],
      "nav":[
         {"pageid":"tools", "url":"/tools", "label":"TOOLS"}
      ]
    },
    {
      "pageid":"readme",
      "label":"BioMuta README",
      "url":"/biomuta/readme",
      "children":[],
      "nav":[
        {"pageid":"tools", "url":"/tools", "label":"TOOLS"},
	{"pageid":"home", "url":"/biomuta/home", "label":"BioMuta Home"}
      ]
    }
  ]
}
```

## Content of static html pages
For each "pageid" in the config JSON file for the menu, you need
to maintain an html files named as page.$PAGE_ID.html.
```
$ ls -ltr biomuta/app/public/html/
	-rw-r--r--. 1 rykahsay developers 502 Apr 10 11:12 biomuta/app/public/html/page.home.html
	-rw-rw-r--. 1 rykahsay developers 839 Apr 10 11:12 biomuta/app/public/html/page.readme.html
```



## Deploying the module application
 Requirements: the following must be available on your server:

* Node.js and npm
* docker


## Setting config parameters
After cloning this repo, you will need to set the paramters given in
app/conf/config.json. The "server" paramater can be "tst" or "prd" for
test or production server respectively. The "app_port" is the port
in the host that should map to docker container for the app.
```
$ cd biomuta/app/conf
$ vi config.json
```

## Creating and starting docker container for the APP

From the "app" subdirectory, run the python script given to build and start container:
  ```
  $ cd biomuta/app/
  $ python3 create_app_container.py -s {DEP}
  $ docker ps --all
  ```
The last command should list docker all containers and you should see the container
you created "running_hivelab_app_{DEP}". To start this container, the best way is
to create a service file (/usr/lib/systemd/system/docker-hivelab-app-{DEP}.service),
and place the following content in it.
  ```
  [Unit]
  Description=Glyds APP Container
  Requires=docker.service
  After=docker.service

  [Service]
  Restart=always
  ExecStart=/usr/bin/docker start -a running_biomuta_app_{DEP}
  ExecStop=/usr/bin/docker stop -t 2 running_biomuta_app_{DEP}

  [Install]
  WantedBy=default.target
  ```
This will allow you to start/stop the container with the following commands, and ensure
that the container will start on server reboot.

  ```
  $ sudo systemctl daemon-reload 
  $ sudo systemctl enable docker-hivelab-app-{DEP}.service
  $ sudo systemctl start docker-hivelab-app-{DEP}.service
  $ sudo systemctl stop docker-hivelab-app-{DEP}.service
  ```


## Mapping APP and API containers to public domains
To map the APP and API containers to public domains (e.g. www.hivelab.org and api.hivelab.org),
add apache VirtualHost directives. This VirtualHost directive can be in a new f
ile (e.g. /etc/httpd/conf.d/hivelab.conf).

  ```
  <VirtualHost *:443>
    ServerName www.hivelab.org

    ProxyPass /biomuta http://127.0.0.1:{APP_PORT}/
    ProxyPassReverse /biomuta http://127.0.0.1:{APP_PORT}/
  </VirtualHost>

  ```

where {APP_PORT} and {API_PORT} are your port for the APP and API ports 
in conf/config.json file. You need to restart apache after this changes using 
the following command:

   ```
   $ sudo apachectl restart 
   ```






