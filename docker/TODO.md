# Goals

- [x] one process per container
- [X] Starting the bare docker file will give you a basic zope / zms
- [x] everything as similar to our server deployment as possible to allow easy migration
- [x] modern os and python
- [ ] simple to use and develop in vscode -> .devcontainer!
- [x] all mutable data in mounted volumes
- [ ] example systemd files to run everything
  - [ ] this should show how automated container updates are done!
- [ ] example nginx config so you get the same experience as on the server

# TODOs

- [x] Create basic Dockerfile for the project
- [x] specialize them for zeoserver and zope
- [x] create docker-compose file that runs each server separately
- [ ] add devcontainer.json to develop and run everything from vscode
- [ ] …
