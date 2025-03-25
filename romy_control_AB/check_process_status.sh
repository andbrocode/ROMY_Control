#!/bin/bash
#
# check if a process is still running and communicate error message via mail
#
# author = andbro @2022
#
mailadress="brotzer@geophysik.uni-muenchen.de"
#
datapath="/SD-Card/"

## ___________________________________

process=${1}

host=$(hostname)
beagle_name=${host::8}

sdate=$(date +"%Y%m%d")
stime=$(date +"%H%M%S")

## check status of process: 1=running, 0=not running
status=`ps aux | grep -i "${process}" | grep -v "grep" | wc -l`

## check if process name had been passed
if [ -z "$process" ];then
	echo " -> no process passed!"
	exit
fi

## process status
if [ $status -ge 1 ]
   then
        echo " -> ${process} is running"
   else
        echo " -> ${process} is not running"
	echo "${sdate}, ${stime}, ${process} on ${beagle_name} stopped!" | mail -s "${beagle_name}-ERROR" $mailadress
fi

## check increasing directory
tmpfile=/tmp/check_size.tmp

if [ ! -f $tmpfile ];then
    touch $tmpfile
    du -b ${datapath}$(date +%Y)/ | awk '{ print $1}' > $tmpfile
fi

typeset -i old_size=$(cat $tmpfile)
typeset -i new_size=$(du -b ${datapath}$(date +%Y)/ | awk '{ print $1}')

if [ $old_size -ge $new_size ]; then
    echo  " -> filesize stopped increasing! old: ${old_size} new: ${new_size}!"
    echo  "${sdate}, ${stime}, filesize stopped increasing! old: ${old_size} new: ${new_size}!" | mail -s "${beagle_name}-ERROR" $mailadress
else
    du ${datapath}$(date +%Y)/ | awk '{ print $1}' > $tmpfile
fi


## End of File
