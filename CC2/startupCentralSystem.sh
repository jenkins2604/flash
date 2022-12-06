#!/usr/bin/env bash
curl 'http://192.168.17.123/current_state.json?pw=admin&Relay4=0' && sleep 3s
curl 'http://192.168.17.123/current_state.json?pw=admin&Relay4=1' && sleep 50s
python3 CC2/CentralSystem.py &
sleep 10s
./CC2/checkCS.sh
cd CC2
python3 -m http.server 8000 &
echo Update|nc -w 10 localhost 8001