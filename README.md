skywrangler-web-server
======================


Development
-----------

### One-time setup

```bash
docker network create skywrangler-web
```

### Running the PX4 simulator

This is optional and requires <https://github.com/PX4/PX4-Autopilot>.

```bash
# Not in the devcontainer!
cd PX4-Autopilot
HEADLESS=1 make px4_sitl gazebo___baylands
```

### Running the server

The devcontainer should set up everything. In the devcontainer, just run:

```bash
skywrangler-web-server
```

### Watching MAVSDK server logs

```bash
tail -f /var/log/mavsdk-server.log
```

### Watching mock D-bus server logs

```bash
tail -f /var/log/mock-logind.log
```

### Running tests

```bash
pytest-3
```