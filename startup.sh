#!/bin/bash

session_name=romy_control
script=romy_control.py
path=/root/romy_control_AB/

## ------------

screen_status=$(screen -S ${session_name} -Q select . ; echo $?)

if [ ! ${screen_status} == 0 ]; then
	screen -S ${session_name} -X quit >/dev/null
	screen -dmS ${session_name} python3 ${path}${script}
else
	echo "session: ${session_name} already running!"
fi

## End of File
