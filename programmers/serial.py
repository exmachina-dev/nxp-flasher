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



class SerialProgrammer(AbstractProgrammer):
    def __init__(self, device, baudrate, *args, **kwargs):
        self.logger = logging.getLogger('NXPprog.%s' % (self.__class__.__name__))
        super().__init__(self, *args, **kwargs)
        self.device, self.baudrate = device, baudrate
        self._serial = None
        self._timeout = 1

    def init_device(self):
        if not self._serial is None:
            raise ProgrammerError('SerialProgrammer is already started.')

        self._serial = serial.Serial(self.device, self.baudrate)
        self.timeout = self._timeout

    def enter_isp_mode(self):
        self.logger.warn("Serial cannot control ISP mode.")
        self.logger.warn("Press both BOOT and RESET buttons.")
        time.sleep(2)
        self.logger.warn("Release RESET button.")
        time.sleep(2)
        self.logger.warn("Release BOOT button.")

    def post_prog(self):
        self.logger.warn('Please reset the board manually.')

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
        if self._serial:
            return self._serial.timeout
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        if self._serial:
            self._serial.timeout = timeout
            self.logger.info('Timeout set to {}s'.format(timeout))
        else:
            self._timeout = timeout
