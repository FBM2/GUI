'''
Communicating through serial port using pySerial
'''

import serial
import serial.tools.list_ports
import os

class Serial_control():

    def __init__(self, comm_port, timeout=2, on_close=None, log=None, verbose=False):
        self.alive = False
        self.on_close = on_close
        self.log = log

        self.sp = None
        self.verbose = verbose
        if comm_port is not None:
            self.comm_port = comm_port
        else:
            lpis = list(serial.tools.list_ports.comports())     # lpi = ListPortInfo object
            for lpi in lpis:
                self.comm_port = lpi[0]          # here we end up using the last one found
                print('found', lpi[0], '   description:',lpi[1])
        self.sp = serial.Serial(self.comm_port, timeout=timeout)        # connect to serial port

        if self.verbose:
            print('connected as "',self.sp.name,'"',sep='')             # determine and mention which port was really used

        # self.sp.baudrate = 9600
        # self.sp.bytesize = serial.EIGHTBITS
        # self.sp.parity = serial.PARITY_NONE
        # self.sp.stopbits = serial.STOPBITS_TWO
        self.sp.timeout = timeout
        self.sp.write_timeout = timeout

    def __del__(self):
        try:
            if self.alive:
                self.close()
        except:
            pass  # XXX errors on shutdown

    @ property
    def flush(self):
        self.sp.flush()

    def open(self):
        """open serial port"""

        try:
            self.sp.rts = False
            self.sp.open()
        except Exception as msg:
            self.handle_serial_error(msg)

        self.serial_settings_backup = self.sp.get_settings()

        # now we are ready
        self.alive = True

    def close(self):
        """Close serial port"""
        if self.log is not None:
            self.log.info("{}: closing...".format(self.comm_port))
        self.alive = False
        self.sp.flush
        self.sp.close()

        if self.on_close is not None:
            # ensure it is only called once
            callback = self.on_close
            self.on_close = None
            callback(self)


    def handle_serial_read(self):
        """Read data from serial port"""
        try:
            data = self.sp.read_until().decode()
            if len(data) != 0:
                return data
            else:
                self.handle_serial_error('Read recieve 0 Bytes')
        except Exception as msg:
            self.handle_serial_error(msg)

    def handle_serial_write(self, cmd):
        """Write cmd as bytes to serial port"""
        
        try:
            l = self.sp.write(cmd)

            if l != len(cmd):
                self.sp.flush # nominally, waits until all data is written

            if self.verbose:
                print('send_cmd("',cmd,'")', sep='',end='')

            c_r = self.sp.read_until().decode()

            if self.verbose:
                print(' -->', c_r)

            return c_r

        except Exception as msg:
            self.handle_serial_error(msg)

    def handle_serial_error(self, error=None):
        """Serial port error"""
        # terminate connection
        self.close()
        print(self.comm_port + ' closed due to error: ' + error)
