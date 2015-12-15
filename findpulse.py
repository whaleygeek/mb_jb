# findpulse.py  14/12/2015  D.J.Whale
#
# Listen on a nominated server socket.
# when a connection comes in, open it.
# read data 2 bytes at a time as a U16 (endianness??)
# low time is time below a threshold
# high time is time above a threshold
# show time of each low/high as it is seen.
# close down safely when connection lost, and listen again.

# Python 2

# To test
# in first console window:    python findpulse.py > out
# in second console window:   nc localhost 3001 < bytestream.bin
# Edit the THRESHOLD below to change the switching point.

import time
import network
import struct
from math import sqrt

SERVER_PORT = 3001
THRESHOLD = 16384

b1 = None
phase = 0
count = 0
mean= 0
nsample = 0
m2 = 0


def incoming(msg):
    global b1, phase, count, prev, nsample, mean, m2
    nval = len(msg)/2
    vals = struct.unpack(str(nval)+'h',msg)
    for v in vals:
        nsample += 1
        delta = v - mean
        mean += delta/nsample
        m2 += delta*(v-mean)
        THRESHOLD = mean+ sqrt(m2/(nsample))
        if phase == 0:
            if v < THRESHOLD:
                count += 1
            else:
                print("low for: %d, but now %d threshold %d sample %d" % (count, v, THRESHOLD, nsample))
                phase = 1
                count = 1

        elif phase == 1:
            if v >= THRESHOLD:
                count += 1
            else:
                print("high for: %d, but now %d threshold %d sample %d" % (count, v, THRESHOLD, nsample))
                phase = 0
                count = 1

conn = None
def run_listener():
    global conn
    try:
        conn = network.BinaryConnection()
        while True:
            print("waiting for connection...")
            conn.wait(whenHearCall=incoming, port=SERVER_PORT)
            print("connected!")

            while conn.isConnected():
                time.sleep(1)

            print("connection lost!")
    finally:
        conn.hangUp()


if __name__ == "__main__":
    run_listener()

# END
