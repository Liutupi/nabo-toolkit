"""Keep the fixed primary glyph subset and its compact CJK fallback traceable."""
import hashlib
import json
import unittest
from tk_native import ROOT


class FontSubsetPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fonts=json.loads((ROOT/'firmware/fonts/fonts.json').read_text(encoding='utf-8'))
        cls.policy_path=ROOT/cls.fonts['subset_policy']
        cls.policy=json.loads(cls.policy_path.read_text(encoding='utf-8'))

    def test_every_source_symbol_is_assigned_to_primary_or_fallback(self):
        fonts=self.fonts
        sources=[p for p in (ROOT/'firmware/main').glob('tk_*.c') if not p.name.startswith('tk_font_')]
        sources += [ROOT/'game-art/toolkit/prototype'/name for name in ('tk_core.js','tk_hid.js')]
        self.assertEqual(set(fonts['source_files']),{p.relative_to(ROOT).as_posix() for p in sources})
        needed={c for name in fonts['source_files'] for c in (ROOT/name).read_text(encoding='utf-8') if ord(c)>127}
        primary=set(fonts['primary_symbols']);fallback=set(fonts['fallback_symbols'])
        self.assertEqual(set(fonts['symbols']),needed,'Source changes require an updated font manifest')
        self.assertFalse(primary&fallback,'A new fallback glyph must not duplicate the fixed primary subset')
        self.assertEqual(fallback,needed-primary)
        self.assertFalse(needed-(primary|fallback),'Every UI symbol needs an actual rendering route')

    def test_every_fallback_symbol_exists_in_the_linked_cjk_coverage(self):
        fallback=set(self.fonts['fallback_symbols']);cjk=set(self.fonts['cjk_symbols'])
        self.assertFalse(fallback-cjk,'Missing glyphs must never silently become square placeholders')
        for char in fallback:
            self.assertTrue(any(a<=ord(char)<=b for a,b in ((0x3000,0x303f),(0x4e00,0x9fff),(0xff00,0xffef))),char)
        for size in (12,16,18):
            source=(ROOT/f'firmware/fonts/tk_font_{size}.c').read_text(encoding='utf-8')
            self.assertIn('.fallback = &tk_font_cjk',source)

    def test_manifest_binds_the_exact_fixed_subset_policy(self):
        self.assertEqual(self.fonts['subset_policy'],'firmware/fonts/subset-symbols.json')
        self.assertEqual(self.policy['format'],'TKFONT_SUBSET1')
        self.assertEqual(hashlib.sha256(self.policy_path.read_bytes()).hexdigest(),self.fonts['subset_policy_sha256'])
        symbols=self.policy['symbols']
        self.assertEqual(symbols,''.join(sorted(set(symbols))))
        self.assertEqual(self.fonts['primary_symbols'],symbols)
