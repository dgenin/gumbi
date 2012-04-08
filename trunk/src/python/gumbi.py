#!/usr/bin/env python

import serial
import struct
import time

class Gumbi:
	"""
	Primary gumbi class. All other classes should be subclassed from this.
	"""

	ACK = "A"
	NACK = "N"
	BAUD = 9600
	DEFAULT_PORT = '/dev/ttyUSB0'
	MAX_PINS = 128
	RESET_LEN = 1024

	NOP = 0
	PFLASH = 1
	SPIFLASH = 2
	SPIEEPROM = 3
	I2CEEPROM = 4
	PING = 5
	INFO = 6
	SPEED = 7
	GPIO = 8
	ID = 9

	EXIT = 0
	READ = 1
	WRITE = 2
	ERASE = 3
	HIGH = 4
	LOW = 5

	def __init__(self, port=None):
		"""
		Class constructor, calls self._open().
		@port - Gumbi serial port.
		"""
		self.serial = None
		self._open(port)

	def _open(self, port):
		"""
		Opens a connection to the Gumbi board.
		"""
		if port is None:
			port = self.DEFAULT_PORT
		self.serial = serial.Serial(port, self.BAUD)

	def _close(self):
		"""
		Closes the connection with the Gumbi board.
		"""
		self.serial.close()

	def Pin2Real(self, pin):
		"""
		Converts user-supplied pin numbers (index 1) to Gumbi board pin numbers (index 0).
		"""
		return (pin - 1)

	def Pack32(self, value):
		"""
		Packs a 32-bit value for transmission to the Gumbi board.
		"""
                return struct.pack("<I", value)

        def Pack16(self, value):
		"""
		Packs a 16-bit value for transmission to the Gumbi board.
		"""
                return struct.pack("<H", value)

        def PackByte(self, value):
		"""
		Packs an 8-bit value for transmission to the Gumbi board.
		"""
                return chr(value)

        def PackBytes(self, data):
		"""
		Packs an array of 8-bit values for transmission to the Gumbi board.
		"""
                pdata = ''
                for byte in data:
                        pdata += self.PackByte(byte)
                return pdata

	def ReadAck(self):
		"""
		Reads an ACK/NACK from the Gumbi board. Returns True on ACK, raises an exception on NACK.
		"""
		if self.Read(1) != self.ACK:
			raise Exception(self.ReadText())
		return True

	def SetMode(self, mode):
		"""
		Puts the Gumbi board in the specified mode.
		"""
		self.Write(self.PackByte(mode))

	def ReadText(self):
		"""
		Reads and returns a new-line terminated string from the Gumbi board.
		"""
		return self.serial.readline().strip()

	def Read(self, n=1):
		"""
		Reads n bytes of data from the Gumbi board. Default n == 1.
		"""
		return self.serial.read(n)

	def Write(self, data):
		"""
		Sends data to the Gumbi board and verifies acknowledgement.
		"""
		self.serial.write(data)
		self.ReadAck()

	def Reset(self):
		"""
		Resets the communications stream with the Gumbi board.
		"""
		self.serial.write(self.PackByte(self.EXIT))
		for i in range(0, self.RESET_LEN):
			self.SetMode(self.NOP)

	def Close(self):
		"""
		Closes the connection with the Gumbi board.
		"""
		return self._close()

class GPIO(Gumbi):
	"""
	Class to provide raw read/write access to all I/O pins.
	"""

	def __init__(self, port=None):
		"""
		Class constructor.
		"""
		Gumbi.__init__(self, port)
		self.SetMode(self.GPIO)

	def _exit(self):
		"""
		Exits the Gumbi board from GPIO mode.
		"""
		self.Write(self.PackBytes([self.EXIT, 0]))

	def PinHigh(self, pin):
		"""
		Sets the specified pin high.
		"""
		self.Write(self.PackBytes([self.HIGH, self.Pin2Real(pin)]))

	def PinLow(self, pin):
		"""
		Sets the specified pin low.
		"""
		self.Write(self.PackBytes([self.LOW, self.Pin2Real(pin)]))

	def ReadPin(self, pin):
		"""
		Reads and returns the value of the specified pin.
		High == 1, Low == 0.
		"""
		self.Write(self.PackBytes([self.READ, self.Pin2Real(pin)]))
		return ord(self.Read(1))

	def Close(self):
		"""
		Exits GPIO mode, closes the Gumbi board connection.
		"""
		self._exit()
		self._close()

class SpeedTest(Gumbi):

	def __init__(self, count, port=None):
		Gumbi.__init__(self, port)
		self.count = count
		self.SetMode(self.SPEED)

	def _test(self):
		self.Write(self.Pack32(self.count))
		self.Read(self.count)

	def Go(self):
		start = time.time()
		self._test()
		t = time.time() - start
		return t

class Info(Gumbi):

	def Info(self):
		data = []

		self.SetMode(self.INFO)
		while True:
			line = self.ReadText()
			if line == self.ACK:
				break
			else:
				data.append(line)
		return data

class Identify(Gumbi):

	def Identify(self):
		self.SetMode(self.ID)
		return self.ReadText()

class Ping(Gumbi):

	def Ping(self):
		self.SetMode(self.PING)
		return self.ReadAck()


if __name__ == '__main__':
	try:
		info = Info()
		print "Board info:", info.Info()
		info.Close()

		io = GPIO()
		print "Pin 3 status:", io.ReadPin(3)
		io.Close()

		s = SpeedTest(1024)
		print "Speed test (1024 bytes):", s.Go()
		s.Close()

	except Exception, e:
		print "Error:", e
