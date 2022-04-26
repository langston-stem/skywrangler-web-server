skywrangler-web-server
======================


Development
-----------

### One-time setup

```bash
docker network create skywrangler-web
```

### Running the server

The devcontainer should set up everything. In the devcontainer, just run:

```bash
skywrangler-web-server
```

### Watching mock D-bus server logs

```bash
tail -f /var/log/mock-logind.log
```
