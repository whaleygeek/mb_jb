# tcontrol.py  14/12/2015  D.J.Whale
#
# controller that talks to the control protocol via a network socket

import time
import network
import serial

# strong pulsar with period of about 0.36 seconds
RA_DEC = "19:35:47.8259  +16:16:39.986"

AZ_MICROBIT = "/dev/ttyACM0"
EL_MICROBIT = "/dev/ttyACM1"

PORT    = 7045
ADDRESS = "127.0.0.1" # localhost for testing
ADDRESS = "x.x.x.x" # control PC
#NAME    = "7metre" # for testing
NAME = "Lovell"

az_microbit = None
el_microbit = None

az_actual = 0.0
el_actual = 0.0

new_stat = False
result = None
reason = None
OK     = 'OK'
ERROR  = 'ERROR'


def trace(msg):
    print(str(msg))

def incoming(msg):
    global az_actual, el_actual, result, reason, new_stat
    trace("incoming:" + str(msg))

    if len(msg) > 1:
        # STAT: 7metre 2015-12-10T15:45:43.000Z azel 206.512984 38.990994
        # STAT: <name> time azel <az> <el>
        try:
            parts = msg.split(" ")
            if parts[0] == "ERROR:":
                trace("found error")
                if result == None:
                    trace("signalled error")
                    result = ERROR
                    reason = msg

            elif parts[0] == 'OK:':
                trace("found ok")
                if result == None:
                    trace("signalled ok")
                    result = OK
                    reason = msg

            elif parts[0] == "STAT:":
                if parts[1] != NAME:
                    trace("not correct name?")
                else:
                    t = parts[2]
                    if parts[3] != "azel":
                        trace("not an azel message?")
                    else:
                        az = parts[4]
                        el = parts[5]
                        az = float(az)
                        el = float(el)
                        trace("az: %f el: %f" % (az, el))
                        az_actual = az
                        el_actual = el
                        new_stat = True

        except Exception as e:
            trace("Can't parse:%s because of %s" % (msg, e))

def check_result():
    # blocking wait for an OK or ERROR in result
    trace("waiting for result")
    while True:
        if result == None:
            time.sleep(0.1)
        else:
            if result == OK:
                trace("OK result:%s" % reason)
                return True
            trace("ERROR result:%s" % reason)
            return False


def send(msg):
    global result, reason
    result = None
    reason = None
    trace("sending:" + str(msg))
    network.say(msg)


def start_test_controller():

    # CONNECT to the t controller
    trace("connecting...")
    network.call(ADDRESS, whenHearCall=incoming, port=PORT)
    trace("connected!")

    try:
        run_test_controller()
    finally:
        try:
            trace("deallocating...")
            send("tel %s dealloc" % NAME)
            time.sleep(2)
            trace("closing...")
            network.hangUp()
        except Exception as e:
            print("Failed to dealloc: %s" % e)


def run_test_controller():
    # select the correct name
    send("tel %s alloc" % NAME)
    check_result()

    # get a setpoint from user

    az_setpoint = float(raw_input("setpoint az? "))
    el_setpoint = float(raw_input("setpoint el? "))

    # request the setpoint
    az = str(az_setpoint) # apply any formatting
    el = str(el_setpoint) # apply any formatting

    send("tel %s azel %s %s" % (NAME, az, el))
    check_result()

    # track the setpoint
    # status messages come in via incoming() and update the globals.
    global az_actual, el_actual
    while True:
        send("tel %s status" % NAME)
        time.sleep(1)
        diff_az = az_actual - az_setpoint
        diff_el = el_actual - el_setpoint
        print("Track: s:%f %f  a:%f %f  d:%f %f"
                % (az_setpoint, el_setpoint, az_actual, el_actual, diff_az, diff_el))



def start_mb_controller():
    global result, reason, az_microbit, el_microbit

    # connect two micro:bits
    trace("Connecting to AZ microbit...")
    az_microbit = serial.Serial(port=AZ_MICROBIT, baudrate=115200)

    trace("Connecting to EL microbit...")
    el_microbit = serial.Serial(port=EL_MICROBIT, baudrate=115200)

    # CONNECT to the t controller
    trace("connecting to telescope control...")
    network.call(ADDRESS, whenHearCall=incoming, port=PORT)
    trace("connected!")

    try:
        run_mb_controller()
    finally:
        try:
            trace("deallocating...")
            send("tel %s dealloc" % NAME)
            time.sleep(2)
            trace("closing...")
            network.hangUp()
        except Exception as e:
            print("Failed to dealloc: %s" % e)


def hasdata(s):
    return s.inWaiting() != 0


def readline(s):
    line = ""
    while True:
      ch = s.read(1)
      if ch == '\n': return line
      line += ch


STAT_POLL_RATE_SEC = 1

def run_mb_controller():
    global az_actual, el_actual, new_stat

    az_setpoint = None
    el_setpoint = None

    # select the correct name
    send("tel %s alloc" % NAME)
    check_result()

    next_stat_time = time.time() + STAT_POLL_RATE_SEC

    while True:
        # process any data from AZ micro:bit
        if hasdata(az_microbit):
            az_msg = readline(az_microbit).strip()
            trace("AZ data:%s" % az_msg)
            # decode message Aaz,A,B
            if len(az_msg) < 6:
                print("Malformed AZ message:%s" % az_msg)
            else:
                ty = az_msg[0]
                if ty != 'A':
                    print("Not an AZ message:%s" % az_msg)
                else:
                    parts = (az_msg[1:]).split(",")
                    if len(parts) < 3:
                         print("AZ message had missing fields:%s" % az_msg)
                    else:
                        try:
                            az = float(parts[0])
                        except:
                            print("Failed to decode AZ:%s" % az_msg)
                            az = None
                        #print(parts)
                        A = parts[1]
                        if A == '0':
                            button_a = False
                        else:
                            button_a = True

                        B = parts[2]
                        if B == '0':
                            button_b = False
                        else:
                            button_b = True
                        #button_a = False
                        #button_b = False

                        if az < 0.0: az = 0
                        if az > 360.0: az = 360.0
                        az_setpoint = az

                        if button_a: # send az/el
                            send("tel %s azel %f %f" % (NAME, az_setpoint, el_setpoint))
                            check_result()

                        if button_b: # send RA/DEC
                            send("tel %s pos %s" % (NAME, RA_DEC))
                            check_result()


        # process any data from EL micro:bit
        if hasdata(el_microbit):
            el_msg = readline(el_microbit)
            trace("EL data:%s" % el_msg)
            # decode message Eel
            if len(el_msg) < 2:
                print("EL message too short:%s" % el_msg)
            else:
                ty = el_msg[0]
                if ty != 'E':
                    print("not an EL message:%s" % el_msg)
                else:
                    el = el_msg[1:]
                    try:
                        el = float(el)
                    except:
                        print("Not a valid el number:%s" % el_msg)
                        el = None

                    el_setpoint = el

        # Request a new STAT if it is time to do so
        now = time.time()
        if now > next_stat_time:
            send("tel %s status" % NAME)
            next_stat_time = now + STAT_POLL_RATE_SEC

        # If a new stat came in, show any values we have
        if new_stat:
            new_stat = False
            if az_setpoint == None or el_setpoint == None:
                diff_az = "?"
                diff_el = "?"
            else:
                diff_az = str(az_setpoint - az_actual)
                diff_el = str(el_setpoint - el_actual)

            az = str(az_setpoint)
            el = str(el_setpoint)
            print("s: %s %s  a:%f %f  d:%s %s" % (az, el, az_actual, el_actual, diff_az, diff_el))



if __name__ == "__main__":
    #start_test_controller()
    start_mb_controller()


# END


