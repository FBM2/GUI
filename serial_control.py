'''
Communicating through serial port using pySerial
'''

import serial
import os

class Serial_control():

    def __init__(self, device, on_close=None, log=None):
        self.alive = False
        self.on_close = on_close
        self.log = log
        self.device = device
        self.serial = serial.Serial()
        self.serial.port = device
        self.serial.baudrate = 9600
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_TWO
        self.serial.timeout = 5
        self.serial.write_timeout = 5

    def __del__(self):
        try:
            if self.alive:
                self.close()
        except:
            pass  # XXX errors on shutdown

    def open(self):
        """open serial port"""

        try:
            self.serial.rts = False
            self.serial.open()
        except Exception as msg:
            self.handle_serial_error(msg)

        self.serial_settings_backup = self.serial.get_settings()

        # now we are ready
        self.alive = True

    def close(self):
        """Close serial port"""
        if self.log is not None:
            self.log.info("{}: closing...".format(self.device))
        self.alive = False

        self.serial.close()
        if self.on_close is not None:
            # ensure it is only called once
            callback = self.on_close
            self.on_close = None
            callback(self)


    def handle_serial_read(self):
        """Read data as bytes from serial port"""
        try:
            data = self.serial.read()
            if len(data) != 0:
                return data
            else:
                self.handle_serial_error('Read recieve 0 Bytes')
        except Exception as msg:
            self.handle_serial_error(msg)

    def handle_serial_write(self, cmd):
        """Write cmd as bytes to serial port"""
        try:
            l = self.serial.write(cmd)
            if l != len(cmd):
                self.handle_serial_error('Command send length error')
        except Exception as msg:
            self.handle_serial_error(msg)

    def handle_serial_error(self, error=None):
        """Serial port error"""
        # terminate connection
        self.close()
        print(self.device + ' closed due to error: ' + error)
