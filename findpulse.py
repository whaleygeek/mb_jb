# findpulse.py  14/12/2015  D.J.Whale
#
# Listen on a nominated server socket.
# when a connection comes in, open it.
# read data 2 bytes at a time as a U16 (endianness??)
# low time is time below a threshold
# high time is time above a threshold
# show time of each low/high as it is seen.
# close down safely when connection lost, and listen again.

import time
import network

SERVER_PORT = 3001
THRESHOLD = 16384

b1 = None
phase = 0
count = 0

def incoming(msg):
    global b1, phase, count, prev

    for c in msg:
        b = ord(c)

        if b1 == None:
            b1 = b
        else:
            v = b1 + 256 * b # low/high (little-endian)
            # signed integers (note long lead in at +max in sample data)
            if v > 32767:
                v = -(65536 - v) # two's compliment negative data value
            #print(v,b1,b)
            b1 = None
            if phase == 0:
                if v < THRESHOLD:
                    count += 1
                else:
                    print("low for: %d, but now %d" % (count, v))
                    phase = 1
                    count = 1

            elif phase == 1:
                if v >= THRESHOLD:
                    count += 1
                else:
                    print("high for: %d, but now %d" % (count, v))
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
