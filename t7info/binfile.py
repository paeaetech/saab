
import struct
import sys

class BinException(Exception):
	pass

class HeaderId:
	VIN = 0x90
	IMMOBILIZER = 0x92
	CHECKSUM_F2 = 0xf2
	CHECKSUM_FB = 0xfb
	CHECKSUM_START = 0xfd
	CHECKSUM_END = 0xfe
	ENGINE_TYPE = 0x97
	SW_VERSION = 0x95
	SW_PART_NUMBER = 0x94
	HW_PART_NUMBER = 0x91
	
	@staticmethod
	def getName(_id):
		if _id == HeaderId.VIN:
			return "VIN"
		elif _id == HeaderId.IMMOBILIZER:
			return "Immobilizer"
		elif _id == HeaderId.ENGINE_TYPE:
			return "Engine Type"
		elif _id == HeaderId.SW_VERSION:
			return "ECU SW Version"
		elif _id == HeaderId.SW_PART_NUMBER:
			return "SW Part number"
		elif _id == HeaderId.HW_PART_NUMBER:
			return "HW Part number"
		elif _id == HeaderId.CHECKSUM_F2:
			return "F2 checksum"
		elif _id == HeaderId.CHECKSUM_FB:
			return "FB checksum"
		elif _id == HeaderId.CHECKSUM_START:
			return "Checksum area start"
		elif _id == HeaderId.CHECKSUM_END:
			return "Checksum area end"
		return "Unknown"

		

class BinFile(object):
	
	
	def __init__(self,_filename):
		f = open(_filename)
		
		self.data = f.read()
		self.header = {}
		
		if len(self.data) != 512*1024:
			raise BinException("data is wrong size (%d)" % len(self.data))
			
		self._parse()
		
	def getHeader(self,_id):
		if str(_id) in self.header:
			return self.header[str(_id)][0]
			
		return None

	def getHeaderFormatted(self,_id):
		if str(_id) in self.header:
			return self.header[str(_id)][1]

		return None

		
	def _parse(self):
		is_motorola = ord(self.data[2]) == 0xfc and ord(self.data[3]) == 0xef
		
		if is_motorola:
			print "Warning: file is in wrong byteorder"
		
		self.is_motorola = is_motorola
		self._readHeader()

	def _readHeader(self):
		pos = len(self.data)-1
		while True:
			size = ord(self.data[pos])
			pos-=1
			_id = ord(self.data[pos])
			pos-=1
			if size == 0 or size == 0xff:
				break
				

			data = ""
			for i in range(size):
				data += self.data[pos]
				pos-=1

		
			if size == 4:
				(hdr,) = struct.unpack(">I",data)
				asc = "0x%08x" % hdr
			else:
				hdr = data
				asc = data
				
			self.header[str(_id)]=(hdr,asc)
		
	def printHeader(self):
		print "Header:"
		print "  ID %s DATA" % 'NAME'.ljust(20)
		print ""


		for k,v in self.header.items():
			
			print "  %02x %s %s" % (int(k),HeaderId.getName(int(k)).ljust(20),self.getHeaderFormatted(int(k)))
		
		
	def _checksum_f2(self,start,length):
		XOR_TABLE = (0x81184224, 0x24421881, 0xc33c6666, 0x3cc3c3c3, 0x11882244, 0x18241824, 0x84211248, 0x12345678)
		
		const1 = 0x40314081
		const2 = 0x7FEFDFD0
		
		xorc = 1
		checksum = 0
		
		pos = start
		while length:
			(temp,) = struct.unpack_from(">I",self.data,pos)
			checksum += temp ^ XOR_TABLE[xorc]
			xorc = (xorc+1) % len(XOR_TABLE)
			pos += 4
			length-=4

		
		checksum = checksum ^ const1
		checksum -= const2
		checksum = checksum & 0xffffffff

		return checksum
		
	def _checksum_fb(self,start,length):
		
		checksum = 0
		pos = start
		
		while length>>2:
			(temp,) = struct.unpack_from(">I",self.data,pos)
			checksum += temp
			pos+=4
			length -= 4
		
		checksum8 = 0
		for i in range(length):
			temp = ord(self.data[pos])
			pos+=1
			checksum8 += temp
			
		checksum8 = checksum8 & 0xff
		checksum += checksum8
		checksum = checksum & 0xffffffff
		return checksum
		
		
	def calculate_f2(self):
		start = self.getHeader(HeaderId.CHECKSUM_START)
		end = self.getHeader(HeaderId.CHECKSUM_END)
		
		return self._checksum_f2(start,end-start)
		
	def calculate_fb(self):
		start = self.getHeader(HeaderId.CHECKSUM_START)
		end = self.getHeader(HeaderId.CHECKSUM_END)
		
		return self._checksum_fb(start,end-start)
		
