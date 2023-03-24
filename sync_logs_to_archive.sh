#!/bin/bash
#
# rsync data of romy_control.py to romy_archive
#
## ________________________________________

YEAR=$(date +%Y)

RING="RZ"
BEAGLE="01"

SIZEFILE1="/tmp/sizefile1.txt"
SIZEFILE2="/tmp/sizefile2.txt"

LOGFILE1="/SD-Card/Logfiles/${YEAR}_romy_${BEAGLE}_control.log"
LOGFILE2="/SD-Card/Logfiles/${YEAR}_romy_${BEAGLE}_mlti.log"

MAILADRESS="brotzer@geophysik.uni-muenchen.de"


function run {

	## ________________________________________
	## touch logfile if not existing
	if [ ! -f $2 ];then
	    touch $2
	    echo 0 >> $2
	fi

	## ________________________________________
	## sync logs if file size increased

	old_size=$(cat $2 | wc -c)
	new_size=$(cat $1 | wc -c)


	if [[ $old_size != $new_size ]];then

	    ## update sizefile
	    cp $1 $2

	    ## synchronize log file to archive
	    /usr/bin/rsync -urlt $1 sysop@taupo.geophysik.uni-muenchen.de:/freenas-ffb-01/romy_archive/${YEAR}/BW/CROMY/ >/dev/null 2>&1

	    ## check if sync was success
	    if [ $? -eq 0 ]; then
	       echo "synchronized $1 successfully!"
	    else
	       echo "ERROR: synchronization of logs @ ${RING} failed!" | mail -s "ERROR: Sync Logs ROMY Control ${RING}" $MAILADRESS
	    fi

	else
	    echo "no change in size!"
	fi
}


run $LOGFILE1 $SIZEFILE1

run $LOGFILE2 $SIZEFILE2


## END OF FILE
