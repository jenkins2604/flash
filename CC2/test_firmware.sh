#!/usr/bin/env bash
while true
do
    re=$(echo tm fsn|nc -w 20 localhost 8001)
    echo $re
    isJson=$(echo $re | jq -r type)
    if [ $? -ne 0 ]
    then
        echo Error
        exit 1
    else
        re=$(echo $re|jq -r '.message.updatestatus')
    fi

    if [[ $re == "Installed" ]]
    then
        echo reboot|nc -w 10 localhost 8001
        echo Installed
        exit 0
    elif [[ $re == "NA" ]] || [[ $re == "DownloadFailed" ]] || [[ $re == "InstallationFailed" ]]
    then
        echo Failed
        exit 1
    fi
done