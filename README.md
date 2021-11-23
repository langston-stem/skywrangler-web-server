skywrangler-web-server
======================


Development
-----------

### Running the server

The devcontainer should set up everything. In the devcontainer, just run:

```bash
skywrangler-web-server
```

### Link network to skywranger-web-client devcontainer

This explains how to create a bridge network between the `skywrangler-web-server`
devcontainer and the `skywrangler-web-client` devcontainer. This is needed so
that the proxy used by `yarn start` in the `skywrangler-web-client` devcontainer
will be able to connect to the server running in the `skywrangler-web-server`
devcontainer.

```bash
# see if we have already created network
docker network ls

# if it isn't there
docker network create skywrangler-web

# otherwise see if containers are already connected
docker network inspect skywrangler-web

# to get container names
docker container ls

# add the client
docker network connect skywrangler-web <name>

# add the server
docker network connect --alias skywrangler-web-server skywrangler-web <name>
```

### Watching mock D-bus server logs

```bash
tail -f /var/log/mock-logind.log
```
