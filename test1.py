import serial
import time

BAUD     = 115200
PARITY   = serial.PARITY_NONE
DATABITS = serial.EIGHTBITS
STOPBITS = serial.STOPBITS_ONE

MICROBIT1_PORT = '/dev/ttyACM0'
MICROBIT2_PORT = '/dev/ttyACM1'
MICROBIT3_PORT = '/dev/ttyACM2'

print("Opening port 1")
s1 = serial.Serial(MICROBIT1_PORT)
s1.baudrate = BAUD
s1.parity   = PARITY
s1.databits = DATABITS
s1.stopbits = STOPBITS

s1.close()
s1.port = MICROBIT1_PORT
s1.open()

print("port 1 open")

while True:
	ready = s1.inWaiting()
	print(ready)

	if ready > 0:
		print("read")
		msg = s1.read(ready)
		print(msg)
	else:
		time.sleep(1)
