import cvcomm

class ControlVault3:
	NAME = 'Broadcom ControlVault 3'

	turn_on_seq1 = [
		"20 00 01 00",
	]
	turn_on_seq2 = [
		"20 00 01 00",
		"20 01 00",
		"20 03 02 01 52",
		"20 02 1f 0a 21 01 00 28 01 00 30 01 04 31 01 03 54 01 06 5b 01 00 60 01 07 80 01 01 81 01 01 82 01 0e",
		"21 00 10 05 04 03 02 05 03 03 01 01 01 02 01 01 03 01 01",
		"21 01 07 00 01 01 03 00 01 05",
		"20 02 09 01 b9 06 01 00 00 0b 00 00",
		"20 02 c7 11 18 01 02 2a 01 32 80 01 00 c2 02 03 02 c4 02 00 13 ca 05 00 0f 0d 03 08 cb 01 00 d6 0b 01 01 00 01 12 00 01 00 01 00 01 d8 01 01 de 04 01 00 00 00 e0 07 00 60 93 1c 63 3e 0a e1 02 79 07 e2 2a 48 07 0c 10 00 31 39 39 39 39 39 39 39 39 39 39 41 39 90 90 90 90 3f 90 90 90 88 8a 8c 94 94 28 04 07 00 00 00 00 00 00 00 00 e3 08 17 04 16 0d 10 0c 2b 0b e4 01 37 e5 1e e0 1e 02 12 00 0a 00 10 04 54 54 54 54 2b 52 50 53 4e 20 2d 18 0c 02 07 00 94 70 94 70 20 e6 2d 01 68 00 77 00 8b 00 a7 00 d6 00 22 01 c0 01 9e 58 4c 40 33 26 20 1e 68 00 77 00 8b 00 a7 00 d6 00 22 01 c0 01 5e 58 4c 40 33 2b 26 1e",
		"2f 1b 06 08 00 00 01 00 00",
		"20 02 2d 04 29 11 46 66 6d 01 01 11 02 02 03 80 03 02 00 01 04 01 64 2a 01 30 61 11 46 66 6d 01 01 11 02 02 03 80 03 02 00 01 04 01 64 62 01 30",
		"20 02 0e 04 18 01 01 32 01 40 50 01 02 00 02 2c 01",
		"21 03 0d 06 00 01 01 01 02 01 06 01 80 01 82 01",
	]

	def __init__(self, device):
		self.device = device
		self.communicator = cvcomm.ControlVaultCommunicator(device)

	def turn_on(self):
		self.communicator.ctrl_transfer(0x41, 1, 0, 3)
		self.communicator.talk(self.turn_on_seq1)
		self.communicator.ctrl_transfer(0x41, 1, 1, 3)
		self.communicator.ctrl_transfer(0x41, 0, 0, 3)
		self.communicator.ctrl_transfer(0x41, 0, 1, 3)
		self.communicator.ctrl_transfer(0x41, 1, 0, 3)
		self.communicator.talk(self.turn_on_seq2)
		self.communicator.ctrl_transfer(0x41, 1, 1, 3)

	def turn_off(self):
		self.communicator.ctrl_transfer(0x41, 1, 0, 3)
		self.communicator.ctrl_transfer(0x41, 0, 0, 3)

	def reset(self):
		self.device.reset()
