#!/usr/bin/env bash
curl "http://192.168.17.123/current_state.json?pw=admin&Relay4=0" && sleep 1s
curl "http://192.168.17.123/current_state.json?pw=admin&Relay4=1&Relay13=0&Relay14=0&Relay5=0&Relay6=0&"\
"Relay11=0&Relay12=0&Relay7=0&Relay8=0&Relay2=1&Relay15=1"
sleep 50s
python3 CC2/CentralSystem.py &
sleep 10s
./CC2/checkCS.sh
sleep 200s #make sure that the OCL firmware finish installed if any, could be improved by reading info from OCPP
cd CC2
python3 -m http.server 8000 &
