import cvcomm

class ControlVault2:
	NAME = 'Broadcom ControlVault 2'

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

	def __init__(self, device):
		self.device = device
		self.communicator = cvcomm.ControlVaultCommunicator(device)

	def turn_on(self):
		self.communicator.ctrl_transfer(0x41, 0, 1, 3)
		self.communicator.talk(self.turn_on_seq1)
		self.communicator.ctrl_transfer(0x41, 1, 0, 3)
		self.communicator.talk(self.turn_on_seq2)
		self.communicator.ctrl_transfer(0x41, 1, 1, 3)

	def turn_off(self):
		self.communicator.ctrl_transfer(0x41, 1, 0, 3)
		self.communicator.ctrl_transfer(0x41, 0, 0, 3)

	def reset(self):
		self.device.reset()
