#!/usr/bin/env python3

# Enable NFC on Linux (CCID/PCSCD)
# Dell E7470
# Dell ControlVault2
# BCM20795 (20795A1)

import binascii
import logging
import math
import struct
import sys
import time
import usb.core
import usb.util

VENDOR_ID = 0x0A5C
DEVICE_ID = 0x5834

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def to_hex(val):
	return ' '.join([bytes([i]).hex() for i in val])

class BcmCommunicator:
	def __init__(self, device, bulk_in, bulk_out):
		self.logger = logging.getLogger(__name__)
		self.device = device
		self.bulk_in = bulk_in
		self.bulk_out = bulk_out
	
	def ctrl_transfer(self, *args, **kwargs):
		self.logger.debug('Control: {} {}'.format(args, kwargs))
		return self.device.ctrl_transfer(*args, **kwargs)
	
	def write(self, *args, **kwargs):
		return self.bulk_out.write(*args, **kwargs)
	
	def read(self, *args, **kwargs):
		return self.bulk_in.read(*args, **kwargs)
	
	def send_packet(self, payload):
		packet_type = 0x01
		unknown1 = 0x00
		length = len(payload)
		
		packet = struct.pack('>BBH', packet_type, unknown1, length) + payload
		
		self.logger.debug('Put: {}'.format(to_hex(packet)))
		self.write(packet)

	def recv_packet(self):
		packet = self.read(64, timeout=5000).tobytes()
		tag = packet[0:2]
		if tag != b'\x00\x00':
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
	
	@classmethod
	def find(cls, vendor_id, product_id):
		logger = logging.getLogger(__name__)
		logger.info('Looking for device {:04X}:{:04X}...'.format(vendor_id, product_id))
		
		device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
		if device is None:
			raise Exception('Cannot find device {:04X}:{:04X}'.format(vendor_id, product_id))
		
		logger.debug('Enumerating interfaces...')
		configuration = device.get_active_configuration()
		bcm_interface = None
		for interface in configuration:
			if interface.bInterfaceClass == 0xff and interface.iInterface == 0x08:
				bcm_interface = interface
				break
		if bcm_interface is None:
			raise Exception('Cannot find vendor-specific interface')
		logger.debug('Interface found: {}'.format(bcm_interface._str()))
		
		logger.debug('Enumerating endpoints...')
		bulk_in = None
		bulk_out = None
		for endpoint in bcm_interface:
			if endpoint.bmAttributes & usb.util._ENDPOINT_TRANSFER_TYPE_MASK == usb.util.ENDPOINT_TYPE_BULK:
				if endpoint.bEndpointAddress & usb.util._ENDPOINT_DIR_MASK == usb.util.ENDPOINT_IN:
					if bulk_in is not None:
						raise Exception('More than one BULK IN endpoint found!')
					bulk_in = endpoint
					logger.debug('BULK IN found: {}'.format(bulk_in._str()))
				if endpoint.bEndpointAddress & usb.util._ENDPOINT_DIR_MASK == usb.util.ENDPOINT_OUT:
					if bulk_out is not None:
						raise Exception('More than one BULK OUT endpoint found!')
					bulk_out = endpoint
					logger.debug('BULK OUT found: {}'.format(bulk_out._str()))
		
		if bulk_in is None:
			raise Exception('BULK IN endpoint not found!')
		if bulk_out is None:
			raise Exception('BULK OUT endpoint not found!')
		
		logger.debug('Returning {} object...'.format(cls.__name__))
		return cls(device, bulk_in, bulk_out)

turn_on_seq1 = [
	"10 2f 04 00",
	"10 2f 1d 03 05 90 65",
	"10 2f 2d 00",
	"10 2f 11 01 f7",
	"01 27 fc 0c 08 00 01 00 01 00 00 00 00 00 00 00",
]
turn_on_seq2 = [
	"10 20 00 01 01",
	"10 20 01 02 01 00",
	"10 20 02 67 01 b9 64 01 00 ff ff 50 00 8b 13 00 10 00 06 00 00 00 00 00 ff 00 00 00 ff 00 00 04 00 00 00 00 03 00 00 00 03 00 0c 00 00 0d 00 00 00 00 00 00 00 00 00 00 33 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 02 53 3b 0f 00 00 00 00 00 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00",
	"10 20 02 90 0a ca 05 00 00 00 00 2c 80 01 01 b0 05 01 03 03 03 08 b5 03 01 03 ff c9 0d 24 00 00 00 01 00 bb 00 e4 00 0a 01 02 d6 0d 01 02 00 00 00 00 00 01 00 01 5a 00 8a b2 02 e8 03 c8 1e 06 1f 00 0a 00 30 00 04 24 00 1c 00 75 00 77 00 76 00 1c 00 03 00 0a 00 56 01 00 00 40 04 d7 01 07 dd 32 00 00 00 29 16 08 08 06 04 00 00 00 1f 27 0a 6d 20 00 52 20 00 00 00 01 85 00 00 32 1f 00 00 02 0a 16 00 02 55 55 55 55 55 55 55 55 55 55 55 55 55 1e",
	"10 20 02 06 01 b7 03 02 00 01",
	"10 2f 06 01 01",
	"10 20 02 0e 02 51 08 20 79 ff ff ff ff ff ff 58 01 07",
	"10 21 00 07 02 04 03 02 05 03 03",
	"10 20 02 17 01 29 14 46 66 6d 01 01 11 02 02 07 ff 03 02 00 13 04 01 64 07 01 03",
	"10 20 02 1a 02 61 14 46 66 6d 01 01 11 02 02 07 ff 03 02 00 13 04 01 64 07 01 03 60 01 07",
	"10 20 02 10 05 30 01 04 31 01 00 32 01 40 38 01 00 50 01 02",
	"10 20 02 05 01 00 02 fa 00",
	"10 20 02 0b 01 c2 08 01 08 00 04 80 c3 c9 01",
	"10 21 03 0d 06 00 01 01 01 02 01 80 01 82 01 06 01",
]

def turn_on(communicator):
	communicator.ctrl_transfer(0x41, 0, 1, 3)
	communicator.talk(turn_on_seq1)
	communicator.ctrl_transfer(0x41, 1, 0, 3)
	communicator.talk(turn_on_seq2)
	communicator.ctrl_transfer(0x41, 1, 1, 3)

def turn_off(communicator):
	communicator.ctrl_transfer(0x41, 1, 0, 3)
	communicator.ctrl_transfer(0x41, 0, 0, 3)



if __name__ == "__main__":
	if len(sys.argv) < 2:
		print('Usage: {} [on|off]'.format(sys.argv[0]))
		sys.exit(2)
	
	communicator = BcmCommunicator.find(VENDOR_ID, DEVICE_ID)
	if sys.argv[1] == 'on':
		logger.info('Turning NFC on...')
		turn_on(communicator)
		logger.info('NFC should be turned on now!')
	elif sys.argv[1] == 'off':
		logger.info('Turning NFC off...')
		turn_off(communicator)
		logger.info('NFC should be turned off now!')
	else:
		raise Exception('Unknown option: {}'.format(sys.argv[1]))
