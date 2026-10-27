"""Synthetic C-backed serial endpoint for Node client integration. Never opens a port."""
import json
import sys
from test_tk_config import ConfigTests
ConfigTests.setUpClass();lib=ConfigTests.lib;lib.tk_mock_reset();host=lib.tk_cfg_host_new();now=0
try:
    for request in sys.stdin:
        line=json.loads(request)['line'];now+=10;lib.tk_cfg_host_line(host,line.encode(),now,True)
        if line=='>tk.cfg.read':
            for _ in range(100):now+=16;lib.tk_cfg_host_tick(host,now,True)
        output=lib.tk_cfg_host_lines(host).decode().splitlines();lib.tk_cfg_host_clear(host)
        print(json.dumps({'lines':output}),flush=True)
finally:lib.tk_cfg_host_free(host);ConfigTests.tearDownClass()
