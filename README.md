LS1 Checksum Correction
=======================
Corrects and verifies 512KiB LS1 ECU ROMs.


```
usage: checksum.py [-h] [-v] [-c OUTPUT] file

Verify checksum of LS1 ROM

positional arguments:
  file                  path to ROM

optional arguments:
  -h, --help            show this help message and exit
  -v, --verify
  -c OUTPUT, --correct OUTPUT
                        Corrects checksum and writes to OUTPUT
```