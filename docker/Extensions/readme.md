# Externalizing Extensions for Docker

Hint: if the docker container cannot write to the ./Extensions or ./var folder, 
you can simply set the permissions to 777. (Important: not recommended for production!)

```bash
chmod -R 777 Extensions
chmod -R 777 var
```