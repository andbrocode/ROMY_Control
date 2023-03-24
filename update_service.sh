#!/bin/bash
#
# update romy_control.service
#

systemctl disable romy_control

cp ./romy_control.service /etc/systemd/system/romy_control.service

systemctl enable romy_control

systemctl daemon-reload

systemctl start romy_control
echo $?

echo "Done"

## End Of File
