#!/usr/bin/env python3

import logging
import sys
import usb.core

class UsbDeviceMatcher:
	def __init__(self, properties, handler):
		self.properties = properties
		self.handler = handler

	def matches(self, candidate):
		for prop, value in self.properties.items():
			if prop not in candidate.__dict__ or candidate.__dict__[prop] != value:
				return False
		return True

class UsbDeviceFinder:
	SUPPORTED_DEVICES = [
		UsbDeviceMatcher({'idVendor': 0x0A5C, 'idProduct': 0x5832}, lambda device: __import__('cv2').ControlVault2(device)),
		UsbDeviceMatcher({'idVendor': 0x0A5C, 'idProduct': 0x5834}, lambda device: __import__('cv2').ControlVault2(device)),
		UsbDeviceMatcher({'idVendor': 0x0A5C, 'idProduct': 0x5842}, lambda device: __import__('cv3').ControlVault3(device)),
		UsbDeviceMatcher({'idVendor': 0x0A5C, 'idProduct': 0x5843}, lambda device: __import__('cv3').ControlVault3(device)),
	]

	@classmethod
	def _dev_matcher(cls, device):
		for matcher in cls.SUPPORTED_DEVICES:
			if matcher.matches(device):
				return True
		return False

	@classmethod
	def _cls_matcher(cls, device):
		for matcher in cls.SUPPORTED_DEVICES:
			if matcher.matches(device):
				return matcher.handler(device)
		raise Exception('Cannot find handler for device {:04X}:{:04X}'.format(dev.idVendor, dev.idProduct))

	@classmethod
	def find(cls):
		logger = logging.getLogger(__name__)
		logger.info('Looking for supported device...')

		device = usb.core.find(custom_match=cls._dev_matcher)
		if device is None:
			raise Exception('Cannot find BCM device - check list of supported devices')
		logger.info('Found {:04X}:{:04X}'.format(device.idVendor, device.idProduct))

		handler = cls._cls_matcher(device)
		logger.info('Handler {} ({})'.format(handler.__class__.__name__, handler.NAME))
		return handler


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print('Usage: {} [on|off|reset]'.format(sys.argv[0]))
		sys.exit(2)

	logging.basicConfig(level=logging.DEBUG)
	logger = logging.getLogger(__name__)

	logger.info("Checking for dependencies...")
	if "pyusb" not in {pkg.key for pkg in pkg_resources.working_set}:
		logger.info("pyusb is not available.")

		if (input("Seems you are missing \"pyusb\". Would you like to install it now? (y/N)") == 'y'):
			try:
				print("> pip install pyusb")
				cp = subprocess.run(["pip", "install", "pyusb"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				print(cp.stdout.decode())

			except Exception as e:
				print(str(e) + "\nERROR: There was a problem and the package could not be installed.\n"
					"Try installing the library manually with pip:\n"
					"> pip install pyusb\n"
					"More info here: https://pypi.org/project/pyusb/#files\n and here: https://github.com/walac/pyusb")
				sys.exit()

			print("Success: pyusb has been installed")

		else:
			logger.info("...permission denied")
			raise Exception("Missing required library: pyusb.")
	logger.info("pyusb is installed.")

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
