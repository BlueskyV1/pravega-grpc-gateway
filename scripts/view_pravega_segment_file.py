#!/usr/bin/env python3

import argparse
import logging
import struct


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        description=
            'Show the events in a Pravega segment as stored in a file on a tier 2. '
            'These files are named like "0.#epoch.0$offset.0".'
    )
    parser.add_argument('--max_events', type=int, default=0, help='Stop after this many events')
    parser.add_argument('--print_size', type=int, default=100, help='Print this many bytes in each event')
    parser.add_argument('file', type=str)
    args = parser.parse_args()

    with open(args.file, 'rb') as f:
        total_records = 0
        total_bytes = 0

        while True:
            try:
                header = f.read(8)
                if not header:
                    break
                num_bytes = struct.unpack('>Q', header)[0]  # 64-bit unsigned integer
                event = f.read(num_bytes)
                total_records += 1
                total_bytes += num_bytes
                logging.info("num_bytes=%d, event=%s..." % (num_bytes, str(event)[0:args.print_size]))
                if 0 < args.max_events <= total_records:
                    break
            except EOFError:
                break

    logging.info('Processed %0.6f MB in %d records.' % (total_bytes / 1e6, total_records))


if __name__ == "__main__":
    main()
