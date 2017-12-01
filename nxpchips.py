#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Benoit Rapidel <benoit.rapidel+devs@exmachina.fr>
#
# Distributed under terms of the MIT license.

"""
Holds NXP chips parameters
"""

class NXPchip(object):
    FLASH_SECTORS = {
            'lpc23xx': (                # lpc23xx/lpc24xx/lpc214x processors
                4,  4,  4,  4,  4,  4,  4,  4,
                32, 32, 32, 32, 32, 32, 32,
                32, 32, 32, 32, 32, 32, 32,
                4,  4,  4,  4,  4,  4
                ),
            'lpc21xx_64': (             # 64k lpc21xx processors (without bootsector)
                8,  8,  8,  8,  8,  8,  8,  8
                ),
            'lpc21xx_128': (            # 128k lpc21xx processors (without bootsector)
                8,  8,  8,  8,  8,  8,  8,  8,
                8,  8,  8,  8,  8,  8,  8
                ),
            'lpc21xx_256': (            # 256k lpc21xx processors (without bootsector)
                8,  8,  8,  8,  8,  8,  8,  8,
                64, 64,
                8,  8,  8,  8,  8,  8,  8,
                ),
            'lpc17xx': (                # lpc17xx processors
                4,  4,  4,  4,  4,  4,  4,  4,
                4,  4,  4,  4,  4,  4,  4,  4,
                32, 32, 32, 32, 32, 32, 32,
                32, 32, 32, 32, 32, 32, 32,
                ),
            'lpc11xx': (                # lpc11xx processors
                4,  4,  4,  4,  4,  4,  4,  4,
                ),
            'lpc18xx': (                # lpc18xx processors
                8,  8,  8,  8,  8,  8,  8,  8,
                64, 64, 64, 64, 64, 64, 64,
                ),
            }

    CPUS = {
            # 128k flash
            "lpc2364" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "flash_sector_count": 11,
                "devid": 369162498
                },
            # 256k flash
            "lpc2365" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "flash_sector_count": 15,
                "devid": 369158179
                },
            "lpc2366" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "flash_sector_count": 15,
                "devid": 369162531
                },
            # 512k flash
            "lpc2367" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "devid": 369158181
                },
            "lpc2368" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "devid": 369162533
                },
            "lpc2377" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "devid": 385935397
                },
            "lpc2378" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "devid": 385940773
                },
            "lpc2387" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "devid": 402716981

                },
            "lpc2388" : {
                "flash_sector" : FLASH_SECTORS['lpc23xx'],
                "devid": 402718517
                },
            # lpc21xx
            # some incomplete info here need at least sector count
            "lpc2141": {
                "devid": 196353,
                "flash_sector": FLASH_SECTORS['lpc23xx'],
                "flash_sector_count": 8,
                },
            "lpc2142": {
                    "flash_sector": FLASH_SECTORS['lpc23xx'],
                    "flash_sector_count": 9,
                    "devid": 196369,
                    },
            "lpc2144": {
                    "flash_sector": FLASH_SECTORS['lpc23xx'],
                    "flash_sector_count": 11,
                    "devid": 196370,
                    },
            "lpc2146": {
                    "flash_sector": FLASH_SECTORS['lpc23xx'],
                    "flash_sector_count": 15,
                    "devid": 196387,
                    },
            "lpc2148": {
                    "flash_sector": FLASH_SECTORS['lpc23xx'],
                    "flash_sector_count": 27,
                    "devid": 196389,
                    },
            "lpc2109" : {
                    "flash_sector": FLASH_SECTORS['lpc21xx_64'],
                    "devid": 33685249
                    },
            "lpc2119" : {
                    "flash_sector": FLASH_SECTORS['lpc21xx_128'],
                    "devid": 33685266
                    },
            "lpc2129" : {
                    "flash_sector": FLASH_SECTORS['lpc21xx_256'],
                    "devid": 33685267
                    },
            "lpc2114" : {
                    "flash_sector" : FLASH_SECTORS['lpc21xx_128'],
                    "devid": 16908050
                    },
            "lpc2124" : {
                    "flash_sector" : FLASH_SECTORS['lpc21xx_256'],
                    "devid": 16908051
                    },
            "lpc2194" : {
                    "flash_sector" : FLASH_SECTORS['lpc21xx_256'],
                    "devid": 50462483
                    },
            "lpc2292" : {
                    "flash_sector" : FLASH_SECTORS['lpc21xx_256'],
                    "devid": 67239699
                    },
            "lpc2294" : {
                    "flash_sector" : FLASH_SECTORS['lpc21xx_256'],
                    "devid": 84016915
                    },
            # lpc22xx
            "lpc2212" : {
                    "flash_sector" : FLASH_SECTORS['lpc21xx_128']
                    },
            "lpc2214" : {
                    "flash_sector" : FLASH_SECTORS['lpc21xx_256']
                    },
            # lpc24xx
            "lpc2458" : {
                    "flash_sector" : FLASH_SECTORS['lpc23xx'],
                    "devid": 352386869,
                    },
            "lpc2468" : {
                    "flash_sector" : FLASH_SECTORS['lpc23xx'],
                    "devid": 369164085,
                    },
            "lpc2478" : {
                    "flash_sector" : FLASH_SECTORS['lpc23xx'],
                    "devid": 386006837,
                    },
            # lpc17xx
            "lpc1768" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26013f37,
                    "cpu_type": "thumb",
                    },
            "lpc1766" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26013f33,
                    "cpu_type": "thumb",
                    },
            "lpc1765" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26013733,
                    "cpu_type": "thumb",
                    },
            "lpc1764" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26011922,
                    "cpu_type": "thumb",
                    },
            "lpc1758" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26013f34,
                    "cpu_type": "thumb",
                    },
            "lpc1756" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26011723,
                    "cpu_type": "thumb",
                    },
            "lpc1754" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26011722,
                    "cpu_type": "thumb",
                    },
            "lpc1752" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26001121,
                    "cpu_type": "thumb",
                    },
            "lpc1751" : {
                    "flash_sector" : FLASH_SECTORS['lpc17xx'],
                    "flash_prog_buffer_base" : 0x10001000,
                    "csum_vec": 7,
                    "devid": 0x26001110,
                    "cpu_type": "thumb",
                    },
            "lpc1114" : {
                    "flash_sector" : FLASH_SECTORS['lpc11xx'],
                    "flash_prog_buffer_base" : 0x10000400,
                    "devid": 0x0444102B,
                    "flash_prog_buffer_size" : 1024
                    },
            # lpc18xx
            "lpc1817" : {
                    "flash_sector" : FLASH_SECTORS['lpc18xx'],
                    "flash_bank_addr": (0x1a000000, 0x1b000000),
                    "flash_prog_buffer_base" : 0x10081000,
                    "devid": (0xF001DB3F, 0),
                    "csum_vec": 7,
                    "cpu_type": "thumb",
                    },
            "lpc1832" : {
                    "flash_sector" : FLASH_SECTORS['lpc18xx'],
                    "flash_bank_addr": (0x1a000000),
                    "flash_prog_buffer_base" : 0x10081000,
                    "csum_vec": 7,
                    "cpu_type": "thumb",
                    },
            "lpc1833" : {
                    "flash_sector" : FLASH_SECTORS['lpc18xx'],
                    "flash_sector_count": 11,
                    "flash_bank_addr": (0x1a000000, 0x1b000000),
                    "flash_prog_buffer_base" : 0x10081000,
                    "devid": (0xf001da30, 0x44),
                    "csum_vec": 7,
                    "cpu_type": "thumb",
                    },
            "lpc1837" : {
                    "flash_sector" : FLASH_SECTORS['lpc18xx'],
                    "flash_bank_addr": (0x1a000000, 0x1b000000),
                    "flash_prog_buffer_base" : 0x10081000,
                    "devid": (0xf001da30, 0),
                    "csum_vec": 7,
                    "cpu_type": "thumb",
                    },
            "lpc1853" : {
                    "flash_sector" : FLASH_SECTORS['lpc18xx'],
                    "flash_sector_count": 11,
                    "flash_bank_addr": (0x1a000000, 0x1b000000),
                    "flash_prog_buffer_base" : 0x10081000,
                    "devid": (0xf001d830, 0),
                    "csum_vec": 7,
                    "cpu_type": "thumb",
                    },
            "lpc1857" : {
                    "flash_sector" : FLASH_SECTORS['lpc18xx'],
                    "flash_bank_addr": (0x1a000000, 0x1b000000),
                    "flash_prog_buffer_base" : 0x10081000,
                    "devid": (0xf001d830, 0x44),
                    "csum_vec": 7,
                    "cpu_type": "thumb",
                    },
        }


    def __init__(self, cpu):
        if cpu not in self.CPUS:
            raise ValueError('Unknown CPU: {}'.format(cpu))

        self._cpu = cpu

    def get_parameter(self, key, default=None):
        if not self.CPUS[self._cpu]:
            raise ValueError('No parameters defined for {}'.format(self._cpu))

        return self.CPUS[self._cpu].get(key, default)

    @property
    def name(self):
        return str(self._cpu)
