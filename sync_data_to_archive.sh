#!/bin/bash
#
# rsync data of romy_control.py to romy_archive
#
# ----------------

YEAR=$(date +%Y)

RING="RZ"

LOGFILE="/SD-Card/Logfiles/romy_data_sync.log"

MAILADRESS="brotzer@geophysik.uni-muenchen.de"

# ---------------

## touch logfile if not existing
if [ ! -f $LOGFILE ];then
    touch $LOGFILE
fi

## sync data
/usr/bin/rsync -urlt /SD-Card/${YEAR}/*.csv sysop@taupo.geophysik.uni-muenchen.de:/freenas-ffb-01/romy_archive/${YEAR}/BW/CROMY/${RING}/ >/dev/null 2>&1

## check if sync was success
if [ $? -eq 0 ]; then
   echo "synchronized successfully!"
else
   echo "ERROR: synchronization @ ${RING} failed!" | mail -s "ERROR: Sync Data ROMY Control ${RING}" $MAILADRESS

   UTC=$(date -u '+%Y-%m-%dT%H:%M:%S.000000')
   echo "$UTC,ERROR: synchronization failed!" >> $LOGFILE
fi


## sync logfile
/usr/bin/rsync -urlt ${LOGFILE} sysop@taupo.geophysik.uni-muenchen.de:/freenas-ffb-01/romy_archive/${YEAR}/BW/CROMY/ >/dev/null 2>&1
#/usr/bin/rsync -urlt /SD-Card/Logfiles/${YEAR}*.log sysop@taupo.geophysik.uni-muenchen.de:/freenas-ffb-01/romy_archive/${YEAR}/BW/CROMY/ >/dev/null 2>&1

## END OF FILE
