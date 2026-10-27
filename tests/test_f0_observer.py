"""Privacy and evidence boundaries for the read-only F0 serial observer."""
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('observer', Path(__file__).resolve().parents[1] / 'tools/observe_f0.py')
O = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(O)


def state(**changes):
    values = dict(stage='F0', page='test', ready=True, os='windows', test=False,
                  heap=195000, largest=114688, min_heap=189000, ready_ms=700, sent=3, failed=0)
    values.update(changes)
    return values


class ObserverTests(unittest.TestCase):
    def test_prefixed_status_whitelists_fields_and_excludes_private_data(self):
        value = state(peer='private peer', passkey='private code')
        parsed = O.parse_status('I (597) tk: ready\r@tk ' + json.dumps(value))
        self.assertEqual(parsed, state())
        self.assertNotIn('peer', parsed)
        self.assertNotIn('passkey', parsed)

    def test_malformed_or_foreign_fields_cannot_reach_public_output(self):
        for value in [state(stage='F1'), state(os='private peer'), state(heap='private data'),
                      state(ready=1), state(sent=-1), state(page='private name')]:
            self.assertIsNone(O.parse_status('@tk ' + json.dumps(value)))
        for line in ['@tk {', '@tk []', 'unrelated private log']:
            self.assertIsNone(O.parse_status(line))

    def test_simulated_and_disconnected_samples_do_not_prove_connected_memory(self):
        self.assertIsNone(O.summary([state(test=True), state(ready=False)])['connected_heap_min'])
        report = O.summary([state(heap=196000), state(heap=195000), state(heap=1, test=True)])
        self.assertEqual(report['connected_heap_min'], 195000)
        self.assertEqual(report['live_connected_samples'], 2)

    def test_advertising_timer_does_not_prove_full_boot_to_ready(self):
        self.assertIsNone(O.summary([state(ready_ms=701)])['boot_to_ready_ms'])
