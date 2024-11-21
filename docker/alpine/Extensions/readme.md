# Externalizing Extensions for Docker

Hint: Mounting the folder ./Extensions keeps the external functions 
synchronous to all all ZEO clients and Docker containers.

Hint: if the docker container cannot write to the ./Extensions or ./var folder, 
on a dev system you can simply set the permissions to 777. 
Important:this not recommended for production!

```bash
chmod -R 777 Extensions
chmod -R 777 var
```