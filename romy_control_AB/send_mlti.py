
#!/bin/python3


import serial

ser = serial.Serial("/dev/ttyS1")
ser.baudrate = 115200
ser.timeout = 0.1
ser.bytesize = 8
ser.parity = "N"
ser.stopbits = 1
ser.write_timeout = 0.1

#cmd = "<get SagI>".encode(encoding="utf-8")
#cmd = "<get ADC0>".encode(encoding="utf-8")
cmd = "<MLTI>".encode(encoding="utf-8")

ser.write(cmd)
