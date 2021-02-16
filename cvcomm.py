import logging
import math
import struct
import usb.util

def to_hex(val):
	return ' '.join([bytes([i]).hex() for i in val])

class ControlVaultCommunicator:
	def __init__(self, device, spi_master=0x01, spi_slave=0x00, spi_crc=0x00):
		self.logger = logging.getLogger(__name__)
		self.device = device
		self.bulk_in, self.bulk_out = self._find_endpoints()

		self.spi_master = spi_master
		self.spi_slave = spi_slave
		self.spi_crc = spi_crc
		self.spi_slave_prefix = struct.pack('>BB', self.spi_slave, self.spi_crc)

	def ctrl_transfer(self, *args, **kwargs):
		self.logger.debug('Control: {} {}'.format(args, kwargs))
		return self.device.ctrl_transfer(*args, **kwargs)

	def write(self, *args, **kwargs):
		return self.bulk_out.write(*args, **kwargs)

	def read(self, *args, **kwargs):
		return self.bulk_in.read(*args, **kwargs)

	def send_packet(self, payload):
		length = len(payload)
		packet = struct.pack('>BBH', self.spi_master, self.spi_crc, length) + payload
		self.logger.debug('Put: {}'.format(to_hex(packet)))
		self.write(packet)

	def recv_packet(self):
		packet = self.read(64, timeout=5000).tobytes()
		tag = packet[0:2]
		if tag != self.spi_slave_prefix:
			raise Exception('Unknown tag: {}'.format(tag.hex()))
		length = packet[2:4]
		length = struct.unpack('>H', length)[0]

		for i in range(0, math.ceil(length/64) - 1):
			packet += self.read(64).tobytes()

		self.logger.debug('Got: {}'.format(to_hex(packet)))
		return packet[4:]

	def talk(self, exchange):
		for packet in exchange:
			self.send_packet(bytes.fromhex(packet))
			data = self.recv_packet()

			if data[1] == 0x61:
				packet = self.recv_packet()

	def _find_endpoints(self):
		self.logger.debug('Enumerating interfaces...')
		configuration = self.device.get_active_configuration()
		bcm_interface = None
		has_contacted = False
		has_contactless = False
		for interface in configuration:
			if interface.bInterfaceClass == 0xff:
				if bcm_interface is not None:
					raise Exception('More than one vendor-specific interface found!')
				bcm_interface = interface
			if interface.bInterfaceClass == 0xb:
				if interface.iInterface == 0x5:
					has_contacted = True
				if interface.iInterface == 0x6:
					has_contactless = True
		if not has_contactless:
			raise Exception('No contactless reader on this device!')
		if bcm_interface is None:
			raise Exception('Cannot find vendor-specific interface')
		self.logger.debug('Interface found: {}'.format(bcm_interface._str()))

		self.logger.debug('Enumerating endpoints...')
		bulk_in = None
		bulk_out = None
		for endpoint in bcm_interface:
			if endpoint.bmAttributes & usb.util._ENDPOINT_TRANSFER_TYPE_MASK == usb.util.ENDPOINT_TYPE_BULK:
				if endpoint.bEndpointAddress & usb.util._ENDPOINT_DIR_MASK == usb.util.ENDPOINT_IN:
					if bulk_in is not None:
						raise Exception('More than one BULK IN endpoint found!')
					bulk_in = endpoint
					self.logger.debug('BULK IN found: {}'.format(bulk_in._str()))
				if endpoint.bEndpointAddress & usb.util._ENDPOINT_DIR_MASK == usb.util.ENDPOINT_OUT:
					if bulk_out is not None:
						raise Exception('More than one BULK OUT endpoint found!')
					bulk_out = endpoint
					self.logger.debug('BULK OUT found: {}'.format(bulk_out._str()))

		if bulk_in is None:
			raise Exception('BULK IN endpoint not found!')
		if bulk_out is None:
			raise Exception('BULK OUT endpoint not found!')

		self.logger.debug('Endpoint discovery successful.')
		return bulk_in, bulk_out
