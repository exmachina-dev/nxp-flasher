#!/usr/bin/python3
#
# Copyright (c) 2009 Brian Murphy <brian@murphy.dk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# A simple programmer which works with the ISP protocol on NXP LPC arm
# processors.

import binascii
import sys
import struct
import getopt
import serial # pyserial
import time

import ihex

# flash sector sizes for lpc23xx/lpc24xx/lpc214x processors
flash_sector_lpc23xx = (
                        4, 4, 4, 4, 4, 4, 4, 4,
                        32, 32, 32, 32, 32, 32, 32,
                        32, 32, 32, 32, 32, 32, 32,
                        4, 4, 4, 4, 4, 4
                       )

# flash sector sizes for 64k lpc21xx processors (without bootsector)
flash_sector_lpc21xx_64 = (
                            8, 8, 8, 8, 8, 8, 8, 8
                           )

# flash sector sizes for 128k lpc21xx processors (without bootsector)
flash_sector_lpc21xx_128 = (
                            8, 8, 8, 8, 8, 8, 8, 8,
                            8, 8, 8, 8, 8, 8, 8
                           )

# flash sector sizes for 256k lpc21xx processors (without bootsector)
flash_sector_lpc21xx_256 = (
                            8, 8, 8, 8, 8, 8, 8, 8,
                            64, 64,
                            8, 8, 8, 8, 8, 8, 8,
                           )

# flash sector sizes for lpc17xx processors
flash_sector_lpc17xx = (
                        4, 4, 4, 4, 4, 4, 4, 4,
                        4, 4, 4, 4, 4, 4, 4, 4,
                        32, 32, 32, 32, 32, 32, 32,
                        32, 32, 32, 32, 32, 32, 32,
                       )

# flash sector sizes for lpc11xx processors
flash_sector_lpc11xx = (
        4, 4, 4, 4, 4, 4, 4, 4,
        )

# flash sector sizes for lpc18xx processors
flash_sector_lpc18xx = (
                        8, 8, 8, 8, 8, 8, 8, 8,
                        64, 64, 64, 64, 64, 64, 64,
                       )


flash_prog_buffer_base_default = 0x40001000
flash_prog_buffer_size_default = 4096

# cpu parameter table
cpu_parms = {
        # 128k flash
        "lpc2364" : {
            "flash_sector" : flash_sector_lpc23xx,
            "flash_sector_count": 11,
            "devid": 369162498
        },
        # 256k flash
        "lpc2365" : {
            "flash_sector" : flash_sector_lpc23xx,
            "flash_sector_count": 15,
            "devid": 369158179
        },
        "lpc2366" : {
            "flash_sector" : flash_sector_lpc23xx,
            "flash_sector_count": 15,
            "devid": 369162531
        },
        # 512k flash
        "lpc2367" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 369158181
        },
        "lpc2368" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 369162533
        },
        "lpc2377" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 385935397
        },
        "lpc2378" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 385940773
        },
        "lpc2387" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 402716981

        },
        "lpc2388" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 402718517
        },
        # lpc21xx
        # some incomplete info here need at least sector count
        "lpc2141": {
            "devid": 196353,
            "flash_sector": flash_sector_lpc23xx,
            "flash_sector_count": 8,
        },
        "lpc2142": {
            "flash_sector": flash_sector_lpc23xx,
            "flash_sector_count": 9,
            "devid": 196369,
        },
        "lpc2144": {
            "flash_sector": flash_sector_lpc23xx,
            "flash_sector_count": 11,
            "devid": 196370,
        },
        "lpc2146": {
            "flash_sector": flash_sector_lpc23xx,
            "flash_sector_count": 15,
            "devid": 196387,
        },
        "lpc2148": {
            "flash_sector": flash_sector_lpc23xx,
            "flash_sector_count": 27,
            "devid": 196389,
        },
        "lpc2109" : {
            "flash_sector": flash_sector_lpc21xx_64,
            "devid": 33685249
        },
        "lpc2119" : {
            "flash_sector": flash_sector_lpc21xx_128,
            "devid": 33685266
        },
        "lpc2129" : {
            "flash_sector": flash_sector_lpc21xx_256,
            "devid": 33685267
        },
        "lpc2114" : {
            "flash_sector" : flash_sector_lpc21xx_128,
            "devid": 16908050
        },
        "lpc2124" : {
            "flash_sector" : flash_sector_lpc21xx_256,
            "devid": 16908051
        },
        "lpc2194" : {
            "flash_sector" : flash_sector_lpc21xx_256,
            "devid": 50462483
        },
        "lpc2292" : {
            "flash_sector" : flash_sector_lpc21xx_256,
            "devid": 67239699
        },
        "lpc2294" : {
            "flash_sector" : flash_sector_lpc21xx_256,
            "devid": 84016915
        },
        # lpc22xx
        "lpc2212" : {
            "flash_sector" : flash_sector_lpc21xx_128
        },
        "lpc2214" : {
            "flash_sector" : flash_sector_lpc21xx_256
        },
        # lpc24xx
        "lpc2458" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 352386869,
        },
        "lpc2468" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 369164085,
        },
        "lpc2478" : {
            "flash_sector" : flash_sector_lpc23xx,
            "devid": 386006837,
        },
        # lpc17xx
        "lpc1768" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26013f37,
            "cpu_type": "thumb",
        },
        "lpc1766" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26013f33,
            "cpu_type": "thumb",
        },
        "lpc1765" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26013733,
            "cpu_type": "thumb",
        },
        "lpc1764" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26011922,
            "cpu_type": "thumb",
        },
        "lpc1758" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26013f34,
            "cpu_type": "thumb",
        },
        "lpc1756" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26011723,
            "cpu_type": "thumb",
        },
        "lpc1754" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26011722,
            "cpu_type": "thumb",
        },
        "lpc1752" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26001121,
            "cpu_type": "thumb",
        },
        "lpc1751" : {
            "flash_sector" : flash_sector_lpc17xx,
            "flash_prog_buffer_base" : 0x10001000,
            "csum_vec": 7,
            "devid": 0x26001110,
            "cpu_type": "thumb",
        },
        "lpc1114" : {
            "flash_sector" : flash_sector_lpc11xx,
            "flash_prog_buffer_base" : 0x10000400,
            "devid": 0x0444102B,
            "flash_prog_buffer_size" : 1024
        },
        # lpc18xx
        "lpc1817" : {
            "flash_sector" : flash_sector_lpc18xx,
            "flash_bank_addr": (0x1a000000, 0x1b000000),
            "flash_prog_buffer_base" : 0x10081000,
            "devid": (0xF001DB3F, 0),
            "csum_vec": 7,
            "cpu_type": "thumb",
        },
        "lpc1832" : {
            "flash_sector" : flash_sector_lpc18xx,
            "flash_bank_addr": (0x1a000000),
            "flash_prog_buffer_base" : 0x10081000,
            "csum_vec": 7,
            "cpu_type": "thumb",
        },
        "lpc1833" : {
            "flash_sector" : flash_sector_lpc18xx,
            "flash_sector_count": 11,
            "flash_bank_addr": (0x1a000000, 0x1b000000),
            "flash_prog_buffer_base" : 0x10081000,
            "devid": (0xf001da30, 0x44),
            "csum_vec": 7,
            "cpu_type": "thumb",
        },
        "lpc1837" : {
            "flash_sector" : flash_sector_lpc18xx,
            "flash_bank_addr": (0x1a000000, 0x1b000000),
            "flash_prog_buffer_base" : 0x10081000,
            "devid": (0xf001da30, 0),
            "csum_vec": 7,
            "cpu_type": "thumb",
        },
        "lpc1853" : {
            "flash_sector" : flash_sector_lpc18xx,
            "flash_sector_count": 11,
            "flash_bank_addr": (0x1a000000, 0x1b000000),
            "flash_prog_buffer_base" : 0x10081000,
            "devid": (0xf001d830, 0),
            "csum_vec": 7,
            "cpu_type": "thumb",
        },
        "lpc1857" : {
            "flash_sector" : flash_sector_lpc18xx,
            "flash_bank_addr": (0x1a000000, 0x1b000000),
            "flash_prog_buffer_base" : 0x10081000,
            "devid": (0xf001d830, 0x44),
            "csum_vec": 7,
            "cpu_type": "thumb",
        },
}


def log(str):
    sys.stderr.write("%s\n" % str)

def dump(name, str):
    sys.stderr.write("%s:\n" % name)
    ct = 0
    for i in str:
        sys.stderr.write("%x, " % ord(i))
        ct += 1
        if ct == 4:
            ct = 0
            sys.stderr.write("\n")
    sys.stderr.write("\n")


def panic(str):
    log(str)
    sys.exit(1)


def syntax():
    panic(
"""{0} <serial device> <image_file> : program image file to processor.
{0} --start=<addr> <serial device> : start the device at <addr>
{0} --read=<file> --addr=<address> --len=<length>:
            read length bytes from address and dump them to a file
{0} --list : list supported processors.
options:
    --cpu=<cpu> : set the cpu type.
    --oscfreq=<freq> : set the oscillator frequency.
    --baud=<baud> : set the baud rate.
    --xonxoff : enable xonxoff flow control.
    --control : use RTS and DTR to control reset and int0.
    --addr=<image start address> : set the base address for the image.
    --eraseonly : don't program, just erase. Implies --eraseall.
    --eraseall : erase all flash not just the area written to.
    --filetype=[ihex|bin]: set filetype to intel hex format or raw binary
    --bank=[0|1]: select bank for devices with flash banks
""".format(sys.argv[0]))

class nxpprog:
    def __init__(self, cpu, device, baud, osc_freq, xonxoff = 0, control = 0):
        self.echo_on = 1
        self.OK = 'OK'
        self.RESEND = 'RESEND'
        self.sync_str = 'Synchronized'

        # for calculations in 32 bit modulo arithmetic
        self.U32_MOD = (2 ** 32)

        # uuencoded line length
        self.uu_line_size = 45
        # uuencoded block length
        self.uu_block_size = self.uu_line_size * 20

        self.serdev = serial.Serial(device, baud)

        # set a two second timeout just in case there is nothing connected
        # or the device is in the wrong mode.
        # This timeout is too short for slow baud rates but who wants to
        # use them?
        self.serdev.timeout = 5
        # device wants Xon Xoff flow control
        if xonxoff:
            self.serdev.xonxoff = 1

        self.cpu = cpu

        # reset pin is controlled by DTR implying int0 is controlled by RTS
        self.reset_pin = "dtr"

        if control:
            self.isp_mode()

        self.serdev.reset_input_buffer()

        self.connection_init(osc_freq)

        self.banks = self.get_cpu_parm("flash_bank_addr", 0)

        if self.banks == 0:
            self.sector_commands_need_bank = 0
        else:
            self.sector_commands_need_bank = 1

    # put the chip in isp mode by resetting it using RTS and DTR signals
    # this is of course only possible if the signals are connected in
    # this way
    def isp_mode(self):
        self.reset(0)
        time.sleep(.1)
        self.reset(1)
        self.int0(1)
        time.sleep(.1)
        self.reset(0)
        time.sleep(.1)
        self.int0(0)

    def reset(self, level):
        if self.reset_pin == "rts":
            self.serdev.rts = level
        else:
            self.serdev.dtr = level

    def int0(self, level):
        # if reset pin is rts int0 pin is dtr
        if self.reset_pin == "rts":
            self.serdev.dtr = level
        else:
            self.serdev.rts = level

    def connection_init(self, osc_freq):
        self.sync(osc_freq)

        if self.cpu == "autodetect":
            devid = self.get_devid()
            for dcpu in cpu_parms.keys():
                cpu_devid = cpu_parms[dcpu].get("devid")
                if not cpu_devid:
                    continue
                if devid == cpu_devid:
                    log("detected %s" % dcpu)
                    self.cpu = dcpu
                    break
            if self.cpu == "autodetect":
                panic("Cannot autodetect from device id %d(0x%x), set cpu name manually" %
                        (devid, devid))

        # unlock write commands
        self.isp_command("U 23130")


    def dev_write(self, data):
        self.serdev.write(data)

    def dev_writeln(self, data):
        self.serdev.write(bytes(data, 'UTF-8'))
        self.serdev.write(b'\r\n')

    def dev_readline(self, timeout=None):
        if timeout:
            ot = self.serdev.timeout
            self.serdev.timeout = timeout

        line = b''
        while 1:
            c = self.serdev.read(1)
            if not c:
                break
            if c == b'\r':
                continue
            if c == b'\n':
                if not line:
                    continue
                else:
                    break
            line += c

        if timeout:
            self.serdev.timeout = ot

        return line.decode("UTF-8")

    def errexit(self, str, status):
        if not status:
            panic("%s: timeout" % str)
        err = int(status)
        if err != 0:
            panic("%s: %d" % (str, err))


    def isp_command(self, cmd):
        self.dev_writeln(cmd)

        # throw away echo data
        if self.echo_on:
            self.dev_readline()

        status = self.dev_readline()
        self.errexit("'%s' error" % cmd, status)


    def sync(self, osc):
        self.dev_write(b'?')
        s = self.dev_readline()
        if not s:
            panic("sync timeout")
        if s != self.sync_str:
            panic("no sync string")

        self.dev_writeln(self.sync_str)
        # recieve our echoed data
        s = self.dev_readline()
        if s != self.sync_str:
            panic("no sync string")

        s = self.dev_readline()
        if s != self.OK:
            panic("not ok")

        self.dev_writeln('%d' % osc)
        # discard echo
        s = self.dev_readline()
        s = self.dev_readline()
        if s != self.OK:
            panic("osc not ok")

        self.dev_writeln('A 0')
        # discard echo
        s = self.dev_readline()
        s = self.dev_readline()
        if int(s):
            panic("echo disable failed")

        self.echo_on = 0


    def sum(self, data):
        s = 0
        for i in data:
            s += i
        return s


    def write_ram_block(self, addr, data):
        data_len = len(data)

        self.isp_command("W %d %d\n" % ( addr, data_len ))

        for i in range(0, data_len, self.uu_line_size):
            c_line_size = data_len - i
            if c_line_size > self.uu_line_size:
                c_line_size = self.uu_line_size
            block = data[i:i+c_line_size]
            bstr = binascii.b2a_uu(block)
            self.dev_write(bstr)


        self.dev_writeln('%s' % self.sum(data))
        status = self.dev_readline()
        if not status:
            return "timeout"
        if status == self.RESEND:
            return "resend"
        if status == self.OK:
            return ""

        # unknown status result
        panic(status)

    def uudecode(self, line):
        # uu encoded data has an encoded length first
        linelen = ord(line[0]) - 32

        uu_linelen = (linelen + 3 - 1) / 3 * 4

        if uu_linelen + 1 != len(line):
            panic("error in line length")

        # pure python implementation - if this was C we would
        # use bitshift operations here
        decoded = ""
        for i in range(1, len(line), 4):
            c = 0
            for j in line[i: i + 4]:
                ch = ord(j) - 32
                ch %= 64
                c = c * 64 + ch
            s = []
            for j in range(0, 3):
                s.append(c % 256)
                c /= 256
            for j in reversed(s):
                decoded = decoded + chr(j)

        # only return real data
        return decoded[0:linelen]


    def read_block(self, addr, data_len, fd = None):
        self.isp_command("R %d %d\n" % ( addr, data_len ))

        expected_lines = (data_len + self.uu_line_size - 1)/self.uu_line_size

        data = ""
        for i in range(0, expected_lines, 20):
            lines = expected_lines - i
            if lines > 20:
                lines = 20
            cdata = ""
            for i in range(0, lines):
                line = self.dev_readline()

                decoded = self.uudecode(line)

                cdata += decoded

            s = self.dev_readline()

            if int(s) != self.sum(cdata):
                panic("checksum mismatch on read got %x expected %x" % (int(s), self.sum(data)))
            else:
                self.dev_writeln(self.OK)

            if fd:
                fd.write(cdata)
            else:
                data += cdata

        if fd:
            return None
        else:
            return data

    def write_ram_data(self, addr, data):
        image_len = len(data)
        for i in range(0, image_len, self.uu_block_size):

            a_block_size = image_len - i
            if a_block_size > self.uu_block_size:
                a_block_size = self.uu_block_size

            err = self.write_ram_block(addr, data[i : i + a_block_size])
            if err:
                panic("write error: %s" % err)

            addr += a_block_size


    def find_flash_sector(self, addr):
        table = self.get_cpu_parm("flash_sector")
        flash_base_addr = self.get_cpu_parm("flash_bank_addr", 0)
        if not flash_base_addr:
            faddr = 0
        else:
            faddr = flash_base_addr[0] # fix to have a current flash bank
        for i in range(0, len(table)):
            n_faddr = faddr + table[i] * 1024
            if addr >= faddr and addr < n_faddr:
                return i
            faddr = n_faddr
        return -1


    def bytestr(self, ch, count):
        data = b''
        for i in range(0, count):
            data += bytes([ch])
        return data


    def insert_csum(self, orig_image):
        # make this a valid image by inserting a checksum in the correct place
        intvecs = struct.unpack("<8I", orig_image[0:32])

        # default vector is 5: 0x14, new cortex cpus use 7: 0x1c
        valid_image_csum_vec = self.get_cpu_parm("csum_vec", 5)
        # calculate the checksum over the interrupt vectors
        csum = 0
        intvecs_list = []
        for vec in range(0, len(intvecs)):
            intvecs_list.append(intvecs[vec])
            if valid_image_csum_vec == 5 or vec <= valid_image_csum_vec:
                csum = csum + intvecs[vec]
        # remove the value at the checksum location
        csum -= intvecs[valid_image_csum_vec]

        csum %= self.U32_MOD
        csum = self.U32_MOD - csum

        log("inserting intvec checksum %08x in image at offset %d" %
                (csum, valid_image_csum_vec))

        intvecs_list[valid_image_csum_vec] = csum

        image = b''
        for vecval in intvecs_list:
            image += struct.pack("<I", vecval)

        image += orig_image[32:]

        return image


    def prepare_flash_sectors(self, start_sector, end_sector):
        if self.sector_commands_need_bank:
            self.isp_command("P %d %d 0" % (start_sector, end_sector))
        else:
            self.isp_command("P %d %d" % (start_sector, end_sector))


    def erase_sectors(self, start_sector, end_sector):
        self.prepare_flash_sectors(start_sector, end_sector)

        log("erasing flash sectors %d-%d" % (start_sector, end_sector))

        if self.sector_commands_need_bank:
            self.isp_command("E %d %d 0" % (start_sector, end_sector))
        else:
            self.isp_command("E %d %d" % (start_sector, end_sector))


    def erase_flash(self, start_addr, end_addr):
        start_sector = self.find_flash_sector(start_addr)
        end_sector = self.find_flash_sector(end_addr)

        self.erase_sectors(start_sector, end_sector)


    def get_cpu_parm(self, key, default = None):
        ccpu_parms = cpu_parms.get(self.cpu)
        if not ccpu_parms:
            panic("no parameters defined for cpu %s" % self.cpu)
        parm = ccpu_parms.get(key)
        if parm:
            return parm
        if default != None:
            return default
        else:
            panic("no value for required cpu parameter %s" % key)


    def erase_all(self):
        end_sector = self.get_cpu_parm("flash_sector_count",
            len(self.get_cpu_parm("flash_sector"))) - 1

        self.erase_sectors(0, end_sector)


    def prog_image(self, image, flash_addr_base = 0,
            erase_all = 0):

        # the base address of the ram block to be written to flash
        ram_addr = self.get_cpu_parm("flash_prog_buffer_base",
                flash_prog_buffer_base_default)
        # the size of the ram block to be written to flash
        # 256 | 512 | 1024 | 4096
        ram_block = self.get_cpu_parm("flash_prog_buffer_size",
                flash_prog_buffer_size_default)

        # if the image starts at the start of a flash bank then make it bootable
        # by inserting a checksum at the right place in the vector table
        if self.banks == 0 and flash_addr_base == 0:
            image = self.insert_csum(image)
        elif flash_addr_base in self.banks:
            image = self.insert_csum(image)

        image_len = len(image)
        # pad to a multiple of ram_block size with 0xff
        pad_count_rem = image_len % ram_block
        if pad_count_rem != 0:
            pad_count = ram_block - pad_count_rem
            image += self.bytestr(0xff, pad_count)
            image_len += pad_count

        log("padding with %d bytes" % pad_count)

        if erase_all:
            self.erase_all()
        else:
            self.erase_flash(flash_addr_base, flash_addr_base + image_len)

        for image_index in range(0, image_len, ram_block):
            a_ram_block = image_len - image_index
            if a_ram_block > ram_block:
                a_ram_block = ram_block

            flash_addr_start = image_index + flash_addr_base
            flash_addr_end = flash_addr_start + a_ram_block
            progress = (image_index / image_len) * 100

            log("writing %d bytes to %6x (%3.0f%%)" % (a_ram_block, flash_addr_start, progress))

            self.write_ram_data(ram_addr,
                    image[image_index: image_index + a_ram_block])

            s_flash_sector = self.find_flash_sector(flash_addr_start)

            e_flash_sector = self.find_flash_sector(flash_addr_end)

            self.prepare_flash_sectors(s_flash_sector, e_flash_sector)

            # copy ram to flash
            self.isp_command("C %d %d %d" %
                    (flash_addr_start, ram_addr, a_ram_block))


    def start(self, addr = 0):
        mode = self.get_cpu_parm("cpu_type", "arm")
        # start image at address 0
        if mode == "arm":
            m = "A"
        elif mode == "thumb":
            m = "T"
        else:
            panic("invalid mode to start")

        self.isp_command("G %d %s" % (addr, m))


    def select_bank(self, bank):
        status = self.isp_command("S %d" % bank)

        if status == self.OK:
            return 1

        return 0


    def get_devid(self):
        self.isp_command("J")
        id1 = self.dev_readline()

        # FIXME find a way of doing this without a timeout
        id2 = self.dev_readline(.2)
        if id2:
            ret = (int(id1), int(id2))
        else:
            ret = int(id1)
        return ret


if __name__ == "__main__":
    # defaults
    osc_freq = 16000 # kHz
    baud = 115200
    cpu = "autodetect"
    flash_addr_base = 0
    erase_all = 0
    erase_only = 0
    xonxoff = 0
    start = 0
    control = 0
    filetype = "bin"
    select_bank = 0
    read = 0
    readlen = 0

    optlist, args = getopt.getopt(sys.argv[1:], '',
            ['cpu=', 'oscfreq=', 'baud=', 'addr=', 'start=',
                'filetype=', 'bank=', 'read=', 'len=',
                'xonxoff', 'eraseall', 'eraseonly', 'list', 'control'])

    for o, a in optlist:
        if o == "--list":
            log("Supported cpus:")
            for val in cpu_parms.keys():
                log(" %s" % val)
            sys.exit(0)
        if o == "--cpu":
            cpu = a
        elif o == "--xonxoff":
            xonxoff = 1
        elif o == "--oscfreq":
            osc_freq = int(a)
        elif o == "--addr":
            flash_addr_base = int(a, 0)
        elif o == "--baud":
            baud = int(a)
        elif o == "--eraseall":
            erase_all = 1
        elif o == "--eraseonly":
            erase_only = 1
        elif o == "--control":
            control = 1
        elif o == "--filetype":
            filetype = a
            if not ( filetype == "bin" or filetype == "ihex" ):
                panic("invalid filetype: %s" % filetype)
        elif o == "--start":
            start = 1
            if a:
                startaddr = int(a, 0)
            else:
                startaddr = 0
        elif o == "--bank":
            select_bank = 1
            bank = int(a)
        elif o == "--read":
            read = 1
            readfile = a
        elif o == "--len":
            readlen = int(a)
        else:
            panic("unhandled option: %s" % o)

    if cpu != "autodetect" and not cpu in cpu_parms:
        panic("unsupported cpu %s" % cpu)

    if len(args) == 0:
        syntax()

    log("cpu=%s oscfreq=%d baud=%d" % (cpu, osc_freq, baud))

    device = args[0]

    prog = nxpprog(cpu, device, baud, osc_freq, xonxoff, control)

    if erase_only:
        prog.erase_all()
    elif start:
        prog.start(startaddr)
    elif select_bank:
        prog.select_bank(bank)
    elif read:
        if not readlen:
            panic("read length is 0")
        fd = open(readfile, "w")
        prog.read_block(flash_addr_base, readlen, fd)
        fd.close()
    else:
        if len(args) != 2:
            syntax()

        filename = args[1]

        if filetype == "ihex":
            ih = ihex.ihex(filename)
            (flash_addr_base, image) = ih.flatten()
        else:
            image = open(filename, "rb").read()

        prog.prog_image(image, flash_addr_base, erase_all)

        prog.start(flash_addr_base)
