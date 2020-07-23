# -*- coding: utf-8 -*-
"""
Serial communication to McPherson spectrometer scan controller 789A-4 via pyserial

For PySerial see documentation at https://pyserial.readthedocs.io/

For a list of ASCII commands see https://mcphersoninc.com/pdf/789A-4.pdf

"""

import time
from serial_control import Serial_control

class spectrometer:
	def __init__(self, comm_port=None, timeout=2, verbose=False):

		self.steps_per_rev = 36000  # Motor corresponds to 36000 steps/rev
		self.nm_per_rev = 4 # 4 nm/Motor rev

		self.verbose = verbose

		self.sp = Serial_control(comm_port, timeout=timeout, verbose=verbose)        # open serial port

		if verbose:
			print('attempting to establish communications with scan controller')
		self.id = self.send_cmd(' ')   # initialize - "After power-up, always send an ASCII [SPACE] before any other command is sent"
		if len(self.id) == 0:
			self.id = b'(unknown due to no response from Scan Controller)'
			if verbose:
				print('Scan Controller did not respond. Initialization already completed?')
		else:
			if self.id[-2:] == "\r\n":
				self.id = self.id[0:-2]
			print('Initialized Scan Controller "',self.id,'"',sep='')


	def __bool__(self):
		""" boolean test if valid - assumes valid if the serial port reports is_open """
		return self.sp.alive

	def __enter__(self):
		""" no special processing after __init__() """
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		""" same as __del__() """
		self.__del__()

	def __del__(self):
		""" close up """
		if self.sp.alive == True:
			self.sp.close()

	def send_cmd(self, s):
		""" Send ASCII command to scan controller.
			Add carriage return to every command send except [SPACE] (according to the manual).
			read_until() returns bytes when available and reads until ‘\n’ is found
			The return string contains the command itself at the beginning and '\r\n' at the end. These are removed from the return of the function.
		"""
		c = s
		if c != ' ':
			c += '\r\n'
		cmd = c.encode()
		c_r = self.sp.handle_serial_write(cmd)

		return c_r


#=====================================================================
#=====================================================================

	def is_moving(self):
		'''Read moving status to check if motor is still moving'''
		resp = self.send_cmd('^')
		if '0' in resp:
			if self.verbose:
				print('Not moving')
			return False
		
		elif '16' in resp:
			if self.verbose:
				print('Slewing')
			return True

		elif '1' in resp:
			if self.verbose:
				print('Moving')
			return True

		elif '2' in resp:
			if self.verbose:
				print('Moving fast')
			return True

		else:
			print('Unknown moving status')
			return 999

	def wait_for_motion_complete(self):
		'''Check motor moving status every 0.1 sec until stopped'''

		while self.is_moving == True:
			time.sleep(0.1)

		if self.verbose:
			print('stopped moving')

#=====================================================================

	def scan_up(self, d):
		steps = int(d / self.nm_per_rev * self.steps_per_rev)
		self.send_cmd('+' + str(steps))

	def scan_down(self, d):
		steps = int(d / self.nm_per_rev * self.steps_per_rev)
		self.send_cmd('-' + str(steps))

#=====================================================================

	def homing(self):
		'''
		TODO: This still needs testing and is not complete
		Homing should be done prior to scanning.
		Always perform the Homing Procedure every time power is disconnected.
		'''

		p.send_cmd('A8') # Enable home circuit

		resp = p.send_cmd(']') # Check home switch and try to move
			
		init = True
		stat = False
		while stat == False:
			try:
				resp = p.send_cmd(']')

				if '32' in resp:
					if init:
						p.send_cmd('M+23000')
						init = False
				elif '0' in resp:
					if init:
						p.send_cmd('M-23000')
						init = False
				else:
					p.send_cmd('@')
					stat = True
				
				time.sleep(0.8)
			except KeyboardInterrupt:
				p.send_cmd('@')
				break

if __name__ == '__main__':
	""" standalone """

	p = spectrometer(verbose=True)


		

#	p.close()

	print('done')
