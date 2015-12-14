# tsim.py  14/12/2015  D.J.Whale
# Python 2

import time
import thread
import network

NAMES = [
    "lv",
    "mk2",
    "da",
    "pi",
    "kn",
    "de",
    "cm",
    "42ft",      
    "7m"
]

selected_name = None
status_enabled = False

# degrees
az_setpoint   = 0.0   # 0..359
el_setpoint   = 0.0   # 0..90? 180?
az_actual     = 225.0 # 0..359
el_actual     = 45.0  # 0..90? 180?

# J2000 reference frame in sexagesimal
#ra_setpoint   = None
#dec_setpoint  = None
#ra_actual     = None
#dec_setpoint  = None

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
#   OK:
#   ERROR:

def trace(msg):
    print(str(msg))
    
def incoming(msg):
    trace("incoming:" + str(msg))
    # drop anything not starting with 'tel '
    if len(msg) < 4: return error("Must use tel prefix")
    if msg[:4] != 'tel ': return error("Must use tel prefix")

    # split out parts (tel name cmd params)
    try:
        tel, name, cmdargs = msg.split(" ",2)
    except Exception as e:
        print(e)
        return error("Unparseable command line:%s" % msg)
    
    if not name in NAMES: return error("Unknown name:%s" % name)

    parts = cmdargs.split(" ", 1)
    cmd = parts[0]
    if len(parts) > 1:
        args = parts[1]
    else:
        args = None

    # decode command and dispatch
    if   cmd == 'alloc':  alloc(name)
    elif cmd == 'status': status(name)
    elif cmd == 'azel':   azel(name, args)
    elif cmd == 'pos':    pos(name, args)
    else: error("Unknown command:%s" % cmd)


def error(msg):
    send("ERROR: " + str(msg))

def ok(msg=""):
    send("OK: " + str(msg))

def send(msg):
    print(msg)
    #TODO: send a message back to the client over network connection

def alloc(name):
    #trace("alloc:" + str(params))
    if name == None: return error("Must provide a name")
    if name in NAMES:
        global selected_name
        selected_name = name
    else:
        return error("Unknown name:%s" % name)
    ok("allocated %s" % name)
    
def status(name):
    #trace("status:")
    if selected_name == None: return error("Nothing allocated")
    start_status_reports()
    ok("status reports enabled")

def azel(name, params):
    trace("azel:" + str(params))
    try:
        az, el = params.split(" ", 1)
        az = float(az)
        el = float(el)
    except:
        return error("Invalid az/el:%s" % params)

    global az_setpoint, el_setpoint
    az_setpoint = az
    el_setpoint = el
    ok("Setpoints changed to az: %f el: %f" % (az, el)) 

def pos(name, params):
    trace("pos:" + str(params))
    # parse out right ascension and declination in J2000
    # reference frame, positions in sexagesimal.
    # ERROR: if parse error
    # change setpoints
    # OK: if was fine

def send_status(msg):
    send("STAT: " + str(msg))

def move(amount):
    global az_actual, el_actual
    # move the item by a defined step, towards setpoints
    # at the moment only supports azel mode
    # move az cyclically
    # el has top and bottom endstops

    # beware of end stops
    # if az_actual < az_setpoint
    # elif az_actual > az_setpoint

    # beware of endstops
    # if el_actual < el_setpoint
    # elif el_actual > el_setpoint
    pass

def tick():
    #trace("tick")
    if status_enabled and selected_name != None:
        timenow = "2015-12-14T00:00:00.000Z" # dummy
        az = str(az_actual) # TODO:formatting
        el = str(el_actual) # TODO:formatting
        send_status("%s %s %s %s %s" % (selected_name, timenow, "azel", az, el))
    move(1) # fast move increment for testing

def run_server():
    trace("run_server")
    # start server listening on port 7045
    # register incoming message listener
    # wait until break
    
def start_ticker():
    def body():
        while True:
            time.sleep(1)
            tick()
    thread.start_new_thread(body, ())
    
def start_status_reports():
    global status_enabled
    status_enabled = True

def run_console():
    trace("run_console")
    
    # run on a stdin/stdout console, for testing.
    def csend(msg):
        print(msg)
    global send
    send = csend

    start_ticker()
    
    while True:
        cmd = raw_input("?> ")
        incoming(cmd)
        
    
if __name__ == "__main__":
    #run_server()
    run_console()

# END

