#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Benoit Rapidel <benoit.rapidel+devs@exmachina.fr>
#
# Distributed under terms of the MIT license.

"""

"""

class AbstractProgrammer(object):
    def __init__(self, *args, **kwargs):
        self.data_buffer = b''

    def init_device(self):
        raise NotImplementedError()

    def enter_isp_mode(self):
        raise NotImplementedError()

    def post_isp_mode(self):
        pass

    def post_prog(self):
        pass

    def read(self, size=None):
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()

    def data_available(self):
        return self.in_waiting

    def readline(self, timeout=None, strip_end=True):
        line = b''
        while 1:
            self.data_buffer += self.read(self.in_waiting or 1, timeout=timeout)
            if not self.data_buffer:
                break

            line = self.find_line()
            if line:
                break
        try:
            if strip_end:
                line = line.rstrip(b'\r\n')
            return line.decode()
        except UnicodeDecodeError:
            return line

    def find_line(self):
        pos = self.data_buffer.find(b'\n')
        if pos >= 0:
            line, self.data_buffer = self.data_buffer[:pos+1], \
                self.data_buffer[pos+1:]
            return line

    def writeline(self, data, **kwargs):
        return self.write(data + b'\n', **kwargs)

    writeln = writeline


class ProgrammerError(Exception):
    pass
