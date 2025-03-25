#!/bin/bash
#
# send notification via mail if service failed
#
# author = Andreas Brotzer
# year = 2024
## __________________________________________
#
mailadress="andreas.brotzer@lmu.de"
#
datapath="/SD-Card/"
#
workdir="/root/romy_control_AB/"
#
# __________________________________________

host=$(hostname)
beagle_name=${host::8}

sdate=$(date +"%Y%m%d")
stime=$(date +"%H%M%S")

echo "${sdate}, ${stime}, ${beagle_name} romy_control service failed!" | mail -s "Beagle ${beagle_name} - Service Failure" $mailadress

# End of File
