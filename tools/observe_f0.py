#!/usr/bin/env python3
"""Observe existing F0 firmware; status queries only, no reset/flash/HID commands."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('stage', 'page', 'ready', 'os', 'test', 'heap', 'largest',
          'min_heap', 'ready_ms', 'sent', 'failed')


def parse_status(line):
    """Only return known diagnostic fields; never copy peer/passkey data."""
    marker = line.find('@tk ')
    if marker < 0:
        return None
    try:
        state, _ = json.JSONDecoder().raw_decode(line[marker + 4:])
    except (ValueError, TypeError):
        return None
    if not isinstance(state, dict) or state.get('stage') != 'F0':
        return None
    if any(type(state.get(k)) is not bool for k in ('ready', 'test')):
        return None
    if state.get('page') not in ('menu', 'test') or state.get('os') not in ('mac', 'windows'):
        return None
    for key in ('heap', 'largest', 'min_heap', 'ready_ms', 'sent', 'failed'):
        if type(state.get(key)) is not int or not 0 <= state[key] <= 0xffffffff:
            return None
    return {key: state[key] for key in FIELDS}


def summary(samples):
    # Test mode simulates successful sends and must never count as HID evidence.
    live = [s for s in samples if s['ready'] and not s['test']]
    return {
        'status_samples': len(samples), 'live_connected_samples': len(live),
        'connected_heap_min': min((s['heap'] for s in live), default=None),
        'connected_largest_min': min((s['largest'] for s in live), default=None),
        'boot_to_ready_ms': None,
        'timing_note': 'ready_ms is advertising-to-ready only; serial-open time is not boot time.',
        'physical_hid': 'Requires user confirmation; sent counts alone are insufficient.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True, help='Re-enumerate and identify the Passport before opening.')
    parser.add_argument('--seconds', type=int, default=120, choices=range(5, 601), metavar='5..600')
    args = parser.parse_args()
    import serial  # Activated IDF Python supplies pyserial; pure parsing tests do not need it.

    folder = ROOT / 'private/device'
    folder.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    raw_path = folder / f'f0-{stamp}.log'
    result_path = folder / f'f0-{stamp}.json'
    port = serial.Serial(port=None, baudrate=115200, timeout=0.1, write_timeout=1)
    port.dtr = False
    port.rts = False
    port.port = args.port
    print('Opening the identified port may restart the device. Re-enter the test page if needed.', flush=True)
    samples = []
    pending = b''
    started = time.monotonic()
    query_at = started + 3
    try:
        port.open()
        with raw_path.open('xb') as raw:
            while time.monotonic() - started < args.seconds:
                now = time.monotonic()
                if now >= query_at:
                    port.write(b'>tk.status\n')
                    query_at = now + 2
                chunk = port.read(4096)
                raw.write(chunk)
                pending += chunk
                # ESP USB console can use bare CR, LF, or CRLF, including mid-chunk.
                lines = re.split(br'[\r\n]', pending)
                pending = lines.pop()
                for line in lines:
                    state = parse_status(line.decode('utf-8', errors='replace'))
                    if state is not None:
                        changed = not samples or state != samples[-1]
                        samples.append(state)
                        if changed:
                            print(json.dumps(state), flush=True)
                if len(pending) > 16384:
                    pending = pending[-16384:]
    except KeyboardInterrupt:
        print('Observation stopped.', flush=True)
    finally:
        port.close()
        report = summary(samples)
        result_path.write_text(json.dumps({'summary': report, 'samples': samples}, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
