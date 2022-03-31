import logging
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
