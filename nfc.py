#!/usr/bin/env python3
import logging
import sys

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print('Usage: {} [on|off|reset]'.format(sys.argv[0]))
		sys.exit(2)

	logging.basicConfig(level=logging.DEBUG)
	logger = logging.getLogger(__name__)

	try:
		from usbhandler import UsbDeviceFinder
	except ImportError as e:
		if e.name == 'usb':
			print("'usb' module note found!.\nThe 'pyusb' library is required.")
		sys.exit(1)    
	
	handler = UsbDeviceFinder.find()
	if sys.argv[1] == 'on':
		logger.info('Turning NFC on...')
		handler.turn_on()
		logger.info('NFC should be turned on now!')
	elif sys.argv[1] == 'off':
		logger.info('Turning NFC off...')
		handler.turn_off()
		logger.info('NFC should be turned off now!')
	elif sys.argv[1] == 'reset':
		logger.info('Resetting device...')
		handler.reset()
		logger.info('NFC device has been reset!')
	else:
		raise Exception('Unknown option: {}'.format(sys.argv[1]))
