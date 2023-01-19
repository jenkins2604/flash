#!/usr/bin/env bash
#loop until firmware installation is either finished or failed
echo Update|nc -w 10 localhost 8001
while true
do
    re=$(echo tm fsn|nc -w 20 localhost 8001)
    if [ $? -ne 0 ]
    then
        echo 'Test station faulty'
        exit 1
    fi
    re=$(echo $re|jq -r '.message.updateStatus')
    echo $re
    if [[ $re == "Downloading" ]] || [[ $re == "Installing" ]] 
    then
        continue
    elif [[ $re == "Installed" ]]
    then
        echo reboot|nc -w 10 localhost 8001
        echo Installed
        exit 0
    else
        echo 'update failed'
        exit 1
    fi
done
