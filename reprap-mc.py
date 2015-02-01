 #!/bin/python
import serial, sys, time

config = {
  'serial' : {
    'port' : {
      'printer' : "/dev/ttyACM0",
      'arduino' : "/dev/ttyACM1"
    },
    'speed' : 115200,
    'timeout' : 2, # seconds
    'eol' : "\n\r"
  },
  'printer' : {
    'command_delay': 0.02, # seconds
    'general_gcode': 'G91',
    'extrusion': {
      'step' : 0.20
    },
    'travel' : {
      'step' : 2.10
    },
    'plate' : {
      'step' : 0.05
    }
  },
  'analog' : {
    'zero' : 1024 / 2,
    'tolerance' : 30
  }
}


class RepRapMCPrinterController:

  def __init__(self):
    
    self.ser_printer = None
    self.ser_arduino = None

  def sendGCode(self, gcode):

    self.ser_printer.write(gcode + config.serial.eol)

    # Flush
    self.ser_printer.flushOutput()

  def bootstrap(self):

    print "Sending startup gcodes"

    # Homes
    self.sendGCode('G28')

    # Set units to millimeters
    self.sendGCode('G21')

    # Use relative coordinates for traveling
    self.sendGCode('G91')

    # Use relative displacement for extrusion
    self.sendGCode('G92 E0')

    # Heats the head
    self.sendGCode('M104 S200')

    # Heats the plate
    self.sendGCode('M140 S60')

    # Boosts speed by 200%
    self.sendGCode('M220 S200')

    # Lower Z-plate
    self.sendGCode('G1 Z' + config.printer.plate.step + ' F2400')


    # Absolute positionning for these guys
    self.z = 0.2
    self.extrusion = 0

  def connect(self):

    print "Connecting serial ports"

    # Open the ports
    self.ser_printer = serial.Serial(port=config.serial.port.printer, baudrate=config.serial.speed, timeout=config.serial.timeout)
    self.ser_arduino = serial.Serial(port=config.serial.port.arduino, baudrate=config.serial.speed, timeout=config.serial.timeout)

    # Wait for ports to initialize
    time.sleep(2)

    # Flush
    self.flushAll()

  def flushAll(self):

    self.ser_printer.flushOutput()
    self.ser_printer.flushInput()
    self.ser_arduino.flushInput()

  def movePlateTo(self, absolute_z):

    self.sendGCode(config.printer.general_gcode + ' Z' + str(absolute_z) + ' F2400')

  def start(self):

    print "Starting process ..."

    # Let's compute this here first
    lower_bound = config.analog.zero + tolerance
    upper_bound = config.analog.zero - tolerance

    while True:

      self.flushAll()

      command_available = False
      command = self.ser_arduino.readline().split(",")

      # A correct command line contains 4 items : x, y, extrude and plate
      if len(command) == 4:

        try:

          x = int(command[0])
          y = int(command[1])
          extrude = int(command[2])
          plate = int(command[3])

          command_available = True

        except ValueError:
          
          # We have a rogue serial line, skip it
          command_available = False


      if command_available == True:

        print "Command received :", x, y, extrude, plate

        degrees = {}

        if x < lower_bound:
          # We want to move the extruder to the left
          degrees['X'] = +config.printer.travel.step
        elif x > upper_bound:
          # ... to the right
          degrees['X'] = -config.printer.travel.step

        if y < lower_bound:
          # We're going further from the face of the printer
          degrees['Y'] = -config.printer.travel.step
        elif y > upper_bound:
          # ... and closer
          degrees['Y'] = +config.printer.travel.step

        if extrude == 1:
          self.extrusion += config.printer.extrusion.step
          degrees['E'] = self.extrusion

        if plate == 1:
          self.z += config.printer.plate.step
          self.movePlateTo(self.z)

          # TODO insert timer to avoid multiple bed descents
          # TODO insert timer to avoid multiple bed descents
          # TODO insert timer to avoid multiple bed descents
          # TODO insert timer to avoid multiple bed descents
          
          continue # When moving the bed down, we don't allow any other command

        # We need to "move" somehow on any degree of freedom including extrusion
        if len(degrees) > 0:

          gcode = config.printer.general_gcode
          for key, value in degrees.iteritems():
            gcode += " " + key + str(value)

          self.sendGCode(gcode)

      time.sleep(config.printer.command_delay)

mc = RepRapMCPrinterController()

mc.connect()
mc.bootstrap()

# Start !
mc.start()
