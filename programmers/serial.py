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

from .abstract import AbstractProgrammer
from .abstract import ProgrammerError

logger = logging.getLogger('NXPprog.SerialProgrammer')


class SerialProgrammer(AbstractProgrammer):
    def __init__(self, device, baudrate, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.device, self.baudrate = device, baudrate
        self._serial = None

    def init_device(self):
        if not self._serial is None:
            raise ProgrammerError('SerialProgrammer is already started.')

        self._serial = serial.Serial(self.device, self.baudrate)

    def enter_isp_mode(self):
        logger.warn("Serial cannot control ISP mode.")
        logger.warn("Press both BOOT and RESET buttons.")
        time.sleep(2)
        logger.warn("Release RESET button.")
        time.sleep(2)
        logger.warn("Release BOOT button.")

    def post_isp_mode(self):
        self._write(bytes((self.UART_START_ECHO_CMD,)))
        data = self.read(1)
        print('RX: {:b}'.format(data[0]))

        if self.bridge_mode == True:
            self._write(bytes((self.UART_BRIDGE_CMD,)))
            data = self.read(1)
            print('BRIDGE: {:b}'.format(data[0]))
            self._bridge_mode = True
            logger.info('Bridge mode active. You will need to'
                    ' unplug/plug your BusPirate to reset it.')

    def post_prog(self):
        logger.warn('Please reset the board manually.')

    def read(self, size=None, timeout=None):
        if timeout:
            ot = self._serial.timeout
            self._serial.timeout = timeout

        data = self._serial.read(size or self._serial.in_waiting)

        if timeout:
            self._serial.timeout = ot

        return data

    def write(self, data, **kwargs):
        return self._serial.write(data)

    @property
    def in_waiting(self):
        return self._serial.in_waiting

    @property
    def timeout(self):
        return self._serial.timeout

    @timeout.setter
    def timeout(self, timeout):
        self._serial.timeout = timeout
        logger.info('Timeout set to {}s'.format(timeout))
