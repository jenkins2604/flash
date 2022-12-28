#!/usr/bin/env bash
while true
do
    re=$(echo tm fsn|nc -w 20 localhost 8001)
    isJson=$(echo $re | jq -r type)
    if [ $? -ne 0 ]
    then
        echo 'Test station faulty'
        exit 1
    else
        err1=$(echo $re|jq -r '.message.notificationStatus[1].error_code')
        err2=$(echo $re|jq -r '.message.notificationStatus[2].error_code')
        if [[ $err1 != "NoError" ]] && [[ $err2 != "NoError" ]]
            then
                echo "Test station faulty"
                exit 1
        fi
        re=$(echo $re|jq -r '.message.updatestatus')
        echo $re
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
