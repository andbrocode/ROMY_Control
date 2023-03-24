#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 15:39:25 2021

changed on 2023-02-20

@author: andbro

"""

## ##### IMPORTS ###############################################

import os
import csv
import serial

from time import sleep
from pathlib import Path
from datetime import datetime
from numpy import zeros, ones, delete, append, mean, std

## ##### VARIABLES #############################################

## working diretory
workdir = "./"

## get beagle number
beagle = os.uname()[1][6:8]

## threshold criteria
threshold_ac = 0.15       # detect if sagnac signal exitst with good quality
threshold_dc = 0.1        # detect if lasing is happening
threshold_ac_std = 0.1    # standard deviation of ac values -> detect multi-mode

## get readings command
cmd_read ="<get SagI>".encode("utf-8")
#cmd_read ="<get ADC1>".encode("utf-8")

## iniciate MLTI command
cmd_mlti = "<MLTI>".encode("utf-8")

## logging
logfile = f"romy_{beagle}_control.log"
mlti_file = f"romy_{beagle}_mlti.log"
logpath = "/SD-Card/Logfiles/"

## data output
outpath = "/SD-Card/"
length_of_data_buffer = 60

## serials
serial1 = "/dev/ttyS1"
serial2 = "/dev/ttyS2"

## ##### SETUP ##################################################

## setup the serial configurations
try:
    ser1 = serial.Serial(serial1)
    ser1.baudrate = 115200
    ser1.timeout = 1
    ser1.write_timeout = 1
    ser1.bytesize = 8
    ser1.parity = "N"
    ser1.stopbits = 1
    exitstatus=0
except:
    print(f"ERROR: Could not setup Serial Connection: {serial1}")
    exitstatus=1

try:
    ser2 = serial.Serial(serial2)
    ser2.baudrate = 115200
    ser2.timeout = 1
    ser2.write_timeout = 1
    ser2.bytesize = 8
    ser2.parity = "N"
    ser2.stopbits = 1
    exitstatus=0
except:
    print(f"ERROR: Could not setup Serial Connection: {serial2}")
    exitstatus=1

if exitstatus == 1:
    exit()


## ##### METHODS ################################################

## -------------------------------------------
def __write_to_log(directory, filename, msg):

    timestamp = datetime.utcnow().isoformat()

    ## modify file name
    filename = f"{timestamp[:4]}_{filename}"

    if not Path('{}'.format(directory)).exists():
        os.mkdir(directory)

    if not Path('{}{}'.format(directory, filename)).exists():
        Path('{}{}'.format(directory, filename)).touch()

    with open('{}{}'.format(directory, filename),'a') as log:
        log.write(timestamp+","+msg+"\n")


## -------------------------------------------
def __check_file_structure(outpath):

    ## compelte path if necessary
    if outpath[-1] != "/":
        outpath += "/"

    ## check if output path exists
    if not os.path.exists(outpath):
        os.mkdir(outpath)

    ## check if current year file exists
    year_now = str(datetime.now().year)
    if not os.path.exists(outpath+year_now):
        os.mkdir(outpath+year_now)


## -------------------------------------------
def __dump_to_file(outpath, data_to_dump):

    outfile = f"romy_{beagle}_{str(data_to_dump[0][0])[:10].replace('-','')}_control.csv"

    ## modify outpath
    if outpath[-1] != "/":
        outpath += "/"
    outpath += str(datetime.now().year) +"/"

    ## check if output file exists, otherwise create
    if not Path('{}{}'.format(outpath, outfile)).exists():
        Path('{}{}'.format(outpath, outfile)).touch()

        ## create and write header to new file
        header = ["datetime","AC", "DC", "F0", "ACmean", "DCmean"]
        with open('{}{}'.format(outpath, outfile), 'a') as out:
            dump = csv.writer(out, delimiter=",")
            dump.writerow(header)

    ## dump data
    with open('{}{}'.format(outpath, outfile), 'a') as out:
        dump = csv.writer(out, delimiter=",")
        for datastring in data_to_dump:
            dump.writerow(datastring)


## -------------------------------------------
def __readout():

    # example readout "<AC: 0.10 DC: 0.34 F: nan>"

    try:
        ser2.write(cmd_read)
        sleep(0.2)
    except:
        __write_to_log(logpath, logfile, "ERROR: send read-command failed!")
        print("ERROR: send read-command failed!")
        return

    ## read serial stream
    serBarCode = ser2.readline(ser2.inWaiting())

    ## create a timestamp at readout
    timestamp = datetime.utcnow().isoformat()

    if len(serBarCode) >= 1:
        #print(serBarCode.decode("utf-8"))
        test = 1
    else:
        __write_to_log(logpath, logfile, "")

    ## decode and reformat the serial readout
    readout = serBarCode.decode("utf-8").split("\r")[0].strip("<>").split(" ")

    return readout, timestamp


## -------------------------------------------
def __check_MLTI(last_mlti, recovery):

#    if (mean(dc_array) < threshold_dc):

        ## get timestamp as reference criteria
#        last_mlti = datetime.utcnow().isoformat()

        ## send command for MLTI
#        ser1.write(cmd_mlti)

#        __write_to_log(logpath, logfile, "ACTION: inciated MLTI due to low DC value!")
#        __write_to_log(logpath, mlti_file, "MLTI,DC")

    if (std(ac_array) > threshold_ac_std) or (mean(ac_array) < threshold_ac):

        ## change recovery status and increase count
        recovery['mode'] = True
        recovery['num'] = recovery_num + 1

        ## get timestamp as reference criteria
        last_mlti = datetime.utcnow().isoformat()

        ## send command for MLTI
        ser1.write(cmd_mlti)

        print(f"{last_mlti}: MLTI ...")
#        __write_to_log(logpath, logfile, "ACTION: inciated MLTI due to low AC value!")
        __write_to_log(logpath, mlti_file, "MLTI,AC")

    else:
        recovery['mode'] = False

    return last_mlti, recovery



################ MAIN #############################################

if __name__ == "__main__":

    ## check and setup file structure
    __check_file_structure(outpath)

    ## log start of romy_control.py
    __write_to_log(logpath, logfile, "RESTART: started romy_control.py!")

    ## set array dummies
    ac_array = ones(50)
    dc_array = ones(50)

    ## set initial last_mlti value
    last_mlti = datetime.utcnow().isoformat()

    ## set initial last_writeout
    last_writeout = datetime.fromisoformat(datetime.utcnow().isoformat("T","seconds"))

    ## switch for lasing
    lasing_stopped = False

    ## recovery status with mlti
    recovery = {}
    recovery['mode'] = False
    recovery['num'] = 0

    ## initialize updatable version of recovery
    recovery_new = recovery

    ## create empty data buffer
    data_buffer = []

    ## define start date
    date0 = datetime.utcnow().isoformat().split(".")[0][:10]

    while True:

        ## read values from serial port
        readout, timestamp = __readout()


        ## extract values from readout
        if len(readout) == 6:
            ac = round(float(readout[1]), 2)
            dc = round(float(readout[3]), 2)
            try:
                f0 = round(float(readout[5]), 2)
            except:
                f0 = str(readout[5])
        else:
            __write_to_log(logpath, logfile, "ERROR: readout incomplete!")

        ## add values to arrays
        dc_array = delete(dc_array, (0), axis=0)
        dc_array = append(dc_array, dc)

        ac_array = delete(ac_array, (0), axis=0)
        ac_array = append(ac_array, ac)

        ## calculate mean values of arrays
        ac_mean = round(mean(ac_array), 3)
        dc_mean = round(mean(dc_array), 3)


        ## check Spark criteria and set lasing switch
        if dc_mean < threshold_dc:
            if not lasing_stopped:
                __write_to_log(logpath, logfile, f"ERROR: lasing stopped! DC_mean={dc_mean} < Threshold={threshold_dc}")
            lasing_stopped = True
        else:
            lasing_stopped = False

        ## get time difference to last MLTI
        time_delta = (datetime.fromisoformat(timestamp) - datetime.fromisoformat(last_mlti)).total_seconds()


        ## check if MLTI criteria are matched and launch MLTI if true
        if abs(time_delta) > 60 and not lasing_stopped:
            last_mlti, recovery_new = __check_MLTI(last_mlti, recovery)


        ## check recovery status
        if recovery_new['mode'] is not recovery['mode']:
             if recovery_new['mode']:
                 __write_to_log(logpath, logfile, f"ACTION: recovery started")
             elif not recovery_new['mode']:
                 __write_to_log(logpath, logfile, f"ACTION: recovery ended ({recovery_new['num']} MLTI)")

                 ## reset recovery count
                 recovery_new['num'] = 0

        ## update recovery status
        recovery = recovery_new


        ## write data buffer to output file when X lines long or date changes (relieves writing operation to SD card)
        if len(data_buffer) == length_of_data_buffer or date0 != timestamp.split(".")[0][:10]:

            ## dump data in buffer to file
            __dump_to_file(outpath, data_buffer)

            ## reset buffer and date0
            data_buffer = []
            date0 = timestamp.split(".")[0][:10]


        ## create datastring and write it to output file every second
        if abs((last_writeout - datetime.fromisoformat(timestamp)).total_seconds()) >= 1:

            ## make and write datastring
            data_buffer.append([timestamp.split(".")[0], ac, dc, f0, ac_mean, dc_mean])

            ## reset last_writeout variable
            last_writeout = datetime.fromisoformat(timestamp.split(".")[0])


## END OF FILE
