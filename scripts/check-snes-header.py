#!/usr/bin/env python3
"""Validate standard SNES headers without depending on libmagic's database."""
from pathlib import Path
import sys


def valid_header(data):
    shift = 512 if len(data) % 1024 == 512 else 0
    for address in (0x7fc0, 0xffc0, 0x40ffc0):
        offset=address+shift
        if len(data)<offset+64:
            continue
        header=data[offset:offset+64]
        complement=int.from_bytes(header[28:30],'little')
        checksum=int.from_bytes(header[30:32],'little')
        reset=int.from_bytes(header[60:62],'little')
        title=header[:21]
        if (header[21]&0xef) in (0x20,0x21,0x22,0x23,0x25) and reset>=0x8000 and (
                complement^checksum)==0xffff and any(32<=b<127 for b in title):
            return True
    return False


if __name__=='__main__':
    sys.exit(0 if valid_header(Path(sys.argv[1]).read_bytes()) else 1)
