#!/bin/bash
if [ ! -f "ocl_firmware.hex"  ] ||  [ ! -f "ocl_firmware.version" ]
then
	echo "Required files are missing."
  exit 1
fi
#check version of default OCL firmware
defaultVersion=$(sshpass -p root ssh root@192.168.7.2 'cat /usr/share/firmware/ocl_firmware.version')
OclVersion=$(cat ocl_firmware.version)
echo $defaultVersion
#fake version number to force OCL update firmware. FIX ME: CCU always force OCL firmware install with OCL dev firmware version
if [[ $defaultVersion == $OclVersion ]]
  then
    echo 'same firmware version, forcing OCL to update'
    echo $(($OclVersion+1)) > ocl_firmware.version
fi

sshpass -p root scp ocl_firmware.hex root@192.168.7.2:/mnt/data/ocl_firmware.hex
sshpass -p root scp ocl_firmware.version root@192.168.7.2:/mnt/data/ocl_firmware.version
sleep 1s
sshpass -p root ssh -t root@192.168.7.2 << EOF 
  mount | grep -q /usr/share/firmware/ocl_firmware.version || mount -o bind /mnt/data/ocl_firmware.version /usr/share/firmware/ocl_firmware.version
  mount | grep -q /usr/share/firmware/ocl_firmware.hex || mount -o bind /mnt/data/ocl_firmware.hex /usr/share/firmware/ocl_firmware.hex
  systemctl restart sysmgr
EOF

echo loading...

if [[ $defaultVersion == $OclVersion ]]
  then
    sleep 60s #make sure that the OCL firmware finish installed, could be improved by checking data received from OCPP
    echo 'switch version back to normal'
    echo $(($OclVersion)) > ocl_firmware.version
    sshpass -p root scp ocl_firmware.version root@192.168.7.2:/mnt/data/ocl_firmware.version
    sshpass -p root ssh root@192.168.7.2 'mount | grep -q /usr/share/firmware/ocl_firmware.version || mount -o bind /mnt/data/ocl_firmware.version /usr/share/firmware/ocl_firmware.version' 
    sleep 120s
else
  sleep 180s #make sure that the OCL firmware finish installed, could be improved by checking data received from OCPP
fi

#Restart OCL by engage Relay3 (unplug power supply to OCL) and then disengage Relay3 (plug power supply to OCL)  then restart CCU
curl 'http://192.168.17.123/current_state.json?pw=admin&SetAll=16398'
sleep 30s
curl 'http://192.168.17.123/current_state.json?pw=admin&SetAll=16394'
sshpass -p root ssh -t root@192.168.7.2 << EOF 
  systemctl stop ledmgr chargemanager outletmanager rfidcd rfidcd2
  sleep 5s
  systemctl restart sysmgr
EOF
sleep 30s
