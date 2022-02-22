skywrangler-web-server
======================


Development
-----------

### Setting up a devcontainer

* In VS Code open the command pallatte and search for "Remote-Containers: Clone repository in container volume..."
* Then select "GitHub".


### Running the server

The devcontainer should set up everything. In the devcontainer, just run:

```bash
skywrangler-web-server
```

### Watching mock D-bus server logs

```bash
tail -f /var/log/mock-logind.log
```
