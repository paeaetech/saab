#!/usr/bin/python

from binfile import *
		
__VERSION = "v0.1"		
__NAME = "T7Info.py"

def printHelp():
	print ""
	print "Usage: %s binfile" % sys.argv[0]
		
def main():
	print "%s %s, (c) Mikko Sivulainen. Based on code by Tomi Liljemark" % (__NAME,__VERSION)
	print""
	
	if len(sys.argv) < 2:
		printHelp()
		return
		
	try:
		b = BinFile(sys.argv[1])
	except BinException as e:
		print "Error: %s" % e
		return
		
	b.printHeader()
	print ""
	csum = b.calculate_f2()
	if csum == b.getHeader(HeaderId.CHECKSUM_F2):
		status = "OK"
	else:
		status = "FAIL"

	print "F2 calculated checksum is 0x%08x: %s" % (csum,status)
	
	csum = b.calculate_fb()
	if csum == b.getHeader(HeaderId.CHECKSUM_FB):
		status = "OK"
	else:
		status = "FAIL"
	
	print "FB calculated checksum is 0x%08x: %s" % (csum,status)
	
	
		
if __name__ == '__main__':
	main()