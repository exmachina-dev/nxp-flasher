#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Benoit Rapidel <benoit.rapidel+devs@exmachina.fr>
#
# Distributed under terms of the MIT license.

"""

"""

from .abstract import ProgrammerError
from .buspirate import BusPirate
from .serial import SerialProgrammer

programmers = {
        'serial': SerialProgrammer,
        'buspirate': BusPirate,
        }

def find_programmer(name):
    if name.lower() in programmers:
        return programmers[name.lower()]

    raise ValueError('Programmer {} no found'.format(name))
