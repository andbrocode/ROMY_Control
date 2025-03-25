#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon May 17 15:39:25 2021

changed on 2023-02-20
changed on 2023-03-24
changed on 2023-07-28
changed on 2023-09-21
changed on 2023-10-06
changed on 2023-11-06
changed on 2023-11-10
changed on 2024-02-21
changed on 2024-03-28
changed on 2024-04-08


@author: Andreas Brotzer

"""

## ##### IMPORTS ###############################################

import os
import sys
import csv
import serial
import subprocess

from time import sleep
from pathlib import Path
from datetime import datetime
from numpy import zeros, ones, delete, append, mean, std, nanmean

## ##### VARIABLES #############################################

## working diretory
workdir = "./"

## get beagle number
beagle = os.uname()[1][6:8]

## threshold criteria
threshold_ac = 0.3       # detect if sagnac signal exitst with good quality
threshold_dc = 0.1        # detect if lasing is happening
threshold_ac_std = 0.1    # standard deviation of ac values -> detect multi-mode

## get readings command
cmd_read ="<get SagI>".encode("utf-8")
#cmd_read ="<get ADC1>".encode("utf-8")

## iniciate MLTI command
cmd_mlti = "<MLTI>".encode("utf-8")

## MLTI wait time (in seconds)
mlti_wait_time = 30

## logging
logfile = f"romy_{beagle}_control.log"
mlti_file = f"romy_{beagle}_mlti.log"
logpath = "/SD-Card/Logfiles/"

## data output
outpath = "/SD-Card/"
length_of_data_buffer = 60 # old = 30

## serials
serial1 = "/dev/ttyS1"
serial2 = "/dev/ttyS2"

## mail adress for warning mails
mailadress = "andreas.brotzer@lmu.de"


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
    sys.exit()


## ##### METHODS ################################################

## -------------------------------------------
def __send_mail(subject, body, mailadress):
    body_str_encoded_to_byte = body.encode()
    return_stat = subprocess.run([f"mail", f"-s {subject}", f"{mailadress}"], input=body_str_encoded_to_byte)


## -------------------------------------------
def __write_to_log(directory, filename, msg):

    timestamp = datetime.utcnow().isoformat()

    ## modify file name
    filename = f"{timestamp[:4]}_{filename}"

    if not Path('{}'.format(directory)).exists():
        try:
            os.mkdir(directory)
        except Exception as e:
            print(e)

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
        try:
            os.mkdir(outpath)
        except Exception as e:
            print(e)

    ## check if current year file exists
    year_now = str(datetime.now().year)
    if not os.path.exists(outpath+year_now):
        try:
            os.mkdir(outpath+year_now)
        except Exception as e:
            print(e)

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
def __check_MLTI(last_mlti, xrecovery, mlti_counter):


    #if (std(ac_array) > threshold_ac_std) or (mean(ac_array) < threshold_ac):
    if mean(ac_array) < threshold_ac:

        ## change recovery status and increase count
        xrecovery['mode'] = True
        xrecovery['num'] = xrecovery['num'] + 1

        ## get timestamp as reference criteria
        last_mlti = datetime.utcnow().isoformat()

        ## send command for MLTI
        ser1.write(cmd_mlti)

        print(f"{last_mlti}: MLTI ...")
        #__write_to_log(logpath, logfile, "ACTION: inciated MLTI due to low AC value!")
        __write_to_log(logpath, mlti_file, "MLTI,AC")

        # increase mlti counter
        mlti_counter += 1

    else:
        # toggle recorvery state
        xrecovery['mode'] = False

        # reset mlti counter
        mlti_counter = 0

    return last_mlti, xrecovery, mlti_counter



################ MAIN #############################################

if __name__ == "__main__":

    ## check and setup file structure
    __check_file_structure(outpath)

    ## log start of romy_control.py
    __write_to_log(logpath, logfile, "RESTART: started romy_control.py!")

    ## set array dummies
    #ac_array = ones(50)
    #dc_array = ones(50)
    ac_array = ones(mlti_wait_time)
    dc_array = ones(mlti_wait_time)

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

    ## set a coutner for readout failure
    readout_failure_counter = 0

    ## set a mlti counter
    mlti_counter = 0

    ## create empty data buffer
    data_buffer = []

    ## define start date
    date0 = datetime.utcnow().isoformat().split(".")[0][:10]

    ## flush input
    ser1.flushInput()
    ser2.flushInput()


    while True:


        ## read values from serial port
        readout, timestamp = __readout()
        #print(readout, timestamp)

        ## extract values from readout
        if len(readout) == 6:
            ac = round(float(readout[1]), 2)
            dc = round(float(readout[3]), 2)
            try:
                f0 = round(float(readout[5]), 2)
            except:
                f0 = str(readout[5])
                readout_failure_counter += 1

            if ac == "NAN" or dc == "NAN":
                readout_failure_counter += 1

                ## flush the serial input
                ser1.flushInput()
                ser2.flushInput()

        else:
            __write_to_log(logpath, logfile, "ERROR: readout incomplete!")
            readout_failure_counter += 1

            ## flush the serial input
            ser1.flushInput()
            ser2.flushInput()

        if readout_failure_counter > 20:

            ## write to log file
            __write_to_log(logpath, logfile, "ERROR: stopped due to readout counter!")

            ## send notification mail
            __send_mail(f"ERROR: {beagle} failure count exceeded", f"{timestamp} ERROR: {beagle} - failure count exceeded! Exiting script to force restart!", mailadress)

            ## quit script to force a restart of the script
            # quit()
            sys.exit(1)

        #print(readout_failure_counter, dc, ac, recovery)
        #print()

        ## add values to arrays
        dc_array = delete(dc_array, (0), axis=0)
        dc_array = append(dc_array, dc)

        ac_array = delete(ac_array, (0), axis=0)
        ac_array = append(ac_array, ac)

        ## calculate mean values of arrays
        ac_mean = round(nanmean(ac_array), 3)
        dc_mean = round(nanmean(dc_array), 3)


        ## check Spark criteria and set lasing switch
        if dc_mean < threshold_dc:

            ## check if this is a change in lasing status
            if not lasing_stopped:

                if not recovery['mode']:

                    ## write logfile entry
                    __write_to_log(logpath, logfile, f"WARNING: {beagle} - lasing stopped! DC_mean={dc_mean} < Threshold={threshold_dc}")

                    ## send notification via mail
                    __send_mail(f"WARNING: {beagle} lasing stopped", f"{timestamp}  WARNING: {beagle} - lasing stopped! DC_mean={dc_mean} < Threshold={threshold_dc}", mailadress)

            lasing_stopped = True

        else:

            ## check if this is a change in lasing status
            if lasing_stopped:

                if not recovery['mode']:

                    ## write logfile entry
                    __write_to_log(logpath, logfile, f"INFO: {beagle} - lasing started! DC_mean={dc_mean} > Threshold={threshold_dc}")

                    ## send notification via mail
                    __send_mail("INFO: {beagle} lasing started", f"{timestamp}  INFO: {beagle} - lasing started! DC_mean={dc_mean} > Threshold={threshold_dc}", mailadress)

            lasing_stopped = False


        ## get time difference to last MLTI
        time_delta = (datetime.fromisoformat(timestamp) - datetime.fromisoformat(last_mlti)).total_seconds()


        ## check if MLTI criteria are matched and launch MLTI if true
        if abs(time_delta) > mlti_wait_time and not lasing_stopped:

            # check if MLTI criterion is met and launch MLTI if required
            last_mlti, recovery_new, mlti_counter = __check_MLTI(last_mlti, recovery, mlti_counter)

            if mlti_counter > 20:
                # write to logfile
                __write_to_log(logpath, logfile, f"INFO: {beagle} - exit due to MLTI counter! mlti_counter={mlti_counter}")

                # send notification via mail
                __send_mail(f"ERROR: {beagle} MLTI count exceeded", f"{timestamp} ERROR: {beagle} - MLTI count exceeded! Exiting script to force restart!", mailadress)

                # exit and force restart of script
                sys.exit()

        ## check recovery status
        if abs(recovery_new['mode']-recovery['mode']) == 1:
            if recovery_new['mode']:

                ## write logfile entry
                __write_to_log(logpath, logfile, f"ACTION: recovery started")

                ## send notification via mail
                __send_mail("ACTION: {beagle} - recovery started", f"{timestamp}  ACTION: {beagle} - recovery started", mailadress)


            else:

                ## write logfile entry
                __write_to_log(logpath, logfile, f"ACTION: recovery stopped ({recovery_new['num']} MLTI)")

                ## send notification via mail
                __send_mail("ACTION: {beagle} recovery stopped", f"{timestamp}  ACTION: recovery stopped ({recovery_new['num']} MLTI)", mailadress)

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
