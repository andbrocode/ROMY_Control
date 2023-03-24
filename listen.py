#!/bin/python

import sys
import serial
from time import sleep

cmd ="<get SagI>".encode("utf-8")


if len(sys.argv) >1:
    testing = False
    print("using port: sys.argv[1]")
else:
    print("testing all tty ports! Otherwise pass: /dev/ttyXX")
    testing = True


def __setup_serial(serial_name):
    ser = serial.Serial(f"/dev/{serial_name}")
    ser.baudrate = 115200
    ser.timeout = 1
    ser.write_timeout = 1
    ser.bytesize = 8
    ser.parity = "N"
    ser.stopbits = 1

    return ser

def __comand(ser):
    try:
        ser.write(cmd)
    except:
        print("Failed to send command!")

    sleep(0.5)
    serBarCode = ser.readline(ser.inWaiting())

    if len(serBarCode) >= 1:
        print(serBarCode.decode("utf-8"))
    else:
        print(f"failed for {ss}!")



while True:

    if testing:
        for ss in range(5):
            print(f"Testing: {ss}")
            
            ser = __setup_serial(f"ttyS{ss}")
            sleep(0.2)
            
            __comand(ser)
            
    else:
        ser = __setup_serial(sys.argv[1])
        
        __comand(ser)
    

## End Of File
