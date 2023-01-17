#!/bin/bash

sshpass -p root ssh -t root@192.168.7.2 << EOF 
  cat /etc/version
  mount | grep -q /usr/share/firmware/ocl_firmware.version || mount -o bind /mnt/data/ocl_firmware.version /usr/share/firmware/ocl_firmware.version
  sleep 3s
  mount | grep -q /usr/share/firmware/ocl_firmware.hex || mount -o bind /mnt/data/ocl_firmware.hex /usr/share/firmware/ocl_firmware.hex
  sleep 3s
  systemctl restart sysmgr
EOF
