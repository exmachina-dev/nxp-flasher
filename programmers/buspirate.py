#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Benoit Rapidel <benoit.rapidel+devs@exmachina.fr>
#
# Distributed under terms of the MIT license.

"""

"""

import serial
import time
import logging

from .abstract import ProgrammerError
from .serial import SerialProgrammer

logger = logging.getLogger('NXPprog.BusPirate')


class BusPirate(SerialProgrammer):
    PINDIR_CMD = 0b01000000
    PINSET_CMD = 0b10000000

    UART_START_ECHO_CMD =   0b00000010 # UART start echo uart RX
    UART_STOP_ECHO_CMD =    0b00000011 # UART stop echo uart RX
    UART_BRIDGE_CMD =       0b00001111 # bridge mode (reset to exit)
    UART_BULK_CMD =         0b00010000 # xxxx, Bulk transfer, send 1-16 bytes (0=1byte!)
    UART_SPEED_CMD =        0b01100000 # xxxx, Set speed,0000=300,0001=1200,10=2400,4800,9600,19200,31250, 38400,57600,1010=115200,
    UART_PINSET_CMD =       0b01000000 # wxyz, Set peripheral w=power, x=pullups, y=AUX, z=CS
    UART_CONFIG_CMD =       0b10000000 # wxxyz, config, w=output type, xx=databits and parity, y=stop bits, z=rx polarity (default :00000)

    UART_POWER =      0b00001000
    UART_PULLUP =     0b00000100
    UART_AUX_PIN =    0b00000010
    UART_CS_PIN =     0b00000001

    UART_BAUD_300    = 0b0000
    UART_BAUD_1200   = 0b0001
    UART_BAUD_2400   = 0b0010
    UART_BAUD_4800   = 0b0011
    UART_BAUD_9600   = 0b0100
    UART_BAUD_19200  = 0b0101
    UART_BAUD_33250  = 0b0110
    UART_BAUD_38400  = 0b0111
    UART_BAUD_57600  = 0b1000
    UART_BAUD_115200 = 0b1001

    POWER =      0b01000000
    PULLUP =     0b00100000
    AUX_PIN =    0b00010000
    MOSI_PIN =   0b00001000
    CLK_PIN =    0b00000100
    MISO_PIN =   0b00000010
    CS_PIN =     0b00000001

    def __init__(self, device, baudrate, *args, **kwargs):
        super().__init__(device, baudrate, *args, **kwargs)
        self._pinstate = 0
        self._pinconf = 0
        self._bridge_mode = False

        self.bridge_mode = True

    def init_device(self):
        if not self._serial is None:
            raise ProgrammerError('BusPirate is already started.')

        self._serial = serial.Serial(self.device, 115200)
        self.timeout = self._timeout

        self.read(timeout=.1)
        self._write(b'\x0f') # Reset BusPirate if in binary mode
        self._write(b'\n\n') # Ensure no ASCII menu is launched
        time.sleep(.1)
        self.read()
        self._write(bytes(20)) # Enter binary mode: \x00 * 20
        data = self.read(5)
        if b'BBIO' in data:
            logger.info('BusPirate in binary mode v{}'.format(chr(data[4])))
        else:
            logger.info(data)
            err = ProgrammerError('BusPirate not responding.')
            logger.error(err)
            raise err

        self._write(b'\x03')  # Enter UART mode
        data = self.read(4)
        if b'ART' in data:
            logger.info('BusPirate in UART mode v{}'.format(chr(data[3])))
        else:
            logger.info(data)
            err = ProgrammerError('BusPirate not responding.')
            logger.error(err)
            raise err

        self._write(bytes((self.UART_SPEED_CMD | self.UART_BAUD_115200,)))
        data = self.read(1)

        self._write(bytes((0b10000 | self.UART_CONFIG_CMD,)))
        data = self.read(1)

        self.set_pullup(True)
        self.set_power(True)
        self._set_pinstate(self.UART_AUX_PIN & self.UART_CS_PIN, True)

    def enter_isp_mode(self):
        # Set both pin to LOW
        self._set_pinstate(self.UART_AUX_PIN & self.UART_CS_PIN, False)

        time.sleep(.1)
        # Set RESET to HIGH
        self.set_aux_pin(True)

        time.sleep(.1)
        # Set BOOT to HIGH
        self.set_cs_pin(True)

    def post_isp_mode(self):
        self._write(bytes((self.UART_START_ECHO_CMD,)))
        data = self.read(1)

        if self.bridge_mode == True:
            self._write(bytes((self.UART_BRIDGE_CMD,)))
            data = self.read(1)
            self._bridge_mode = True
            logger.info('Bridge mode active. You will need to'
                    ' unplug/plug your BusPirate to reset it.')

    def post_prog(self):
        if not self._bridge_mode:
            self.set_aux_pin(False)
            time.sleep(.1)
            self.set_aux_pin(True)
            self._write(b'x\00'*20)
        else:
            logger.warn('Bridge mode active. Unplug/plug your'
                    ' BusPirate to reset it.')

    def set_aux_pin(self, state):
        if not self._set_pinstate(self.UART_AUX_PIN, state):
            raise ProgrammerError('Error while setting AUX pin')

    def set_cs_pin(self, state):
        if not self._set_pinstate(self.UART_CS_PIN, state):
            raise ProgrammerError('Error while setting CS pin')

    def set_power(self, state):
        if not self._set_pinstate(self.UART_POWER, state):
            raise ProgrammerError('Error while setting power')

    def set_pullup(self, state):
        if not self._set_pinstate(self.UART_PULLUP, state):
            raise ProgrammerError('Error while setting pullups')

    def _set_pinstate(self, pin, state):
        if state:
            self._pinstate |= pin
        else:
            self._pinstate &= ~pin

        self._write(bytes((self._pinstate | self.UART_PINSET_CMD,)))
        data = self.read(1)
        if data[0] == 1:
            return True
        return False


    def read(self, size=None, timeout=None):
        if timeout:
            ot = self._serial.timeout
            self._serial.timeout = timeout

        data = self._serial.read(size or self._serial.in_waiting)

        if timeout:
            self._serial.timeout = ot

        return data

    def write(self, data, **kwargs):
        if not self._bridge_mode:
            written = self.bulk_write(data, **kwargs)
        else:
            return super().write(data)

    def _write(self, data):
        return super().write(data)

    def bulk_write(self, data, ignore_reply=True):
        data_len = len(data)
        if data_len <= 0:
            raise ValueError('Data length must be >= 1')
        if data_len >= 256:
            raise ValueError('Data length must be <= 256')

        data_cmd = bytes((self.UART_BULK_CMD | (data_len - 1),))
        data_cmd += data

        written_bytes = self._write(data_cmd)

        if ignore_reply:
            rtn = self.read(data_len + 1, timeout=1)
        else:
            self.read(1)
        time.sleep(.1)
        return written_bytes
