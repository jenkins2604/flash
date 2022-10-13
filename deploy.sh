#!/bin/sh

echo "deploying..."

# bundle, minify, and package css and js - optional
# gulp build

# using SSH vs SFTP because SSH offers us rm -rf *
# which deletes directories even if they are empty
# we don't have to traverse the directory and delete files manually
# <<EOF tells shell to give the following lines to the sftp terminal
sshpass -p "root" ssh root@192.168.7.2 <<EOF
cd /mnt/data/etc
if test -f "test.txt";
then
    echo "test has found."
    rm test.txt
else
    echo "clear for build"
fi
exit
EOF

# upload files from build to the remote file build
# sshpass -p "root" scp test.txt root@192.168.7.2:/mnt/data/etc

echo "deploy finished"

