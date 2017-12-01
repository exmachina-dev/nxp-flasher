NXP-flasher
===========

This tool allows to flash NXP chips from command-line.

# Usage

To get the list of supported chips:
```sh
nxpprog.py -l
```

To display help and usage, simply type:
```sh
nxpprog.py
```

# Notes

Althought it should support every chip specified in nxpchips.py file, it
only been tested with the LPC1768.

Because this tool is written in Python it should run on every platform.
Even if it's been only tested on Windows 10.

# Source code

Original source code can be found on [GitHub](https://github.com/exmachina-dev/nxp-flasher)
