#!/usr/bin/env python3
import sys, fileinput

with fileinput.input() as f:
    for line in f:
        raw_hex_line = line.strip().lower().removeprefix('0x')
        raw_bytes = bytes.fromhex(raw_hex_line)
        sys.stdout.buffer.write(raw_bytes + b'\n')
