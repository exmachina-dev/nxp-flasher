NXP-flasher
===========

This tool allows to flash NXP chips from command-line.

# Installation and requirements

NXP-flasher requires Python 3+ to run as well as the serial module to run.
To install it, simply run:

```sh
pip3 install pyserial
```

or:

```sh
pip3 install --user pyserial
```

# Usage

To get the list of supported chips:
```sh
python.exe .\nxpprog.py -l
```

To display help and usage, simply type:
```sh
python.exe .\nxpprog.py
```

To use an other programmer, type:
```sh
python.exe .\nxpprog.py -p PROGRAMMER
```

Available programmers are:
- serial
- buspirate

# Notes

Althought it should support every chip specified in nxpchips.py file, it has
only been tested with the LPC1768.

Because this tool is written in Python it should run on every platform,
even if it's been only tested on Windows 10.

# Source code and credits

Based on nxpprog program by Brian Murphy <brian@murphy.dk> released under MIT license.

Original source code can be found at [SourceForge](https://sourceforge.net/projects/nxpprog).

Source code for this fork can be found at [GitHub](https://github.com/exmachina-dev/nxp-flasher).
