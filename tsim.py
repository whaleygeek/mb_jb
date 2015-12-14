# tsim.py  14/12/2015  D.J.Whale

import time
import network

#commands
# tel lv alloc - allocate
#   OK:
#   ERROR:
# tel lv status - send 1 second status reports
#   OK:
#   ERROR:
#   STAT: 7metre 2015-12-10T15:45:43.000Z azel 206.512984 38.990994
# tel lv azel 225.0 45.0
#   OK:
#   ERROR:
# tel lv pos 03:25:42.1 +22:10:10.3

def trace(msg):
    print("tsim:" + str(msg))
    
def incoming(msg):
    trace("incoming:" + str(msg))
    # drop anything not starting with 'tel '
    if len(msg) < 4: return error("Must use tel prefix")
    if msg[:4] != 'tel ': return error("Must use tel prefix")

    # split out parts
    msg = msg[4:]
    parts = msg.split(" ",1)
    cmd = parts[0]
    if len(parts) > 1:
        args = parts[1]
    else:
        args = None

    # decode command and dispatch
    if   cmd == 'alloc':  alloc(args)
    elif cmd == 'status': status(args)
    elif cmd == 'azel':   azel(args)
    elif cmd == 'pos':    pos(args)
    else: error("Unknown command:%s" % cmd)


def error(msg):
    send("ERROR: " + str(msg))

def ok(msg):
    send("OK: " + str(msg))

def send(msg):
    print(msg)
    # send a message back to the client

def alloc(params):
    trace("alloc:" + str(params))
    # simulate allocation
    # send back ok if t name is known

def status(params):
    trace("status:" + str(params))
    # start status reporting on 1 second intervals

def azel(params):
    trace("azel:" + str(params))
    # parse out azimuth and elevation
    # ERROR: if parse error
    # change setpoints
    # send back OK:

def pos(params):
    trace("pos:" + str(params))
    # parse out right ascension and declination in J2000
    # reference frame, positions in sexagesimal.
    # ERROR: if parse error
    # change setpoints
    # OK: if was fine

def run_server():
    trace("run_server")
    # start server listening on port 7045
    # register incoming message listener
    # wait until break

def run_console():
    trace("run_console")
    
    # run on a stdin/stdout console, for testing.
    def csend(msg):
        print(msg)
    global send
    send = csend
    
    while True:
        cmd = raw_input("?> ")
        incoming(cmd)
        
    
if __name__ == "__main__":
    #run_server()
    run_console()

# END

