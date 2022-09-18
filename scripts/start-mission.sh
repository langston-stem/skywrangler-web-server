#!/bin/sh

# origin is selected for the baylands in the gazebo simulation

curl http://localhost:8080/api/drone/fly_mission -H "Content-Type: application/json" \
    -d '{
        "origin": {
            "latitude": 37.4137157,
            "longitude": -121.9961280,
            "elevation": -0.5
         },
         "parameters": {
            "speed": 5,
            "distance": 10,
            "angle": 90
         }
    }'
