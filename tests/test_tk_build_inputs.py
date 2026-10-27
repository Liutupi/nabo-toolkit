"""Check derived firmware inputs against existing assets and recorded portable hashes."""
import hashlib
import json
import unittest
from tk_native import ROOT

class FirmwareInputTests(unittest.TestCase):
    def test_existing_atlas_derivatives_and_font_subsets_are_current(self):
        def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
        metadata=json.loads((ROOT/'firmware/assets/placeholders.json').read_text(encoding='utf-8'))
        for name,item in metadata.items():
            self.assertEqual(sha(ROOT/item['source']),item['source_sha256'])
            self.assertEqual(item['frame'],0);self.assertTrue(item['alpha_unchanged'])
            for extension,field in [('rgb565','rgb565_sha256'),('alpha','alpha_sha256')]:
                self.assertEqual(sha(ROOT/f'firmware/assets/placeholder_{name}.{extension}'),item[field])
        fonts=json.loads((ROOT/'firmware/fonts/fonts.json').read_text(encoding='utf-8'))
        needed={c for name in fonts['source_files'] for c in (ROOT/name).read_text(encoding='utf-8') if ord(c)>127}
        self.assertFalse(needed-set(fonts['symbols']), 'Font subsets must cover newly added source text')
        for name,item in fonts['outputs'].items():
            path=ROOT/f'firmware/fonts/{name}.c';self.assertEqual(sha(path),item['sha256'])
            self.assertEqual(path.stat().st_size,item['bytes'])
            self.assertNotIn('D:/',path.read_text(encoding='utf-8'))
