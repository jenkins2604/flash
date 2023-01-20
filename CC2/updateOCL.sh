#!/bin/bash
sshpass -p root scp ocl_firmware.hex root@192.168.7.2:/mnt/data/ocl_firmware.hex
sshpass -p root scp ocl_firmware.version root@192.168.7.2:/mnt/data/ocl_firmware.version
sleep 1s
sshpass -p root ssh -t root@192.168.7.2 << EOF 
  mount | grep -q /usr/share/firmware/ocl_firmware.version || mount -o bind /mnt/data/ocl_firmware.version /usr/share/firmware/ocl_firmware.version
  mount | grep -q /usr/share/firmware/ocl_firmware.hex || mount -o bind /mnt/data/ocl_firmware.hex /usr/share/firmware/ocl_firmware.hex
  systemctl restart sysmgr
EOF
echo loading...
sleep 200s #make sure that the OCL firmware finish installed, could be improved by checking data received from OCPP
#Restart OCL by engage Relay3 (unplug power supply to OCL) and then disengage Relay3 (plug power supply to OCL)  then restart CCU
curl 'http://192.168.17.123/current_state.json?pw=admin&Relay3=1'
sleep 200s
curl 'http://192.168.17.123/current_state.json?pw=admin&Relay3=0'
sshpass -p root ssh -t root@192.168.7.2 << EOF 
  systemctl stop ledmgr chargemanager outletmanager rfidcd rfidcd2
  systemctl restart sysmgr
EOF
sleep 30s
