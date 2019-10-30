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
import logging
from pathlib import Path

import ihex
from nxpchips import NXPchip
from programmers import find_programmer, ProgrammerError

logger = logging.getLogger('NXPprog')
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(fmt)
logger.addHandler(ch)


class NXPprog(object):
    BAUDRATES = (9600, 19200, 38400, 57600, 115200, 230400)
    OK = 'OK'
    RESEND = 'RESEND'
    SYNC_STR = 'Synchronized'

    # for calculations in 32 bit modulo arithmetic
    U32_MOD = (2 ** 32)
    # uuencoded line length
    UU_LINE_SIZE = 45
    # uuencoded block length
    UU_BLOCK_SIZE = UU_LINE_SIZE * 20

    FLASH_BUFFER_BASE_DEFAULT = 0x40001000
    FLASH_BUFFER_SIZE_DEFAULT = 4096  # Can be 256, 512, 1024 or 4096

    def __init__(self, **kwargs):
        self.programmer = None
        self.echo_on = 1

        self.device = kwargs.pop('device')
        self.baudrate = kwargs.pop('baudrate', 115200)
        self.programmer_name = kwargs.pop('programmer', 'serial')
        self.xonxoff = kwargs.pop('xonxoff', False)
        self.control_isp_mode = kwargs.pop('control', False)

        cpu = kwargs.pop('cpu', None)
        if cpu:
            self.cpu = NXPchip(cpu)
        else:
            self.cpu = None

        self.oscfreq = kwargs.pop('oscfreq', 16000)

    def init_programmer(self):
        if self.programmer:
            raise OSError('Programmer already started')

        self.programmer = find_programmer(self.programmer_name)(self.device, self.baudrate)

        try:
            self.programmer.init_device()
        except ProgrammerError as e:
            logger.error('Could not start programmer: {!s}'.format(e))
            raise e

        # set a two second timeout just in case there is nothing connected
        # or the device is in the wrong mode.
        # This timeout is too short for slow baud rates but who wants to
        # use them?
        self.programmer.timeout = 0.3
        # device wants Xon Xoff flow control
        self.programmer.xonxoff = 1

        if self.control_isp_mode is True:
            self.programmer.enter_isp_mode()

        self.programmer.post_isp_mode()
        self.connection_init()

        self.banks = self.cpu.get_parameter("flash_bank_addr", 0)

        if self.banks == 0:
            self.sector_commands_need_bank = 0
        else:
            self.sector_commands_need_bank = 1

    def connection_init(self):
        self.sync(self.oscfreq)

        if not self.cpu:
            devid = self.get_devid()
            for dcpu in NXPchip.CPUS.keys():
                cpu_devid = NXPchip.CPUS[dcpu].get("devid")
                if not cpu_devid:
                    continue
                if devid == cpu_devid:
                    logger.info("Chip detected: %s" % dcpu.upper())
                    self.cpu = NXPchip(dcpu)
                    break
            if not self.cpu:
                logger.error("Cannot autodetect from device id %d(0x%x), set cpu name manually" %
                        (devid, devid))

        # unlock write commands
        self.isp_command("U 23130")


    def isp_command(self, cmd):
        self.programmer.writeln(cmd.encode())

        # throw away echo data
        if self.echo_on:
            self.programmer.readline()

        status = self.programmer.readline()
        if int(status) != 0:
            logger.error('Error with {!r} command: {}'.format(cmd, status))
            sys.exit(1)


    def sync(self, osc):
        self.programmer.write(b'?')
        s = self.programmer.readline()
        if not s:
            if self.cpu is not None:
                logger.error("Sync timeout. Is the {} chip powered?".format(self.cpu))
            else:
                logger.error("Sync timeout. Is the chip powered?")
            sys.exit(1)
        if s != self.SYNC_STR:
            logger.error("No sync string read (got {}, expected {})".format(s, self.SYNC_STR))
            sys.exit(1)

        self.programmer.writeln(self.SYNC_STR.encode())
        s = self.programmer.readline()
        if s != self.SYNC_STR:
            logger.error("No sync string read (got {}, expected {})".format(s, self.SYNC_STR))
            sys.exit(1)

        s = self.programmer.readline()
        if s != self.OK:
            logger.error("No OK string read (got {}, expected {})".format(s, self.OK))
            sys.exit(1)

        self.programmer.writeln(b'%d' % osc)
        # discard echo
        s = self.programmer.readline()
        s = self.programmer.readline()
        if s != self.OK:
            logger.error("No OK string read while setting OSC (got {}, expected {})".format(s, self.OK))
            sys.exit(1)

        self.programmer.writeln('A 0'.encode())
        # discard echo
        s = self.programmer.readline()
        s = self.programmer.readline()
        if int(s):
            logger.warn("Disabling echo failed")

        self.echo_on = 0


    def sum(self, data):
        s = 0
        for i in data:
            s += int(i)
        return s


    def write_ram_block(self, addr, data):
        data_len = len(data)

        self.isp_command("W %d %d\n" % ( addr, data_len ))

        for i in range(0, data_len, self.UU_LINE_SIZE):
            c_line_size = data_len - i
            if c_line_size > self.UU_LINE_SIZE:
                c_line_size = self.UU_LINE_SIZE
            block = data[i:i+c_line_size]
            bstr = binascii.b2a_uu(block)
            self.programmer.write(bstr)


        self.programmer.writeln(('%s' % self.sum(data)).encode())
        status = self.programmer.readline()
        if not status:
            return "timeout"
        if status == self.RESEND:
            return "resend"
        if status == self.OK:
            return ""

        logger.error('Unknown status: {}'.format(status))
        sys.exit(1)

    def uudecode(self, line):
        try:
            return binascii.a2b_uu(line)
        except binascii.Error:
            nbytes = (((ord(line[0])-32) & 63) * 4 + 5) // 3
            return binascii.a2b_uu(line[:nbytes])

    def read_serialnumber(self):
        sn = ['0x%x' % x for x in self.get_devsn()]
        logger.info('Device S/N: %s', ' '.join(sn))

    def read_block(self, addr, data_len, fd=None):
        if data_len % 4:
            logger.error("Data length must be a multiple of 4")
            sys.exit(1)
        self.isp_command("R %d %d\n" % ( addr, data_len ))

        expected_lines = int(data_len / (self.UU_LINE_SIZE - 1))

        data = b""
        remaining_data_len = data_len
        current_addr = addr
        for i in range(0, expected_lines, 20):
            lines = expected_lines - i
            if lines > 20:
                lines = 20
            cdata = b""
            data_read_len = 0
            for i in range(0, lines):
                line = self.programmer.readline(timeout=0.5)
                try:
                    decoded = self.uudecode(line)
                except binascii.Error as e:
                    logger.warn("Could no decode line: %s", str(e))
                remaining_data_len -= len(decoded)
                data_read_len += len(decoded)
                cdata += decoded

            s = self.programmer.readline()

            if int(s) != self.sum(cdata):
                logger.error("Checksum mismatch on read got %x expected %x. Retrying.",
                             int(s), self.sum(data))
                sys.exit(1)
            else:
                self.programmer.writeln(self.OK.encode())

            progress = (remaining_data_len / data_len) * 100
            logger.info('Read %d bytes at 0x%-6x    (%3.0f%%)',
                        data_read_len, current_addr, 100-progress)
            current_addr += data_read_len

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
        for i in range(0, image_len, self.UU_BLOCK_SIZE):

            a_block_size = image_len - i
            if a_block_size > self.UU_BLOCK_SIZE:
                a_block_size = self.UU_BLOCK_SIZE

            err = self.write_ram_block(addr, data[i : i + a_block_size])
            if err:
                logger.error("Write error: %s", err)
                sys.exit(1)

            addr += a_block_size

    def find_flash_sector(self, addr):
        table = self.cpu.get_parameter("flash_sector")
        flash_base_addr = self.cpu.get_parameter("flash_bank_addr", 0)

        faddr = 0
        if flash_base_addr:
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
        valid_image_csum_vec = self.cpu.get_parameter("csum_vec", 5)
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

        logger.info("Inserting intvec checksum %08x in image at offset %d",
                csum, valid_image_csum_vec)

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

        logger.info("Erasing flash sectors %d-%d", start_sector, end_sector)

        if self.sector_commands_need_bank:
            self.isp_command("E %d %d 0" % (start_sector, end_sector))
        else:
            self.isp_command("E %d %d" % (start_sector, end_sector))

    def erase_flash(self, start_addr, end_addr):
        start_sector = self.find_flash_sector(start_addr)
        end_sector = self.find_flash_sector(end_addr)

        self.erase_sectors(start_sector, end_sector)

    def erase_all(self):
        end_sector = self.cpu.get_parameter("flash_sector_count",
            len(self.cpu.get_parameter("flash_sector"))) - 1

        self.erase_sectors(0, end_sector)

    def prog_image(self, image, flash_addr_base=None, erase_all=False):
        self.read_serialnumber()

        if flash_addr_base is None:
            flash_addr_base = 0

        # the base address of the ram block to be written to flash
        ram_addr = self.cpu.get_parameter("flash_prog_buffer_base",
                self.FLASH_BUFFER_BASE_DEFAULT)
        # the size of the ram block to be written to flash
        # 256 | 512 | 1024 | 4096
        ram_block = self.cpu.get_parameter("flash_prog_buffer_size",
                self.FLASH_BUFFER_SIZE_DEFAULT)

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

        logger.info("Padding with %d bytes" % pad_count)

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
            image_index_stop = (image_index + a_ram_block)

            self.write_ram_data(ram_addr,
                    image[image_index: image_index + a_ram_block])

            s_flash_sector = self.find_flash_sector(flash_addr_start)

            e_flash_sector = self.find_flash_sector(flash_addr_end)

            self.prepare_flash_sectors(s_flash_sector, e_flash_sector)

            # copy ram to flash
            self.isp_command("C %d %d %d" %
                    (flash_addr_start, ram_addr, a_ram_block))

            left_KB = (image_len - image_index_stop) / 1024
            written_KB = a_ram_block/1024
            progress = (image_index_stop / image_len) * 100
            logger.info('Writted %dKB to 0x%-6x    %3dKB left (%3.0f%%)',
                    written_KB, flash_addr_start, left_KB, progress)

        logger.info('Image written to flash')

    def start(self, addr=None):
        addr = addr or 0
        mode = self.cpu.get_parameter("cpu_type", "arm")
        # start image at address 0
        if mode == "arm":
            m = "A"
        elif mode == "thumb":
            m = "T"
        else:
            logger.error("Invalid mode to start: {}".format(mode))
            sys.exit(1)

        self.isp_command("G %d %s" % (addr, m))
        logger.info('Starting chip at 0x%x', addr)


    def select_bank(self, bank):
        status = self.isp_command("S %d" % bank)

        if status == self.OK:
            return 1

        return 0

    def get_devid(self):
        self.isp_command("J")
        id1 = self.programmer.readline()

        # FIXME find a way of doing this without a timeout
        id2 = self.programmer.readline(.2)
        if id2:
            ret = (int(id1), int(id2))
        else:
            ret = int(id1)
        return ret

    def get_devsn(self):
        self.isp_command("N")
        ret = list()
        for i in range(4):
            ret.append(int(self.programmer.readline(.2), 0))

        return ret

    def finalize(self):
        self.programmer.post_prog()

    def readline(self, *args, **kwargs):
        if self.programmer.data_available():
            return self.programmer.read(size=self.programmer.data_available(), **kwargs)


if __name__ == "__main__":
    import argparse

    import sys
    if sys.version_info[0] < 3:
        raise RuntimeError('Only python 3 and later are supported')

    parser = argparse.ArgumentParser(description='Flasher for NXP chips')

    parser.add_argument('device', metavar='SERIAL_DEVICE',
            help='Device to flash')
    parser.add_argument('image_file', metavar='IMAGE', nargs='?',
            help='Image file')

    actions_group = parser.add_mutually_exclusive_group()
    actions_group.add_argument('--list', '-l', action='store_true',
            help='List supported chips and exit')
    actions_group.add_argument('--read', '-r', action='store_true',
            help='Read the data on the chip')
    actions_group.add_argument('--start', '-s', type=int, default=None,
            help='Set the start address of the chip')
    actions_group.add_argument('--eraseonly', '-e', action='store_true',
            help='Don\'t program, just erase. Implies --eraseall')
    actions_group.add_argument('--selectbank', type=int, choices=(0, 1),
            help='Select bank for devices with flash banks')
    actions_group.add_argument('--read-serialnumber', '-S', action='store_true',
            help='Read serialnumber from connected device')

    parser.add_argument('--cpu', '-c', metavar='CPU', choices=list(NXPchip.CPUS.keys()), default=None,
            help='Specify chip')
    parser.add_argument('--baudrate', '-b', metavar='BAUD', type=int, choices=NXPprog.BAUDRATES, default=115200,
            help='Specify baudrate for communication')
    parser.add_argument('--oscfreq', type=int, default=16000,
            help='OSC Freq')
    parser.add_argument('--xonxoff', action='store_true',
            help='Enable XonXoff flow control')
    parser.add_argument('--control', action='store_true',
            help='Use RTS and DTR to control reset and int0')
    parser.add_argument('--addr', '-a', type=str, default="0",
            help='Set the base address for the image')
    parser.add_argument('--filetype', choices=('ihex', 'bin'), default='bin',
            help='Set filetype to Intel hex or raw binary')
    parser.add_argument('--eraseall', '-E', action='store_true',
            help='Erase all the flash, not just the area written to')
    parser.add_argument('--length', '-L', type=str, default="1",
            help='Specify the length to read (only usefull with --read)')
    parser.add_argument('--console', action='store_true',
            help='Keep the programmer open and output bytes on the console')

    parser.add_argument('--programmer', '-p',
            help='Connected programmer')

    args = parser.parse_args()

    if args.list:
        logger.info("Supported cpus:")
        chips = sorted(list(NXPchip.CPUS.keys()))
        while len(chips):
            c = chips[0:4]
            chips = chips[4:]
            logger.info('\t'.join([x.upper() for x in c]))

        parser.exit(0)

    if not (args.eraseonly or args.start or args.selectbank or
            args.read_serialnumber) \
            and not args.image_file:
        parser.error('argument IMAGE_FILE is required in this mode')
        parser.exit(1)

    prog = NXPprog(**vars(args))
    prog.init_programmer()

    logger.info("Initializing with cpu=%s oscfreq=%d baud=%d",
                prog.cpu.name, prog.oscfreq, prog.baudrate)

    args.addr = int(args.addr, 0) # Convert string int representation to int
                                  # This allows to accept args written in hex
                                  # and decimal representation (i.e.: 0xf or
                                  # 16)
    args.length = int(args.length, 0) # Same for length

    try:
        if args.eraseonly:
            prog.erase_all()
        elif args.start is not None:
            prog.start()
        elif args.selectbank:
            prog.select_bank(args.selectbank)
        elif args.read_serialnumber:
            prog.read_serialnumber()
        elif args.read:
            if not args.image_file:
                parser.exit(1)
            output_file = Path(args.image_file)
            if output_file.exists():
                logger.error("File already exists")
                parser.exit(1)

            logger.info("Reading %d bytes starting at 0x%-6x", args.length, args.addr)
            with open(args.image_file, "wb") as fd:
                data = prog.read_block(args.addr, args.length)
                if data:
                    fd.write(data)
                    logger.info("Data saved in %s", args.image_file)
                else:
                    logger.warn("No data could be read")
        else:
            if not args.image_file:
                parser.exit(1)

            filename = args.image_file
            input_file = Path(args.image_file)
            if not (input_file.exists() and input_file.is_file()):
                logger.error("File does not exist")
                parser.exit(1)

            if args.filetype == "ihex":
                ih = ihex.ihex(filename)
                (args.addr, image) = ih.flatten()
            else:
                with open(filename, "rb") as f:
                    image = f.read()

            prog.prog_image(image, args.addr, args.eraseall)

            prog.start(args.addr)
    finally:
        prog.finalize()

    if args.console:
        import signal
        import sys
        import time

        logger.info("Keeping serial link opened.")

        original_sigint = signal.getsignal(signal.SIGINT)
        def exit_gracefully(signum, frame):
            # restore the original signal handler as otherwise evil things will happen
            # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
            signal.signal(signal.SIGINT, original_sigint)

            try:
                if input("\nReally quit? (y/n)> ").lower().startswith('y'):
                    sys.exit(0)

            except KeyboardInterrupt:
                print("Ok ok, quitting")
                sys.exit(0)

            # restore the exit gracefully handler here
            signal.signal(signal.SIGINT, exit_gracefully)

        signal.signal(signal.SIGINT, exit_gracefully)
        while True:
            data = prog.readline()
            if data:
                print(data.decode(errors="ignore"), end='')
            time.sleep(0.1)
