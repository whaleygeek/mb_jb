# controller.py  13/12/2015  D.J.Whale

import serial
import time


MICROBIT1_PORT = '/dev/ttyACM0'
MICROBIT2_PORT = '/dev/ttyACM1'
MICROBIT3_PORT = '/dev/ttyACM2'

class MicroBit():
  BAUD      = 115200
  PARITY    = serial.PARITY_NONE
  DATABITS  = serial.EIGHTBITS
  STOPBITS  = serial.STOPBITS_ONE
  RXTIMEOUT = None # wait forever
  mytype    = None

  COARSE  = "C"
  FINE    = "F"
  MONITOR = "M"

  @staticmethod
  def decodeType(ty):
    if len(ty) == 0: return None
    ty = ty[0]
    if ty == MicroBit.COARSE: return ty
    if ty == MicroBit.FINE:   return ty
    if ty == MicroBit.MONITOR:return ty
    return None # Not known
  
  def __init__(self, portname):
    self.portname = portname
    self.opened = False

  def open(self):
    s = serial.Serial(self.portname,
                      baudrate=self.BAUD,
                      parity=self.PARITY,
                      bytesize=self.DATABITS,
                      stopbits=self.STOPBITS,
                      timeout=self.RXTIMEOUT)
    self.s = s
    self.opened = True
    return self               

  def sendline(self, line):
    if line == None: return
    if len(line) == 0: line = '\n'
    if line[-1] != '\n': line += '\n'
    self.s.write(line)

  def hasdata(self):
    return self.s.inWaiting() != 0

  def readline(self):
    line = ""
    while True:
      ch = self.s.read(1)
      if ch == '\n': return line
      line += ch

  def close(self):
    self.s.close()
    self.s = None 


# Open connections to 3 micro:bits
m1 = MicroBit(MICROBIT1_PORT)
m2 = MicroBit(MICROBIT2_PORT)
m3 = MicroBit(MICROBIT3_PORT)
microbits = [m1, m2, m3]

opencount = 0
while opencount != 3:
  for m in microbits:
    if not m.opened:
      print("trying to open %s" % m.portname)
      try:
        m.open()
        opencount += 1
      except serial.SerialException:
        print("  could not open")
        time.sleep(0.5)
      print("  opened ok")

# Poll data from each one, to work out what type it is
# as the port numbers might move around on reset

found = 0
while found < 2:
  time.sleep(0.5)
  for m in microbits:
    if m.mytype == None:
      print("check? %s" % m.portname)
      if m.hasdata():
        print("  identity?")
        msg = m.readline()
        print("  rx:%s" % msg)
        ty = MicroBit.decodeType(msg)
        if ty != None:
          print("  found %s" % ty)
          m.mytype = ty
          found += 1

# The 3rd microbit must therefore be the monitor bit (it sends no data)
for m in microbits:
  if m.mytype == None:
    m.mytype = MicroBit.MONITOR
    break

# Dump the detected configuration
for m in microbits:
  print("%s -> %s" % (m.portname, m.mytype))


# END

