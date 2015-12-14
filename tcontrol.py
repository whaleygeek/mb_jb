# tcontrol.py  14/12/2015  D.J.Whale
#
# controller that talks to the control protocol via a network socket

import time
import network


PORT    = 7045
ADDRESS = "127.0.0.1" # localhost for testing
NAME    = "lv"

az_actual = 0.0
el_actual = 0.0

result = None
reason = None
OK     = 'OK'
ERROR  = 'ERROR'


def trace(msg):
    pass#print(str(msg))

def incoming(msg):
    global az_actual, el_actual, result, reason
    trace("incoming:" + str(msg))

    if len(msg) > 10:
        # STAT: 7metre 2015-12-10T15:45:43.000Z azel 206.512984 38.990994
        # STAT: <name> time azel <az> <el>
        try:
            parts = msg.split(" ")
            if parts[0] == "ERROR:":
                if result == None:
                    result = ERROR
                    reason = msg

            elif parts[0] == 'OK:':
                if result == None:
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


def test_controller():
    global result, reason

    # CONNECT to the t controller
    trace("connecting...")
    network.call(ADDRESS, whenHearCall=incoming, port=PORT)
    trace("connected!")

    # select the correct name
    result = None
    network.say("tel %s alloc" % NAME)
    check_result()

    # start status reports
    result = None
    network.say("tel %s status" % NAME)
    check_result()

    # get a setpoint from user

    az_setpoint = float(raw_input("setpoint az? "))
    el_setpoint = float(raw_input("setpoint el? "))

    # request the setpoint
    az = str(az_setpoint) # apply any formatting
    el = str(el_setpoint) # apply any formatting

    result = None
    network.say("tel %s azel %s %s" % (NAME, az, el))
    check_result()

    # track the setpoint
    # status messages come in via incoming() and update the globals.
    global az_actual, el_actual
    while True:
        time.sleep(1)
        diff_az = az_actual - az_setpoint
        diff_el = el_actual - el_setpoint
        print("Track: s:%f %f  a:%f %f  d:%f %f"
                % (az_setpoint, el_setpoint, az_actual, el_actual, diff_az, diff_el))


if __name__ == "__main__":
    test_controller()


# END


