#!/usr/bin/env bash
curl "http://192.168.17.123/current_state.json?pw=admin&SetAll=0" && sleep 1s
curl "http://192.168.17.123/current_state.json?pw=admin&SetAll=16394" #set Relay4, 2, 5
sleep 50s
python3 CC2/CentralSystem.py &
sleep 10s
./CC2/checkCS.sh
sleep 200s #make sure that the OCL firmware finish installed if any, could be improved by reading info from OCPP
cd CC2
python3 -m http.server 8000 &
