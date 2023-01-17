#!/usr/bin/env bash
curl "http://192.168.17.123/current_state.json?pw=admin&Relay4=0" && sleep 3s
curl "http://192.168.17.123/current_state.json?pw=admin&Relay4=1&Relay13=0&Relay14=0&Relay5=0&Relay6=0&"\
"Relay11=0&Relay12=0&Relay7=0&Relay8=0&Relay2=1&Relay15=1"
sleep 5s
curl "http://192.168.17.123/current_state.json?pw=admin&Relay2=0&Relay15=0"
sleep 50s
python3 CC2/CentralSystem.py &
sleep 10s
./CC2/checkCS.sh
cd CC2
python3 -m http.server 8000 &
