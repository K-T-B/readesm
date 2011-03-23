#!/usr/bin/python
# -*- coding: utf-8 -*-

## Tool to read tachograph data from a vehicle unit connected serially 
## Copyright(C) Andreas Gölzer

#This is free software: you can redistribute it and/or modify it under the
#terms of the GNU General Public License as published by the Free Software
#Foundation, either version 3 of the License, or (at your option) any later
#version.

#It is distributed in the hope that it will be useful, but WITHOUT ANY
#WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along with
#this program.  If not, see <http://www.gnu.org/licenses/>.

from serial import Serial
from optparse import OptionParser
from struct import pack, unpack
from datetime import date

parser = OptionParser(version="%prog 0.1")
parser.add_option("-s", "--serial", dest="serial",
                  help="serial terminal the VU is connected to", default='/dev/ttyUSB0', metavar="FILE")
parser.add_option("-o", "--output", dest="output",
                  help="File to save readesm data to", default='test.esm', metavar="FILE")


(options, args) = parser.parse_args()


class malformedHeader(Exception):
	def __init__(self, received):
		self.received = received
	def __str__(self):
		return "Expected 0x80 0xF0 0xEE, got " + self.received

class communicationError(Exception):
	def __init__(self, description):
		self.description = description
	def __str__(self):
		return description

class wrongChecksum(Exception):
	def __str__(self):
		return "Received message had wrong checksum"

class vuErrorMessage(Exception):
	def __init__(self, code, requestSID):
		self.code = code
		self.requestSID = requestSID
	def __str__(self):
		errors = {
			0x10 : 'General reject',
			0x11: 'Service not supported',
			0x12: 'Sub function not supported',
			0x13: 'Incorrect Message Length',
			0x22: 'Conditions not correct or Request sequence error',
			0x31: 'Request out of range',
			0x50: 'Upload not accepted',
			0x78: 'Response pending',
			0xFA: 'Data not available'
		}
		rv = "The VU has rejected the request with SID %s and returned an error instead: " % hex(self.requestSID)
		if self.code in errors:
			rv += errors[self.code]
		else:
			rv += "Unknown error code %s" % hex(self.code)
		return rv
	
class vuSerial:
	def __init__(self, maxBaudRate=115200):
		self.open = False
		self.conn = Serial(options.serial, 9600, timeout=5)
		sendRawExpectingResponse('\x81\xEE\xF0\x81\xE0', '\xC1\x8F\xEA', 'Start Communication Request')
		sendExpectingResponse('\x10\x81\x50\x81', 'Diagnostic Session')

		baudRates = {9600:1, 19200:2, 38400:3, 57600:4, 115200:5}
		for baudRate in sorted(baudRates, reverse=True):
			if maxBaudRate < baudRate:
				continue			
			try:
				self.sendExpectingResponse('\x87\x01\x01' + chr(baudRates[baudRate]),'\xC7\x01', "Request Byte rate %i" % baudRate)
			except communicationError as err:
				print err
			else:
				self.sendData('\x87\x02\x03')
				self.conn.baudrate = baudRate
				break
		
		self.sendExpectingResponse('\0\0\0\0\xFF\xFF\xFF\xFF', '\0\xFF', name = 'Request Upload')
		self.open = True

	def __del__(self):
		self.close()
		
	def close(self):
		if self.open:
			self.sendExpectingResponse(chr(0x35), chr(0x77), name = 'Transfer Exit')
			self.sendExpectingResponse(chr(0x82), chr(0xC2), name = 'Stop Communication')
			self.conn.close()
		
	def _getChecksum(self, data):
		sum = 0
		for byte in data:
			sum += ord(data)
		return sum % 256

	def getBlock(self, TREP, parameter = ''):
		self.sendData(chr(0x36) + chr(TREP) + parameter)
		payload = ''
		counter = 1
		failcounter = 0
		while():
			try:
				response = singleResponse()
			except wrongChecksum, malformedHeader:
				failcounter += 1
				if failcounter == 3:
					raise communicationError("Failed to get the same 265-byte-chunk three times, aborting")
				self.sendData(chr(0x83) + chr(0x36) + pack(">H",counter))
				
				
			else:
				failcounter = 0
				payload += response[4:]
				if len(response) < 255:
					break
				counter += 1
				self.sendData(chr(0x83) + chr(0x36) + pack(">H",counter))
		return payload

	def sendRawExpectingResponse(self, rawsenddata, expectdata, name = ''):
		print "Sending 'Request %s'" % name
		self.sendData(senddata)
		response = self.singleResponse()
		if response == expectdata:
			print "Got the expected response"
		else:
			raise communicationError("Expected " + expectdata + " as response to " + name + ", got " + response)
		
	def sendExpectingResponse(self, senddata, expectdata, name = ''):
		return sendRawExpectingResponse(composeMessage(senddata), expectdata, name)

	def singleResponse(self):
		header = self.conn.read(4)
		if header[0:3] != '\x80\xF0\xEE':
			raise malformedHeader(header)
		length = ord(header[3])
		dataWithChecksum = self.conn.read(length + 1)
		payload = dataWithChecksum[:-1]
		if _getChecksum(header + payload) == ord(dataWithChecksum[-1]):
			if length == 3 and ord(payload[0])  == 0x7F:
				raise vuErrorMessage(ord(payload[2]), ord(payload[1]))  
			return payload
		else:
			raise wrongChecksum

	def sendData(self, data):
		self.conn.write(self.composeMessage(data))
		
	def composeMessage(self, data):
		fullmsg = '\x80\xEE\xF0' + chr(len(data)) + data
		sum = _getChecksum(fullmsg)
		return fullmsg + chr(sum)


print "This is completely untested, without some hacking this will not work, and even if it does, it won't do what you expect"

vu = vuSerial()
data = vu.getBlock(1)
print "Read data from vehicle unit in ", data[388:388+17]
minDate = unpack('>I',data[424:428])
maxDate = unpack('>I',data[428:432])
print "Downloadable data is from " +  date.fromtimestamp(mindate) + " to " + date.fromtimestamp(maxdate) 

for date in Range(minDate, maxDate + 1, 86400):
	print "Downloading data for " +  date.fromtimestamp(date)
	try:
		data += vu.getBlock(2, pack('>I',date))
	except vuErrorMessage as err:
		print err
	except communicationError as err:
		print err
	
for TREP in range(3,7):
	print "asking for data block TREP", TREP
	try:
		data += vu.getBlock(TREP)
	except vuErrorMessage as err:
		print err
	except communicationError as err:
		print err

vu.close()

esmfile = fopen(options.output)
esmfile.write(data)
esmfile.close()


