#!/usr/bin/env python3
"""Re-record the pure JS reference in a temporary folder and compare every byte."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT/'tests/tk_golden'
recorded = json.loads((GOLD/'verification.json').read_text())
with tempfile.TemporaryDirectory() as folder:
    subprocess.run(['node',str(GOLD/'record_golden.js'),folder],cwd=ROOT,check=True)
    for name, expected in recorded['files'].items():
        actual = (Path(folder)/name).read_bytes()
        assert actual == (GOLD/name).read_bytes(), f'{name}: stale golden reference'
        assert hashlib.sha256(actual).hexdigest() == expected['sha256'], f'{name}: wrong recorded hash'
        assert len(actual) == expected['bytes'], f'{name}: wrong recorded length'
print('JS golden determinism: PASS (not a full JS–C model replay)')
