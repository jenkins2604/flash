#!/usr/bin/env bash
curl "http://192.168.17.123/current_state.json?pw=admin&SetAll=0" && sleep 1s
curl "http://192.168.17.123/current_state.json?pw=admin&SetAll=16394" #set Relay4, 2, 15
sleep 50s
python3 CC2/CentralSystem.py &
sleep 10s
./CC2/checkCS.sh
sleep 120s #make sure that the OCL firmware finish installed if any, could be improved by reading info from OCPP
