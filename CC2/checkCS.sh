#!/usr/bin/env bash
while true
do
    re=$(echo quit|nc -q 0 localhost 8001)
    if [ $? -ne 0 ]; then exit 2; fi
    err=$(echo $re | cut -c 1-7)
    if [[ $err == "ErrorCS" ]] || [[ $err == "" ]]
    then sleep 20s; continue
    else break
    fi
done
