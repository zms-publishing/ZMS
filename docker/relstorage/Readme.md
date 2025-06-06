# Running ZMS in a Docker container on RelStorage

Important: *The presented Docker environment is not yet recommended for production, just for testing and exploration.* 

RelStorage stores the ZODB data in a RDBMS: the dockerfile installs - based on Py3.11-slim - Postgres (V15) as the database storing Zope/ZMS data. When Zope is started the first time a schema "zodb" an a postgres-user "zodbuser" is created SQL. The mounted configuration file ./ect/zope.ini tells Zope to store its data via the relstorage-interface

```xml
<zodb_db main>
  mount-point /
  <relstorage>
    <postgresql>
      dsn dbname='zodb' user='zodb' host='localhost' password='zodb'
    </postgresql>
  </relstorage>
</zodb_db>
```

## Configurations for Port-Forwarding

To get a direct access from outsiede the container to Zope (on port 8080) and Postgres (on port 5432) both applications need a modified configuration  files that are mounted from the host filesystem.
The crucial lines here are:

```
#./etc/zope.ini
host = 0.0.0.0

#./etc/postgres/15/main/postgresql.conf
listen_addresses = '*'

#./etc/postgres/15/main/pg_hba.conf
host  all  all  0.0.0.0/0  md5
```
---

_Screen-Image:_ The example environment is Windows 11 with WSSL/Ubuntu and Docker installed. Zope/ZMS are running in a Docker container on exposed port 8080 while Postgress can be reached (due to to upper conf modifications) from the host on 5432, e.g. with HeidiSQL.

![RelStorage-ZODB](../../docs/images/develop_relstorage.png)

## Running OpenSearch in another Docker Container

In the folder ./zms/docker/opensearch a docker-compose.yml file is provided to run OpenSearch with Tika in a separate container-set. The ZMS instance running in the RelStorage container can be connected to this OpenSearch instance by the given the environment variable `ZMS_OPENSEARCH_URL` (http://opensearch-node:9200) in the docker-compose.yml file of the ZMS container.

Important: to share a common network between the two container-sets, docker needs to register a common network. This is done by the command:

```bash
docker network create zms_network
```

The command has to be executed only once. After that, the docker-compose.yml may be used to start the containers. The network name `zms_network` are used in the docker-compose.yml files of both container-sets.

![RelStorage-ZODB](../../docs/images/develop_relstorage_opensearch.png)