#!/bin/bash

sshpass -p root ssh -t root@192.168.7.2 << EOF 
  cat /etc/version
  mount | grep -q /usr/share/firmware/ocl_firmware.version || mount -o bind /mnt/data/ocl_firmware.version /usr/share/firmware/ocl_firmware.version
  mount | grep -q /usr/share/firmware/ocl_firmware.hex || mount -o bind /mnt/data/ocl_firmware.hex /usr/share/firmware/ocl_firmware.hex
  systemctl restart sysmgr
  sleep 220s
EOF

#Restart OCL by engage Relay3 (unplug power supply to OCL) and then disengage Relay3 (plug power supply to OCL)  then restart CCU
sshpass -p root ssh -t root@192.168.7.2 << EOF 
  curl 'http://192.168.17.123/current_state.json?pw=admin&Relay3=1'
  sleep 60s
  curl 'http://192.168.17.123/current_state.json?pw=admin&Relay3=0'
  systemctl stop ledmgr chargemanager outletmanager rfidcd rfidcd2
  systemctl restart sysmgr
EOF
