# netcp.py  14/12/2015  D.J.Whale
#
# send binary data to a network server socket, at a specific rate

import time
import network

FILENAME        = "bytestream.bin"
SEND_SIZE       = 2
SAMPLES_PER_SEC = 8000

SERVER_ADDRESS  = "127.0.0.1"
SERVER_PORT     = 3001


def trace(msg):
    print(str(msg))

def do_send(filename, send_size, samples_per_sec, conn):
    f = open(filename, "rb")
    delaytime_sec = 1.0 / float(samples_per_sec)
    nexttime = time.time()

    while True:
        data = f.read(send_size)
        if len(data) != send_size:
            break # end of stream reached

        # delay to next sample (not very accurate in python!)
        now = time.time()
        while now < nexttime:
            now = time.time()

        conn.say(data) # TODO need a binary mode, BinaryConnection?
        nexttime = now + delaytime_sec

    f.close()


if __name__ == "__main__":
    trace("connecting to server...")

    conn = network.BinaryConnection()
    conn.call(SERVER_ADDRESS, port=SERVER_PORT)
    trace("sending data...")
    do_send(FILENAME, SEND_SIZE, SAMPLES_PER_SEC, conn)
    trace("disconnecting...")
    conn.hangUp()
    trace("done!")

# END
